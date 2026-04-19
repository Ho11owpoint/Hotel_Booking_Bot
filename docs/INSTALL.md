# Installation Manual — Aurora Grand Hotel Chatbot

This guide walks you through installing and running the chatbot on a fresh
machine. Tested on **Windows 10/11** and **macOS 14+** with **Python 3.10
through 3.14**.

---

## 1. Prerequisites

| Requirement | Minimum version | Check                     |
|-------------|-----------------|---------------------------|
| Python      | 3.10            | `python --version`        |
| pip         | 22.0            | `python -m pip --version` |
| A browser   | any modern one  | —                         |

If Python is missing, install from https://www.python.org/downloads/ and make
sure you tick **"Add Python to PATH"** on Windows.

## 2. Get the code

Unzip the submission archive (or clone the repo). You should end up with a
folder containing:

```
Hotel_Booking_Bot/
├── src/
├── tests/
├── docs/
├── requirements.txt
└── README.md
```

Open a terminal *inside* that folder.

## 3. (Recommended) Create a virtual environment

Isolating the project keeps your system Python clean.

**Windows (PowerShell or Git-Bash):**
```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

You should now see `(.venv)` in your shell prompt.

## 4. Install dependencies

```bash
python -m pip install -r requirements.txt
```

This installs **Flask** — the only runtime dependency.

## 5. Run the application

```bash
cd src
python app.py
```

Expected output:

```
 * Serving Flask app 'app'
 * Running on http://127.0.0.1:5000
```

## 6. Open the chat

Open your browser and visit **http://127.0.0.1:5000**.

Type *"book a room"* to start a booking.

## 7. Run the test suite (optional but recommended)

From the project root:

```bash
python -m unittest tests/test_bot.py -v
```

You should see `Ran 15 tests ... OK`.

## 8. Where are the bookings saved?

Confirmed bookings are appended to `src/data/bookings.json`. You can also
inspect them via the debug endpoint while the server is running:

```
GET http://127.0.0.1:5000/bookings
```

To wipe the booking log, simply delete `src/data/bookings.json` (it will be
re-created empty on the next start).

## 9. Troubleshooting

| Symptom                               | Fix                                                   |
|---------------------------------------|-------------------------------------------------------|
| `ModuleNotFoundError: flask`          | You forgot step 4 — run `pip install -r requirements.txt`. |
| Port 5000 already in use              | Another app is using it. Change `port=5000` in `src/app.py` to e.g. `5050`. |
| Bot replies "I didn't catch that"     | Try rephrasing; see [`docs/ARCHITECTURE.md`](ARCHITECTURE.md) for supported patterns. |
| Page looks unstyled                   | Force-refresh (Ctrl+F5) to clear the cached CSS.      |

## 10. Stopping the server

Press **Ctrl+C** in the terminal where the server is running.
