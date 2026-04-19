# Architecture Notes

## 1. High-level component map

```
┌─────────────┐   HTTP/JSON   ┌──────────────┐     ┌───────────────┐
│   Browser   │◀────POST─────▶│    Flask     │─────▶│ HotelBookingBot│
│ chat UI (JS)│               │  (app.py)    │     │  (chatbot.py) │
└─────────────┘               └──────────────┘     └──────┬────────┘
                                                          │
                        ┌─────────────────────────────────┼───────────────┐
                        ▼                                 ▼               ▼
                 ┌─────────────┐                 ┌────────────────┐   ┌──────────────┐
                 │IntentClassif│                 │   Entity       │   │ BookingStore │
                 │  (nlp.py)   │                 │ extractors     │   │ (booking.py) │
                 └─────────────┘                 │   (nlp.py)     │   └──────┬───────┘
                                                 └────────────────┘          │
                                                                             ▼
                                                                     ┌──────────────┐
                                                                     │bookings.json │
                                                                     └──────────────┘
```

## 2. Runtime flow (one user turn)

1. Browser sends `POST /chat  {"message": "..."}`.
2. `app.py` forwards the text to `HotelBookingBot.respond()`.
3. The bot calls `IntentClassifier.classify()` → `(tag, confidence)`.
4. The bot attempts to fill the current dialog slot via the entity
   extractors; it advances the state machine if successful.
5. The bot composes a reply and returns it as JSON.
6. The JS client renders it as a speech bubble in the chat pane.

## 3. Dialog state machine

```
greet ──▶ name ──▶ dates ──▶ guests ──▶ breakfast ──▶ payment ──▶ confirm ──▶ (done)
                                                                                 │
                                                              "no" / "cancel"    │
                                                                  └─loop back─ reset
```

## 4. NLP design choices & trade-offs

### 4.1 Intent classification
We use **bag-of-words + cosine similarity** against the training patterns in
`intents.json`. This is O(N) in the number of patterns (tiny) and needs no
ML framework, but obviously lacks semantic generalisation. For this course
assignment it's the right choice because:

* The vocabulary is closed (hotel booking).
* It's transparent: every prediction is explainable from the training data.
* Zero installation friction for the grader.

Alternatives considered:
| Option     | Pros                    | Why not                               |
|------------|-------------------------|---------------------------------------|
| Rasa       | Production-grade        | Heavy setup; incompatible with Py 3.14|
| Dialogflow | Hosted, free tier       | Requires a Google account + network   |
| spaCy      | Real NER                | Large model download; overkill here   |
| TF-IDF+sklearn | Still light         | One more dependency for no big gain   |

### 4.2 Entity extraction
**Regex + heuristics** for names, dates, guest counts, and payment methods.
For a fixed five-slot booking form this is more robust than a learned model
(which would need hundreds of examples to beat handcrafted patterns).

## 5. Why a module-level bot instance?
`app.py` keeps a single `HotelBookingBot` per process. For a one-user
prototype this is fine and keeps the code readable. To scale to multiple
concurrent sessions we'd:

1. Move the `BookingConversation` into Flask's `session` (cookie-stored)
   or Redis.
2. Instantiate the classifier **once** but the session **per user**.

## 6. Ten-Q/A coverage
The assignment requires the bot to handle *"10 questions and 10 answers"*.
The bot supports the following dialog acts, covering far more than 10 pairs:

| # | User act           | Bot question / response                          |
|---|--------------------|--------------------------------------------------|
| 1 | Greet              | Welcome message                                  |
| 2 | Ask for help       | Usage instructions                               |
| 3 | Start booking      | Ask for name                                     |
| 4 | Provide name       | Ask for dates                                    |
| 5 | Provide dates      | Ask for guest count                              |
| 6 | Provide guests     | Ask about breakfast                              |
| 7 | Breakfast yes/no   | Ask for payment                                  |
| 8 | Provide payment    | Show booking summary                             |
| 9 | Confirm            | Generate booking reference                       |
| 10| Restart / cancel   | Reset dialog                                     |
| 11| Thank you          | You're welcome                                   |
| 12| Goodbye            | Farewell                                         |
| 13| Out-of-scope input | Graceful fallback with hint                      |

## 7. Known limitations

* Single-turn entity pickup only: the bot doesn't re-ask if an entity was
  mis-extracted (the user has to say "restart").
* Date parsing is English-only.
* No real payment processing — the payment method is just recorded.
* Fallback is rule-based; could be replaced by an LLM for more flexible
  small-talk.
