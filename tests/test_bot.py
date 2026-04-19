"""
End-to-end conversation tests for the Aurora Grand Hotel chatbot.

Run from the repo root:
    python -m unittest tests/test_bot.py -v
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

# Make src/ importable when running from the repo root.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from chatbot import HotelBookingBot       # noqa: E402
from nlp import (                         # noqa: E402
    IntentClassifier,
    extract_dates,
    extract_guest_count,
    extract_name,
    extract_payment,
)


class TestEntityExtraction(unittest.TestCase):
    def test_name_from_sentence(self):
        self.assertEqual(extract_name("My name is Jane Doe"), "Jane Doe")
        self.assertEqual(extract_name("I'm John Smith"), "John Smith")
        self.assertEqual(extract_name("call me Max Mustermann"), "Max Mustermann")

    def test_name_bare(self):
        self.assertEqual(extract_name("Egemen Yilmaz"), "Egemen Yilmaz")

    def test_guest_count_digit(self):
        self.assertEqual(extract_guest_count("we are 3 people"), 3)
        self.assertEqual(extract_guest_count("2 guests"), 2)

    def test_guest_count_words(self):
        self.assertEqual(extract_guest_count("two adults"), 2)
        self.assertEqual(extract_guest_count("just me"), 1)
        self.assertEqual(extract_guest_count("a couple"), 2)

    def test_payment_methods(self):
        self.assertEqual(extract_payment("I'll pay by credit card"), "Credit card")
        self.assertEqual(extract_payment("debit please"), "Debit card")
        self.assertEqual(extract_payment("I will pay at the hotel"), "Pay at hotel")

    def test_date_iso(self):
        d1, d2 = extract_dates("from 2026-05-10 to 2026-05-14")
        self.assertEqual(d1.isoformat(), "2026-05-10")
        self.assertEqual(d2.isoformat(), "2026-05-14")

    def test_date_slash(self):
        d1, d2 = extract_dates("10/05/2026 - 14/05/2026")
        self.assertEqual(d1.isoformat(), "2026-05-10")
        self.assertEqual(d2.isoformat(), "2026-05-14")

    def test_date_month_name(self):
        d1, d2 = extract_dates("May 10 to May 14 2026")
        self.assertEqual((d1.month, d1.day), (5, 10))
        self.assertEqual((d2.month, d2.day), (5, 14))


class TestIntentClassifier(unittest.TestCase):
    def setUp(self):
        self.clf = IntentClassifier(ROOT / "src" / "data" / "intents.json")

    def test_greeting(self):
        tag, _ = self.clf.classify("hello there")
        self.assertEqual(tag, "greet")

    def test_book_room(self):
        tag, _ = self.clf.classify("I want to book a room")
        self.assertEqual(tag, "book_room")

    def test_goodbye(self):
        tag, _ = self.clf.classify("goodbye")
        self.assertEqual(tag, "goodbye")

    def test_fallback(self):
        tag, _ = self.clf.classify("pineapple transatlantic dirigible")
        self.assertEqual(tag, "fallback")


class TestFullConversation(unittest.TestCase):
    """Walk the bot through the full 10-turn booking dialog."""

    def test_happy_path(self):
        bot = HotelBookingBot()

        # Turn 1: greet
        r = bot.respond("Hi")
        self.assertIn("full name", r.lower())

        # Turn 2: name
        r = bot.respond("My name is Jane Doe")
        self.assertIn("check-in", r.lower())

        # Turn 3: dates
        r = bot.respond("from 2026-05-10 to 2026-05-14")
        self.assertIn("guests", r.lower())

        # Turn 4: guests
        r = bot.respond("2 guests")
        self.assertIn("breakfast", r.lower())

        # Turn 5: breakfast
        r = bot.respond("yes please")
        self.assertIn("pay", r.lower())

        # Turn 6: payment
        r = bot.respond("credit card")
        self.assertIn("summary", r.lower())

        # Turn 7: confirm
        r = bot.respond("yes confirm")
        self.assertIn("confirmed", r.lower())
        self.assertIn("AGH-", r)   # booking reference

    def test_restart_mid_flow(self):
        bot = HotelBookingBot()
        bot.respond("book a room")
        bot.respond("Jane Doe")
        r = bot.respond("goodbye")
        self.assertIn("thank you", r.lower())
        # Should be back to greet state.
        self.assertEqual(bot.session.current_slot, "greet")

    def test_bare_yes_confirms_booking(self):
        """Regression: a bare 'yes' at the confirm step used to be routed
        to breakfast_yes by the classifier, so the booking never confirmed
        and the bot re-asked indefinitely."""
        bot = HotelBookingBot()
        for msg in ["hi", "Jane Doe", "2026-05-10 to 2026-05-14",
                    "2", "yes", "credit card"]:
            bot.respond(msg)
        self.assertEqual(bot.session.current_slot, "confirm")
        # The critical turn — just "yes", no "please" or "confirm".
        reply = bot.respond("yes")
        self.assertIn("confirmed", reply.lower())
        self.assertIn("AGH-", reply)

    def test_bare_no_restarts_at_confirm(self):
        """Regression: a bare 'no' at the confirm step should reset, not
        get lost in the breakfast_no intent."""
        bot = HotelBookingBot()
        for msg in ["hi", "Jane Doe", "2026-05-10 to 2026-05-14",
                    "2", "yes", "credit card"]:
            bot.respond(msg)
        reply = bot.respond("no")
        self.assertIn("start again", reply.lower())
        self.assertEqual(bot.session.current_slot, "greet")

    def test_out_of_order_info(self):
        """User volunteers name + dates up front — bot should accept both."""
        bot = HotelBookingBot()
        bot.respond("hello")
        r = bot.respond("I'm Alice Wong and I'd like to stay 2026-07-01 to 2026-07-05")
        self.assertEqual(bot.session.booking.name, "Alice Wong")
        self.assertEqual(bot.session.booking.checkin, "2026-07-01")
        self.assertIn("guests", r.lower())


if __name__ == "__main__":
    unittest.main()
