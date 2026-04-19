"""
NLP module for Aurora Grand Hotel booking chatbot.

Handles:
  * Intent classification via TF-IDF-style bag-of-words cosine similarity over
    the training patterns in ``data/intents.json``.
  * Entity extraction (name, dates, guest count, payment method) via a mix of
    regular expressions and lightweight heuristics.

The approach is intentionally lightweight so the project runs on a fresh
Python install without requiring heavy ML frameworks (Rasa / spaCy / etc.),
while still demonstrating the standard intent-and-entity NLP pipeline.
"""

from __future__ import annotations

import json
import math
import re
from collections import Counter
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Optional


# --------------------------------------------------------------------------- #
# Intent classifier                                                           #
# --------------------------------------------------------------------------- #

STOPWORDS = {
    "a", "an", "the", "to", "is", "of", "for", "on", "in", "at", "and",
    "or", "with", "please", "can", "could", "would", "i", "my", "me",
    "we", "our", "you", "your",
}


def _tokenize(text: str) -> list[str]:
    """Lowercase, strip punctuation, drop stopwords."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return [tok for tok in text.split() if tok and tok not in STOPWORDS]


def _cosine(a: Counter, b: Counter) -> float:
    """Cosine similarity between two token Counters."""
    if not a or not b:
        return 0.0
    common = set(a) & set(b)
    dot = sum(a[t] * b[t] for t in common)
    na = math.sqrt(sum(v * v for v in a.values()))
    nb = math.sqrt(sum(v * v for v in b.values()))
    return dot / (na * nb) if na and nb else 0.0


class IntentClassifier:
    """Bag-of-words cosine-similarity intent matcher.

    Trained by loading the patterns from ``intents.json``. For each incoming
    message the classifier returns the intent tag with the highest similarity
    to any of its patterns; if no pattern scores above ``threshold`` we fall
    back to the ``fallback`` intent.
    """

    def __init__(self, intents_path: str | Path, threshold: float = 0.35):
        self.threshold = threshold
        self.intents: dict[str, dict] = {}
        self._pattern_vectors: list[tuple[str, Counter]] = []
        self._load(Path(intents_path))

    def _load(self, path: Path) -> None:
        data = json.loads(path.read_text(encoding="utf-8"))
        for intent in data["intents"]:
            tag = intent["tag"]
            self.intents[tag] = intent
            for pattern in intent["patterns"]:
                self._pattern_vectors.append((tag, Counter(_tokenize(pattern))))

    def classify(self, message: str) -> tuple[str, float]:
        """Return (intent_tag, confidence) for the given user message."""
        query = Counter(_tokenize(message))
        best_tag, best_score = "fallback", 0.0
        for tag, vec in self._pattern_vectors:
            score = _cosine(query, vec)
            if score > best_score:
                best_tag, best_score = tag, score
        if best_score < self.threshold:
            return "fallback", best_score
        return best_tag, best_score

    def response_template(self, tag: str) -> str:
        """Return the first response template for the given intent."""
        return self.intents[tag]["responses"][0]


# --------------------------------------------------------------------------- #
# Entity extraction                                                           #
# --------------------------------------------------------------------------- #

_MONTHS = {
    "jan": 1, "january": 1, "feb": 2, "february": 2, "mar": 3, "march": 3,
    "apr": 4, "april": 4, "may": 5, "jun": 6, "june": 6, "jul": 7, "july": 7,
    "aug": 8, "august": 8, "sep": 9, "sept": 9, "september": 9, "oct": 10,
    "october": 10, "nov": 11, "november": 11, "dec": 12, "december": 12,
}

# Ordered most-specific-first so "couple" wins over "a" on "a couple".
_NUMBER_WORDS: list[tuple[str, int]] = [
    ("one", 1), ("two", 2), ("three", 3), ("four", 4), ("five", 5),
    ("six", 6), ("seven", 7), ("eight", 8), ("nine", 9), ("ten", 10),
    ("couple", 2), ("pair", 2), ("single", 1),
    ("a", 1), ("an", 1),
]


def extract_name(text: str) -> Optional[str]:
    """Pull a plausible full name out of a free-form reply.

    Tries patterns like ``"my name is Jane Doe"`` / ``"I'm John"`` first,
    then falls back to "the first sequence of capitalised words" — which
    handles a bare reply like ``"Egemen Yilmaz"``.
    """
    # Stop at a conjunction / clause boundary so "I'm Alice Wong and I'd
    # like to stay …" yields just "Alice Wong".
    patterns = [
        r"(?:my name is|i am|i'm|this is|call me|it's|name[:\s]+)\s+"
        r"([A-Za-z][A-Za-z .'-]*?)"
        r"(?=\s+(?:and|&|,|but|\.|!|\?|-)\s|\s+(?:i'd|i\s+would|i\s+want|who|that)\b|$)",
    ]
    for pat in patterns:
        m = re.search(pat, text, flags=re.IGNORECASE)
        if m:
            return _clean_name(m.group(1))

    # Fallback: two or more consecutive capitalised tokens.
    m = re.search(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b", text)
    if m:
        return _clean_name(m.group(1))

    # Last-ditch: a single capitalised word on its own line.
    stripped = text.strip()
    if 1 < len(stripped.split()) <= 4 and all(
        p[:1].isalpha() for p in stripped.split()
    ):
        return _clean_name(stripped)
    return None


def _clean_name(raw: str) -> str:
    raw = raw.strip().rstrip(".,!?")
    # Title-case but preserve particles like "de", "van".
    parts = [p if p.lower() in {"de", "van", "von", "der"} else p.capitalize()
             for p in raw.split()]
    return " ".join(parts)


def extract_guest_count(text: str) -> Optional[int]:
    """Pull a guest count from the reply (digits or number-words)."""
    low = text.lower()
    m = re.search(r"\b(\d{1,2})\b", low)
    if m:
        n = int(m.group(1))
        if 1 <= n <= 20:
            return n
    for word, value in _NUMBER_WORDS:
        if re.search(rf"\b{word}\b", low):
            return value
    if "just me" in low or "alone" in low or "myself" in low:
        return 1
    return None


def extract_payment(text: str) -> Optional[str]:
    """Map the reply to one of the supported payment methods."""
    low = text.lower()
    if "credit" in low or "visa" in low or "mastercard" in low or "amex" in low:
        return "Credit card"
    if "debit" in low:
        return "Debit card"
    if "paypal" in low:
        return "PayPal"
    if "cash" in low or "at the hotel" in low or "on arrival" in low or "at hotel" in low:
        return "Pay at hotel"
    return None


def extract_dates(text: str, today: date | None = None) -> Optional[tuple[date, date]]:
    """Extract a (check-in, check-out) pair from a free-form message.

    Recognised forms (non-exhaustive):
      * ``"2026-05-10 to 2026-05-14"``
      * ``"10/05/2026 - 14/05/2026"`` (day-first)
      * ``"May 10 to May 14"`` / ``"10 May to 14 May"``
      * ``"from tomorrow for 3 nights"``
      * ``"next weekend"``
    """
    today = today or date.today()
    low = text.lower()

    # ISO dates.
    iso = re.findall(r"(\d{4}-\d{2}-\d{2})", text)
    if len(iso) >= 2:
        try:
            d1 = datetime.strptime(iso[0], "%Y-%m-%d").date()
            d2 = datetime.strptime(iso[1], "%Y-%m-%d").date()
            if d2 > d1:
                return d1, d2
        except ValueError:
            pass

    # Slash / dash numeric dates, day-first.
    num = re.findall(r"(\d{1,2})[./-](\d{1,2})[./-](\d{2,4})", text)
    if len(num) >= 2:
        parsed = []
        for d, m_, y in num[:2]:
            y_int = int(y) + 2000 if len(y) == 2 else int(y)
            try:
                parsed.append(date(y_int, int(m_), int(d)))
            except ValueError:
                parsed = []
                break
        if len(parsed) == 2 and parsed[1] > parsed[0]:
            return parsed[0], parsed[1]

    # Month-name dates: "may 10 to may 14" or "10 may to 14 may".
    month_dates = _parse_month_name_range(text, today)
    if month_dates:
        return month_dates

    # Relative: "from tomorrow for N nights".
    m = re.search(r"(today|tomorrow|tonight)\b.*?\bfor\s+(\d+)\s+nights?", low)
    if m:
        start = today + timedelta(days=0 if m.group(1) == "today" or m.group(1) == "tonight" else 1)
        return start, start + timedelta(days=int(m.group(2)))

    # "next weekend"
    if "next weekend" in low:
        days_until_sat = (5 - today.weekday()) % 7 or 7
        start = today + timedelta(days=days_until_sat)
        return start, start + timedelta(days=2)

    return None


def _parse_month_name_range(text: str, today: date) -> Optional[tuple[date, date]]:
    """Parse ranges like 'May 10 to May 14' or '10 May to 14 May'."""
    pat1 = re.compile(
        r"\b(" + "|".join(_MONTHS) + r")\s+(\d{1,2})(?:\w{0,2})?\s*(?:to|until|-|–)\s*"
        r"(?:(" + "|".join(_MONTHS) + r")\s+)?(\d{1,2})(?:\w{0,2})?\b",
        flags=re.IGNORECASE,
    )
    m = pat1.search(text)
    if m:
        mon1 = _MONTHS[m.group(1).lower()]
        day1 = int(m.group(2))
        mon2 = _MONTHS[m.group(3).lower()] if m.group(3) else mon1
        day2 = int(m.group(4))
        year = today.year
        try:
            d1 = date(year, mon1, day1)
            d2 = date(year, mon2, day2)
            if d1 < today:
                d1 = date(year + 1, mon1, day1)
                d2 = date(year + 1, mon2, day2)
            if d2 > d1:
                return d1, d2
        except ValueError:
            pass

    pat2 = re.compile(
        r"\b(\d{1,2})(?:\w{0,2})?\s+(" + "|".join(_MONTHS) + r")\s*(?:to|until|-|–)\s*"
        r"(\d{1,2})(?:\w{0,2})?\s+(" + "|".join(_MONTHS) + r")\b",
        flags=re.IGNORECASE,
    )
    m = pat2.search(text)
    if m:
        day1 = int(m.group(1))
        mon1 = _MONTHS[m.group(2).lower()]
        day2 = int(m.group(3))
        mon2 = _MONTHS[m.group(4).lower()]
        year = today.year
        try:
            d1 = date(year, mon1, day1)
            d2 = date(year, mon2, day2)
            if d1 < today:
                d1 = date(year + 1, mon1, day1)
                d2 = date(year + 1, mon2, day2)
            if d2 > d1:
                return d1, d2
        except ValueError:
            pass
    return None
