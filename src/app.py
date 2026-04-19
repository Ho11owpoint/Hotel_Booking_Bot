"""
Flask web server for the Birol Hotel booking chatbot.

Run:
    python app.py

Then open http://127.0.0.1:5000 in your browser.

Endpoints:
    GET  /                  -> landing page (hotel welcome screen)
    GET  /chat              -> chat interface
    POST /chat              -> {"message": "..."} -> {"reply": "...", "slot": "..."}
    POST /reset             -> start a new session
    GET  /api/availability  -> ISO dates that are fully booked
    GET  /bookings          -> confirmed bookings (demo/debug)
"""

from __future__ import annotations

from flask import Flask, jsonify, render_template, request, session

from availability import unavailable_dates
from chatbot import HotelBookingBot

app = Flask(__name__)
app.secret_key = "birol-hotel-demo-secret"  # demo only

# In a production system each session would get its own bot instance stored in
# a server-side cache (Redis, etc.). For a single-user prototype we keep one
# bot per Flask process; the session cookie only tags the user.
_bot = HotelBookingBot()


# --------------------------------------------------------------------------- #
# Pages                                                                       #
# --------------------------------------------------------------------------- #
@app.route("/")
def landing() -> str:
    """Hotel welcome / landing page with the 'book with AI' button."""
    return render_template("landing.html")


@app.route("/chat")
def chat_page() -> str:
    """Render the chat interface, starting from a fresh session."""
    _bot.session.reset()
    session.setdefault("started", True)
    return render_template("index.html", greeting=_bot.greet())


# --------------------------------------------------------------------------- #
# JSON API                                                                     #
# --------------------------------------------------------------------------- #
@app.post("/chat")
def chat():
    """Handle one user turn.

    The response includes ``slot`` so the client can open the calendar
    widget the moment the bot is asking for dates.
    """
    payload = request.get_json(silent=True) or {}
    message = payload.get("message", "")
    reply = _bot.respond(message)
    return jsonify({
        "reply": reply,
        "slot": _bot.session.current_slot,
        "booking": _bot.session.booking.__dict__ if _bot.session.booking else None,
    })


@app.post("/reset")
def reset():
    """Reset conversation state and return the greeting."""
    _bot.session.reset()
    return jsonify({"reply": _bot.greet(), "slot": _bot.session.current_slot})


@app.get("/api/availability")
def api_availability():
    """Return the list of fully-booked ISO dates for the next 12 months."""
    return jsonify({"unavailable": unavailable_dates()})


@app.get("/bookings")
def bookings():
    """Debug endpoint: list of confirmed bookings from the JSON store."""
    return jsonify(_bot.store.all())


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
