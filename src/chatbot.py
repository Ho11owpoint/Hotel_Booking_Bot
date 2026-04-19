"""
Dialog manager: glues NLP + booking state into a single ``respond()`` method.

Design:
  * The classifier tells us *what* the user is trying to do.
  * The booking state tells us *which slot* we still need to fill.
  * ``respond()`` reconciles the two: it prefers filling the next missing slot
    from the message (so the user can volunteer information out of order), but
    also handles transversal intents (greet, help, goodbye, restart).
"""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Optional

from booking import Booking, BookingConversation, BookingStore
from nlp import (
    IntentClassifier,
    extract_dates,
    extract_guest_count,
    extract_name,
    extract_payment,
)


DATA_DIR = Path(__file__).parent / "data"


class HotelBookingBot:
    """Stateful hotel-booking chatbot."""

    HOTEL_NAME = "Birol Hotel"

    def __init__(self) -> None:
        self.classifier = IntentClassifier(DATA_DIR / "intents.json")
        self.store = BookingStore(DATA_DIR / "bookings.json")
        self.session = BookingConversation()

    # --------------------------------------------------------------------- #
    # Public API                                                            #
    # --------------------------------------------------------------------- #

    def greet(self) -> str:
        return (
            f"Hello! Welcome to {self.HOTEL_NAME}. I'm Aria, your booking "
            "assistant. I can reserve a room for you — just say **'book a "
            "room'** to begin, or type **'help'** for more info."
        )

    def respond(self, message: str) -> str:
        """Produce the bot's next reply for the given user message."""
        message = message.strip()
        if not message:
            return "I didn't catch that — could you say it again?"

        intent, confidence = self.classifier.classify(message)

        # Transversal intents handled first, regardless of slot.
        if intent == "goodbye":
            self.session.reset()
            return "Thank you for choosing Birol Hotel. Safe travels!"
        if intent == "help":
            return self.classifier.response_template("help")
        if intent == "thanks":
            return self.classifier.response_template("thanks")

        # ---- Confirm slot handled explicitly ----
        # The classifier would otherwise route a bare "yes" to `breakfast_yes`
        # (that intent lists "yes" as a pattern and appears earlier in the
        # training file), so we use keyword matching here instead of relying
        # on the intent tag.
        if self.session.current_slot == "confirm":
            if self._is_affirmative(message, intent):
                booking_id = self.store.save(self.session.booking)
                summary = (
                    f"Your booking is **confirmed**!\n"
                    f"Reference number: **{booking_id}**\n\n"
                    f"We look forward to welcoming you to {self.HOTEL_NAME} on "
                    f"{self.session.booking.checkin}. "
                    "Anything else I can help with?"
                )
                self.session.reset()
                return summary
            if self._is_negative(message, intent):
                self.session.reset()
                return (
                    "No problem — let's start again. "
                    "May I have your name, please?"
                )
            # Neither yes nor no — nudge them.
            self.session.fallback_count += 1
            if self.session.fallback_count >= 3:
                self.session.reset()
                return (
                    "I'm having trouble understanding. Let's start fresh — "
                    "please say **'book a room'** when you're ready."
                )
            return self._fallback_hint()

        # Kick off a booking if we aren't already in one.
        if self.session.current_slot == "greet":
            if intent in {"greet", "book_room"}:
                self.session.current_slot = "name"
                return (
                    f"Lovely — let's book your stay at {self.HOTEL_NAME}. "
                    "May I have your **full name**, please?"
                )
            # User jumped straight to giving info — try to pick it up.
            if self._try_fill_slot_from_message(message):
                return self._prompt_for_next_slot()
            return self.greet()

        # We're inside a booking flow: try to extract whatever they said.
        filled = self._try_fill_slot_from_message(message)
        if filled:
            self.session.fallback_count = 0
            return self._prompt_for_next_slot()

        # Nothing matched — fall back gracefully.
        self.session.fallback_count += 1
        if self.session.fallback_count >= 3:
            self.session.reset()
            return (
                "I'm having trouble understanding. Let's start fresh — "
                "please say **'book a room'** when you're ready."
            )
        return self._fallback_hint()

    # --------------------------------------------------------------------- #
    # Yes/no helpers                                                        #
    # --------------------------------------------------------------------- #

    _YES_WORDS = (
        "yes", "yeah", "yep", "yup", "sure", "ok", "okay", "correct",
        "confirm", "proceed", "please do", "book it", "go ahead",
        "affirmative", "of course", "absolutely",
    )
    _NO_WORDS = (
        "no", "nope", "nah", "cancel", "stop", "restart", "start over",
        "wrong", "incorrect", "negative",
    )

    def _is_affirmative(self, message: str, intent: str) -> bool:
        """True if the user clearly said yes (any slot-specific context)."""
        if intent == "confirm_yes":
            return True
        low = message.lower().strip().rstrip(".,!?")
        return any(
            low == w or low.startswith(w + " ") or f" {w} " in f" {low} "
            for w in self._YES_WORDS
        )

    def _is_negative(self, message: str, intent: str) -> bool:
        """True if the user clearly said no / cancel."""
        if intent == "confirm_no":
            return True
        low = message.lower().strip().rstrip(".,!?")
        return any(
            low == w or low.startswith(w + " ") or f" {w} " in f" {low} "
            for w in self._NO_WORDS
        )

    # --------------------------------------------------------------------- #
    # Slot filling                                                          #
    # --------------------------------------------------------------------- #

    def _try_fill_slot_from_message(self, message: str) -> bool:
        """Try to pull info for *any* still-missing slot out of ``message``.

        Returns True if we filled at least one slot.
        """
        filled = False
        b = self.session.booking

        if not b.name:
            name = extract_name(message)
            if name:
                b.name = name
                filled = True

        if not (b.checkin and b.checkout):
            dates = extract_dates(message)
            if dates:
                b.checkin = dates[0].isoformat()
                b.checkout = dates[1].isoformat()
                filled = True

        # Only extract a guest count when we're explicitly asking for it —
        # otherwise a stray digit in a date like "2026-05-14" would get
        # interpreted as "14 guests".
        if not b.guests and self.session.current_slot == "guests":
            guests = extract_guest_count(message)
            if guests:
                b.guests = guests
                filled = True

        if b.breakfast is None and self.session.current_slot == "breakfast":
            low = message.lower()
            if any(w in low for w in ("yes", "sure", "yeah", "yep", "please", "include", "with")):
                b.breakfast = True
                filled = True
            elif any(w in low for w in ("no", "nope", "nah", "without", "skip", "room only")):
                b.breakfast = False
                filled = True

        if not b.payment and self.session.current_slot in {"payment", "breakfast"}:
            payment = extract_payment(message)
            if payment:
                b.payment = payment
                filled = True

        return filled

    def _prompt_for_next_slot(self) -> str:
        """Advance the state machine and ask the next question."""
        nxt = self.session.next_missing_slot()
        self.session.current_slot = nxt
        b = self.session.booking

        if nxt == "name":
            return "May I have your **full name**, please?"
        if nxt == "dates":
            return (
                f"Thank you, **{b.name}**! When would you like to stay with "
                "us? Please share your **check-in and check-out dates** "
                "(e.g. *2026-05-10 to 2026-05-14*)."
            )
        if nxt == "guests":
            return (
                f"Got it — {b.checkin} to {b.checkout} ({b.nights()} night"
                f"{'s' if b.nights() != 1 else ''}). "
                "**How many guests** will be staying?"
            )
        if nxt == "breakfast":
            return (
                f"Noted — {b.guests} guest{'s' if b.guests != 1 else ''}. "
                "Would you like to **include breakfast**? (yes / no)"
            )
        if nxt == "payment":
            return (
                "How would you like to pay: **credit card**, **debit card**, "
                "or **pay at the hotel**?"
            )
        if nxt == "confirm":
            return b.summary()
        return "Let me know how I can help further."

    def _fallback_hint(self) -> str:
        """When intent classification fails, hint at the current slot."""
        slot = self.session.current_slot
        hints = {
            "name": "Sorry, I didn't get that. Could you share your full name?",
            "dates": "I couldn't parse the dates. Please try e.g. *2026-05-10 to 2026-05-14*.",
            "guests": "Could you tell me the number of guests as a digit (e.g. *2*)?",
            "breakfast": "Would you like breakfast? Please answer *yes* or *no*.",
            "payment": "Please choose: credit card, debit card, or pay at the hotel.",
            "confirm": "Shall I confirm the booking? Please answer *yes* or *no*.",
        }
        return hints.get(slot, self.classifier.response_template("fallback"))
