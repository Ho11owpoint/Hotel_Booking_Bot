"""
Booking domain logic: the conversation state machine and booking persistence.

The ``BookingConversation`` object walks the user through a fixed sequence of
slots (name → dates → guests → breakfast → payment → confirm). Each turn the
dialog manager decides which slot to fill next based on what is already known.

Bookings are persisted as JSON in ``data/bookings.json`` — deliberately simple
so the project runs with zero external infrastructure.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field, asdict
from datetime import date
from pathlib import Path
from typing import Optional


# Ordered list of slots the bot must fill. The three starred slots are
# *mandatory* per the course specification (name, time period, guests).
SLOTS: tuple[str, ...] = (
    "name",        # *
    "dates",       # *
    "guests",      # *
    "breakfast",
    "payment",
    "confirm",
)


@dataclass
class Booking:
    """A single hotel booking. All fields optional until confirmed."""
    name: Optional[str] = None
    checkin: Optional[str] = None          # ISO yyyy-mm-dd
    checkout: Optional[str] = None
    guests: Optional[int] = None
    breakfast: Optional[bool] = None
    payment: Optional[str] = None
    booking_id: Optional[str] = None
    status: str = "draft"                  # draft | confirmed | cancelled

    def nights(self) -> int:
        if not (self.checkin and self.checkout):
            return 0
        d1 = date.fromisoformat(self.checkin)
        d2 = date.fromisoformat(self.checkout)
        return (d2 - d1).days

    def summary(self) -> str:
        """Human-readable summary used when asking the user to confirm."""
        bf = "included" if self.breakfast else "not included"
        return (
            f"**Booking summary**\n"
            f"- Guest: {self.name}\n"
            f"- Check-in: {self.checkin}\n"
            f"- Check-out: {self.checkout}\n"
            f"- Nights: {self.nights()}\n"
            f"- Guests: {self.guests}\n"
            f"- Breakfast: {bf}\n"
            f"- Payment: {self.payment}\n\n"
            f"Shall I confirm this booking? (yes / no)"
        )


class BookingStore:
    """JSON-file-backed store for confirmed bookings."""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("[]", encoding="utf-8")

    def save(self, booking: Booking) -> str:
        booking.booking_id = f"AGH-{uuid.uuid4().hex[:8].upper()}"
        booking.status = "confirmed"
        data = json.loads(self.path.read_text(encoding="utf-8"))
        data.append(asdict(booking))
        self.path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return booking.booking_id

    def all(self) -> list[dict]:
        return json.loads(self.path.read_text(encoding="utf-8"))


@dataclass
class BookingConversation:
    """Per-session dialog state for one booking."""

    booking: Booking = field(default_factory=Booking)
    # Which slot are we currently trying to fill.
    current_slot: str = "greet"
    # Protect against infinite fallback loops.
    fallback_count: int = 0

    def next_missing_slot(self) -> Optional[str]:
        """Return the next mandatory-then-optional slot still unfilled."""
        b = self.booking
        if not b.name:
            return "name"
        if not (b.checkin and b.checkout):
            return "dates"
        if not b.guests:
            return "guests"
        if b.breakfast is None:
            return "breakfast"
        if not b.payment:
            return "payment"
        return "confirm"

    def reset(self) -> None:
        self.booking = Booking()
        self.current_slot = "greet"
        self.fallback_count = 0
