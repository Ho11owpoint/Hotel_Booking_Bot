# Aurora Grand Hotel — Booking Chatbot

> IU International University of Applied Sciences
> Course: **Project: AI Use Case (CSEMAIPAIUC01)**
> Task 1 — Chatbot for booking a hotel room

A lightweight, dependency-minimal Python chatbot that books hotel rooms
through a short, friendly conversation. Built for the course portfolio and
designed to run on any stock Python install.

---

## 1. Features

* **Mandatory slots** (per spec): guest name, stay period (check-in +
  check-out), number of guests.
* **Optional slots**: breakfast preference, payment method.
* **Natural language input** — bag-of-words intent classifier plus
  regex/heuristic entity extractors (name, dates, guests, payment).
* **Web chat UI** — responsive HTML/CSS/JS frontend served by Flask.
* **Persistent bookings** — confirmed reservations saved as JSON.
* **Unit + end-to-end tests** — 15 tests covering NLP, intent, and dialog.

## 2. Project structure

```
Hotel_Booking_Bot/
├── src/
│   ├── app.py            # Flask web server + HTTP endpoints
│   ├── chatbot.py        # Dialog manager (state machine)
│   ├── nlp.py            # Intent classifier + entity extraction
│   ├── booking.py        # Booking domain model + JSON store
│   ├── data/
│   │   ├── intents.json  # Training patterns & responses
│   │   └── bookings.json # Persistence (created at runtime)
│   ├── templates/
│   │   └── index.html    # Chat UI markup
│   └── static/
│       ├── style.css     # Chat UI styling
│       └── chat.js       # Client-side fetch/render logic
├── tests/
│   └── test_bot.py       # Unit + E2E conversation tests
├── docs/
│   ├── INSTALL.md        # Installation manual
│   ├── ARCHITECTURE.md   # Design notes
│   └── uml_sequence.md   # UML sequence diagram source
├── requirements.txt
└── README.md
```

## 3. Quick start

```bash
# 1. Clone / unzip, then from the project root:
python -m pip install -r requirements.txt

# 2. Start the server
cd src
python app.py

# 3. Open your browser
#    http://127.0.0.1:5000
```

Type *"book a room"* and follow the prompts. See
[`docs/INSTALL.md`](docs/INSTALL.md) for the detailed installation manual.

## 4. Running the tests

```bash
python -m unittest tests/test_bot.py -v
```

All 15 tests should pass in <1 s.

## 5. Example conversation (happy path)

| # | User                              | Bot (summarised)                                |
|---|-----------------------------------|-------------------------------------------------|
| 1 | hi                                | Welcome! Can I have your name?                  |
| 2 | Jane Doe                          | When would you like to stay?                    |
| 3 | 2026-05-10 to 2026-05-14          | Got it — 4 nights. How many guests?             |
| 4 | 2                                 | Would you like breakfast?                       |
| 5 | yes                               | How would you like to pay?                      |
| 6 | credit card                       | **Booking summary** … confirm?                  |
| 7 | yes confirm                       | Confirmed! Reference **AGH-XXXXXXXX**.          |

That is 7 questions / 7 answers for the happy path; error and restart
branches bring the total coverage above the 10/10 minimum required by the
assignment.

## 6. Technology stack

| Component          | Choice             | Why                                                        |
|--------------------|--------------------|------------------------------------------------------------|
| Language           | Python 3.10+       | Ubiquitous, works on the tutor's machine out of the box.   |
| Web framework      | Flask 3            | Smallest possible footprint for a web chat demo.           |
| NLP — intents      | Bag-of-words cosine| Transparent, zero extra dependencies; easy to explain.     |
| NLP — entities     | Regex + heuristics | Robust for the small closed domain; deterministic.         |
| Persistence        | JSON file          | No DB server needed — grader can inspect it directly.      |
| Frontend           | Vanilla HTML/CSS/JS| No build tool — open & read.                               |

Full rationale and trade-offs versus Rasa / Dialogflow are documented in
[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## 7. Submission layout (PebblePad)

The three phase subdirectories mirror the required ZIP structure from the
assignment brief:

```
AIUseCase_Hotel_P1/   # Phase 1 — Concept PDF + UML diagram
AIUseCase_Hotel_P2/   # Phase 2 — Development PDF (~10 slides)
AIUseCase_Hotel_P3/   # Phase 3 — Abstract PDF + final product source
```

## 8. License

This project is submitted as academic course work and is provided as-is for
evaluation purposes.
