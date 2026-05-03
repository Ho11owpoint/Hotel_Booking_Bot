"""
Build Phase 1 (Conception) PDF for the Birol Hotel chatbot.
Course: IU CSEMAIPAIUC01 - Project: AI Use Case (Task 1, Hotel booking).

Follows the lecture-prescribed structure:
  * Value-proposition template (Lec 01)
  * MVS / MVP definition (Lec 01)
  * Frameworks / tools comparison + trade-offs (Lec 01)
  * UML use-case diagram + sequence + state + component diagrams (Lec 02)
  * Workplan, AI ethics and sustainability notes (Lec 01)

Output:
  AIUseCase_Hotel_P1/Birol-Egemen_10254279_AIUseCase_Hotel_Submission_Concept.pdf
"""

from __future__ import annotations
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate,
    Spacer, Table, TableStyle,
)

# --------------------------------------------------------------------------- #
# Paths                                                                       #
# --------------------------------------------------------------------------- #
ROOT = Path(__file__).parent.resolve()
OUT_DIR = ROOT / "AIUseCase_Hotel_P1"
FIG_DIR = OUT_DIR / "figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)
FIG_DIR.mkdir(parents=True, exist_ok=True)

OUT_PATH = OUT_DIR / "Birol-Egemen_10254279_AIUseCase_Hotel_Submission_Concept.pdf"
# Old (placeholder) PDF that's now superseded — clean it up if it exists.
_OLD_PDF = OUT_DIR / "Birol-Egemen_12345678_AIUseCase_Hotel_Submission_Concept.pdf"
if _OLD_PDF.exists():
    _OLD_PDF.unlink()

# --------------------------------------------------------------------------- #
# Visual identity                                                              #
# --------------------------------------------------------------------------- #
INK         = "#1f2430"
INK_SOFT    = "#3a4154"
ACCENT      = "#5be1e6"   # IU teal
ACCENT_DARK = "#1ea7af"
BRASS       = "#9a7b4f"
BRASS_DARK  = "#7a5f3b"
CREAM       = "#f5f1ea"
PAPER       = "#ffffff"

# --------------------------------------------------------------------------- #
# Diagrams (matplotlib)                                                       #
# --------------------------------------------------------------------------- #

def _box(ax, xy, w, h, text, fc="#ffffff", ec=INK, tc=INK,
         fs=8.5, bold=False, radius=0.10):
    """Rounded rectangle with centred text."""
    x, y = xy
    box = mpatches.FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0.02,rounding_size={radius}",
        linewidth=1.1, facecolor=fc, edgecolor=ec,
    )
    ax.add_patch(box)
    weight = "bold" if bold else "normal"
    ax.text(x + w / 2, y + h / 2, text,
            ha="center", va="center",
            fontsize=fs, color=tc, fontweight=weight, wrap=True)


def _ellipse(ax, xy, w, h, text, fc="#fff3df", ec=BRASS_DARK, fs=8):
    e = mpatches.Ellipse(xy, w, h, facecolor=fc, edgecolor=ec, linewidth=1)
    ax.add_patch(e)
    ax.text(xy[0], xy[1], text, ha="center", va="center", fontsize=fs)


def _arrow(ax, p1, p2, label=None, color=INK, ls="-", lw=1.0, fs=7.5):
    ax.annotate(
        "", xy=p2, xytext=p1,
        arrowprops=dict(arrowstyle="->", color=color, lw=lw,
                        linestyle=ls, shrinkA=4, shrinkB=4),
    )
    if label:
        mx, my = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2
        ax.text(mx, my, label, fontsize=fs, color=color,
                ha="center", va="center",
                bbox=dict(boxstyle="round,pad=0.18", facecolor="white",
                          edgecolor="none", alpha=0.9))


# --- 1. Use case diagram ---------------------------------------------------- #
def make_use_case(out: Path) -> None:
    fig, ax = plt.subplots(figsize=(11.0, 7.6))
    ax.set_xlim(-0.5, 11.5); ax.set_ylim(0.0, 8.2)
    ax.set_aspect("equal"); ax.axis("off")

    # System boundary
    sys = mpatches.FancyBboxPatch(
        (2.4, 0.8), 6.8, 6.6,
        boxstyle="round,pad=0.05,rounding_size=0.18",
        linewidth=1.4, fill=False, edgecolor=INK)
    ax.add_patch(sys)
    ax.text(5.8, 7.05, "Birol Hotel Booking Chatbot",
            ha="center", fontsize=12, fontweight="bold")

    use_cases = [
        # (x, y, label, group_color)
        (3.6, 6.5, "Greet & guide\nguest",          "#fff3df"),
        (5.8, 6.5, "Answer concierge\nQ & A",       "#fff3df"),
        (8.0, 6.5, "Refuse off-topic\n(soft-fall)", "#fff3df"),

        (3.6, 5.4, "Book a room",                   "#e6f7f8"),
        (5.8, 5.4, "Select dates\n(calendar widget)","#e6f7f8"),
        (8.0, 5.4, "Select room type\n(quick chips)","#e6f7f8"),

        (3.6, 4.3, "Process payment",               "#e6f7f8"),
        (5.8, 4.3, "Confirm & save\nbooking",       "#e6f7f8"),
        (8.0, 4.3, "View own receipt",              "#e6f7f8"),

        (3.6, 3.2, "Find booking by\nreference",    "#fff3df"),
        (5.8, 3.2, "Sign in to admin",              "#f7e6f0"),
        (8.0, 3.2, "View admin\ndashboard",         "#f7e6f0"),

        (4.7, 2.1, "View occupancy\ncalendar (CEO)","#f7e6f0"),
        (6.9, 2.1, "List all bookings\n(CEO)",      "#f7e6f0"),
    ]
    for x, y, t, c in use_cases:
        _ellipse(ax, (x, y), 1.85, 0.7, t, fc=c, fs=7.2)

    # Actors
    # Guest (primary)
    ax.add_patch(mpatches.Circle((1.0, 5.4), 0.18, fill=True, facecolor="white", edgecolor=INK, lw=1.2))
    ax.plot([1.0, 1.0], [5.22, 4.65], color=INK, lw=1.2)
    ax.plot([1.0, 0.75], [4.85, 4.55], color=INK, lw=1.0)
    ax.plot([1.0, 1.25], [4.85, 4.55], color=INK, lw=1.0)
    ax.plot([1.0, 0.7], [4.65, 4.20], color=INK, lw=1.2)
    ax.plot([1.0, 1.3], [4.65, 4.20], color=INK, lw=1.2)
    ax.text(1.0, 3.95, "Guest", ha="center", fontsize=10, fontweight="bold")
    ax.text(1.0, 3.7, "(primary)", ha="center", fontsize=7.5, style="italic")

    # CEO (primary)
    ax.add_patch(mpatches.Circle((1.0, 2.4), 0.18, fill=True, facecolor="white", edgecolor=INK, lw=1.2))
    ax.plot([1.0, 1.0], [2.22, 1.65], color=INK, lw=1.2)
    ax.plot([1.0, 0.75], [1.85, 1.55], color=INK, lw=1.0)
    ax.plot([1.0, 1.25], [1.85, 1.55], color=INK, lw=1.0)
    ax.plot([1.0, 0.7], [1.65, 1.20], color=INK, lw=1.2)
    ax.plot([1.0, 1.3], [1.65, 1.20], color=INK, lw=1.2)
    ax.text(1.0, 0.95, "CEO / Staff", ha="center", fontsize=10, fontweight="bold")
    ax.text(1.0, 0.7, "(primary)", ha="center", fontsize=7.5, style="italic")

    # Browser storage (secondary)
    _box(ax, (10.0, 4.85), 1.2, 0.85, "Browser\nstorage",
         fc="#eef2f7", ec=INK, fs=8, bold=True)
    ax.text(10.6, 4.55, "(secondary)", ha="center", fontsize=7.5, style="italic")

    # Guest associations
    for tx, ty in [(3.6, 6.5), (3.6, 5.4), (3.6, 4.3), (3.6, 3.2)]:
        _arrow(ax, (1.18, 5.4), (tx - 0.92, ty), color=INK, lw=0.8)
    # CEO associations
    for tx, ty in [(5.8, 3.2), (8.0, 3.2), (4.7, 2.1), (6.9, 2.1)]:
        _arrow(ax, (1.18, 2.4), (tx - 0.92, ty), color=INK, lw=0.8)

    # localStorage associations
    _arrow(ax, (10.0, 5.0), (8.95, 4.3), color=INK, lw=0.8)
    _arrow(ax, (10.0, 5.5), (8.95, 5.4), color=INK, lw=0.8)

    # «include» relationships
    _arrow(ax, (3.95, 5.05), (5.0, 4.65), label="«include»", ls="--", color=ACCENT_DARK)
    _arrow(ax, (4.0, 5.0), (7.4, 4.65),  label="«include»", ls="--", color=ACCENT_DARK)
    _arrow(ax, (4.0, 4.75), (4.0, 4.65), label="",          ls="--", color=ACCENT_DARK)
    # «extend»
    _arrow(ax, (4.7, 3.55), (4.4, 3.95), label="«extend»\n(card only)", ls="--", color=BRASS)

    # (caption rendered separately by reportlab - no in-figure duplicate)
    fig.tight_layout()
    fig.savefig(out, dpi=210, bbox_inches="tight", facecolor=PAPER)
    plt.close(fig)


# --- 2. Sequence diagram ---------------------------------------------------- #
def make_sequence(out: Path) -> None:
    fig, ax = plt.subplots(figsize=(11.4, 8.2))
    ax.set_xlim(0, 12); ax.set_ylim(0, 11.5)
    ax.axis("off")

    actors = [
        ("Guest",          0.9),
        ("Web UI",         2.6),
        ("Aria Bot\nrespond()", 4.4),
        ("Intent\nClassifier", 6.4),
        ("Entity\nExtractors", 8.3),
        ("Booking\nStore",     10.4),
    ]
    for name, x in actors:
        _box(ax, (x - 0.7, 10.6), 1.4, 0.6, name,
             fc=BRASS, tc="white", bold=True, fs=8.2)
        ax.plot([x, x], [0.4, 10.6], color="#666", lw=0.5, ls="--")

    # Helper to position arrows by actor index
    xs = {n: x for n, x in actors}
    def msg(a, b, text, y, ls="-", lw=1.0, color=INK_SOFT):
        _arrow(ax, (xs[a], y), (xs[b], y), text, color=color, ls=ls, lw=lw, fs=7)

    # Greeting / chips
    msg("Guest", "Web UI", "open page", 10.1)
    msg("Web UI", "Aria Bot\nrespond()", "greet()", 9.85)
    msg("Aria Bot\nrespond()", "Web UI",
        "{reply, actions: [Book / Avail / Places / Help]}", 9.6, ls="--")
    msg("Web UI", "Guest", "render bubble + chips", 9.35, ls="--")

    # Tap "Book a room"
    msg("Guest", "Web UI", "tap chip 'Book a room'", 8.95)
    msg("Web UI", "Aria Bot\nrespond()", "respond('book a room')", 8.7)
    msg("Aria Bot\nrespond()", "Intent\nClassifier", "classify(...)", 8.45)
    msg("Intent\nClassifier", "Aria Bot\nrespond()", "(book_room, 0.9)", 8.2, ls="--")
    msg("Aria Bot\nrespond()", "Web UI", "ask: full name?", 7.95, ls="--")

    # Name → Dates (calendar)
    msg("Guest", "Web UI", "type 'Egemen Birol'", 7.55)
    msg("Web UI", "Aria Bot\nrespond()", "respond(...)", 7.3)
    msg("Aria Bot\nrespond()", "Entity\nExtractors", "extract_name()", 7.05)
    msg("Entity\nExtractors", "Aria Bot\nrespond()", "'Egemen Birol'", 6.8, ls="--")
    msg("Aria Bot\nrespond()", "Web UI", "slot=dates → ask range", 6.55, ls="--")
    msg("Web UI", "Guest", "open calendar widget", 6.30, ls="--")

    # Calendar selection → Dates fill
    msg("Guest", "Web UI", "pick range  +  confirm", 5.95)
    msg("Web UI", "Aria Bot\nrespond()", "respond('2026-05-10 to 2026-05-14')", 5.7)
    msg("Aria Bot\nrespond()", "Web UI", "slot=room_type → 4 chips", 5.45, ls="--")

    # Room type
    msg("Guest", "Web UI", "tap 'Deluxe Room'", 5.05)
    msg("Web UI", "Aria Bot\nrespond()", "respond('Deluxe Room')", 4.80)
    msg("Aria Bot\nrespond()", "Web UI", "slot=guests", 4.55, ls="--")

    # Guests + breakfast
    msg("Guest", "Web UI", "type '2'", 4.20)
    msg("Web UI", "Aria Bot\nrespond()", "respond('2')", 3.95)
    msg("Aria Bot\nrespond()", "Web UI",
        "slot=breakfast (+€10/guest/night)", 3.70, ls="--")

    msg("Guest", "Web UI", "tap 'Yes, include breakfast'", 3.35)
    msg("Web UI", "Aria Bot\nrespond()", "respond('yes')", 3.10)
    msg("Aria Bot\nrespond()", "Web UI",
        "slot=payment", 2.85, ls="--")

    # Payment → card form
    msg("Guest", "Web UI", "tap 'Credit card'", 2.50)
    msg("Web UI", "Aria Bot\nrespond()", "respond('credit card')", 2.25)
    msg("Aria Bot\nrespond()", "Web UI",
        "slot=payment_card → render card form", 2.00, ls="--",
        color=BRASS_DARK, lw=1.3)

    msg("Guest", "Web UI", "tap 'Pay €800'", 1.65)
    msg("Web UI", "Aria Bot\nrespond()", "respond('pay')", 1.40)
    msg("Aria Bot\nrespond()", "Web UI",
        "slot=confirm → show summary", 1.15, ls="--")

    # Confirm → save
    msg("Guest", "Web UI", "tap 'yes'", 0.85)
    msg("Web UI", "Aria Bot\nrespond()", "respond('yes')", 0.65)
    msg("Aria Bot\nrespond()", "Booking\nStore", "save(booking)", 0.50,
        color=ACCENT_DARK, lw=1.2)
    msg("Booking\nStore", "Aria Bot\nrespond()", "BH-XXXXXXXX", 0.30, ls="--",
        color=ACCENT_DARK)

    # (caption rendered separately by reportlab - no in-figure duplicate)
    fig.tight_layout()
    fig.savefig(out, dpi=210, bbox_inches="tight", facecolor=PAPER)
    plt.close(fig)


# --- 3. State machine diagram ----------------------------------------------- #
def make_state(out: Path) -> None:
    fig, ax = plt.subplots(figsize=(11.4, 5.2))
    ax.set_xlim(0, 12); ax.set_ylim(0, 5.4)
    ax.set_aspect("equal"); ax.axis("off")

    states = [
        ("greet",        0.6, 3.0),
        ("name",         2.0, 3.0),
        ("dates",        3.4, 3.0),
        ("room_type",    4.9, 3.0),
        ("guests",       6.5, 3.0),
        ("breakfast",    8.0, 3.0),
        ("payment",      9.5, 3.0),
        ("payment_card", 9.5, 1.4),
        ("confirm",      11.0, 3.0),
    ]
    is_mandatory = {"name", "dates", "guests"}
    for name, x, y in states:
        fc = BRASS if name in is_mandatory else "white"
        tc = "white" if name in is_mandatory else INK
        _box(ax, (x - 0.55, y - 0.30), 1.10, 0.60, name,
             fc=fc, tc=tc, bold=True, fs=8.5)

    # Start dot
    ax.plot(0.10, 3.00, "o", markersize=12, color=INK)
    _arrow(ax, (0.13, 3.0), (0.05 + 0.6 - 0.55, 3.0), lw=1.1)

    # Forward arrows along the main line
    main = ["greet", "name", "dates", "room_type",
            "guests", "breakfast", "payment"]
    pos = {n: (x, y) for (n, x, y) in states}
    for a, b in zip(main, main[1:]):
        x1 = pos[a][0] + 0.55; x2 = pos[b][0] - 0.55
        _arrow(ax, (x1, 3.0), (x2, 3.0))

    # payment → confirm (pay-at-hotel)
    _arrow(ax, (10.05, 3.05), (10.45, 3.05), label="hotel pay", fs=7)

    # payment → payment_card (credit/debit)
    _arrow(ax, (9.5, 2.7), (9.5, 1.7), label="card", fs=7, color=BRASS_DARK, lw=1.3)
    # payment_card → confirm
    _arrow(ax, (9.85, 1.5), (10.95, 2.7),
           label="Pay click", fs=7, color=BRASS_DARK, lw=1.3)

    # End state
    ax.plot(11.85, 3.0, "o", markersize=14,
            markerfacecolor="white", markeredgecolor=INK, markeredgewidth=1.6)
    ax.plot(11.85, 3.0, "o", markersize=7, color=INK)
    _arrow(ax, (11.55, 3.0), (11.78, 3.0), label="confirm", fs=7)

    # Restart loop (confirm -> name)
    _arrow(ax, (11.0, 2.7), (2.0, 2.0), color="#aa3344", lw=1.2,
           label="cancel / restart", fs=7)
    _arrow(ax, (2.0, 2.0), (2.0, 2.7), color="#aa3344", lw=1.2)

    # Concierge transversal (any → answer → return)
    ax.text(6.0, 4.7,
            "Concierge intents (places to visit, wifi, parking, …) are answered transversally and the bot returns to the current slot.",
            ha="center", fontsize=8, style="italic", color=ACCENT_DARK)
    # Show the loop arrow
    rect = mpatches.FancyBboxPatch(
        (2.5, 4.05), 7.5, 0.45,
        boxstyle="round,pad=0.04,rounding_size=0.10",
        linewidth=0, facecolor="#e6f7f8", edgecolor="none")
    ax.add_patch(rect)
    ax.text(6.25, 4.27, "Concierge Q&A (greet | name | dates | room_type | guests | breakfast | payment | payment_card | confirm)",
            ha="center", fontsize=7.5, color=INK)

    # Legend
    ax.text(0.6, 0.5,
            "● Brass   = mandatory slots (name, dates, guests, per assignment spec)        "
            "● White  = optional / configuration slots         "
            "● Red    = restart edge",
            fontsize=8, color=INK_SOFT)

    # (caption rendered separately by reportlab - no in-figure duplicate)
    fig.tight_layout()
    fig.savefig(out, dpi=210, bbox_inches="tight", facecolor=PAPER)
    plt.close(fig)


# --- 4. Component / deployment diagram -------------------------------------- #
def make_component(out: Path) -> None:
    fig, ax = plt.subplots(figsize=(11.0, 6.4))
    ax.set_xlim(0, 11); ax.set_ylim(0, 6.4)
    ax.set_aspect("equal"); ax.axis("off")

    # No in-figure caption: reportlab adds the caption below the image,
    # avoiding duplication with the other figures.

    # Edge servers / GitHub
    _box(ax, (0.4, 4.4), 2.4, 0.8, "GitHub repository\n(main branch · /docs)",
         fc="#fbf8f2", bold=True, fs=8.2)
    _arrow(ax, (2.8, 4.8), (3.45, 4.8), label="git push  →  CI deploy")
    _box(ax, (3.45, 4.4), 2.4, 0.8, "GitHub Pages\n(CDN · HTTPS)",
         fc="#fff3df", bold=True, fs=8.2)
    _arrow(ax, (5.85, 4.8), (6.5, 4.8), label="HTTP")

    # Web container
    web = mpatches.FancyBboxPatch(
        (6.5, 0.8), 4.2, 4.6,
        boxstyle="round,pad=0.05,rounding_size=0.16",
        linewidth=1.3, fill=False, edgecolor=INK)
    ax.add_patch(web)
    ax.text(8.6, 5.20, "Browser  /  WKWebView", ha="center",
            fontsize=10, fontweight="bold")

    _box(ax, (6.7, 4.20), 1.9, 0.55, "index.html\nlanding",         fs=7.5)
    _box(ax, (8.65, 4.20), 1.9, 0.55, "chat.html",                   fs=7.5)
    _box(ax, (6.7, 3.55), 1.9, 0.55, "booking.html",                fs=7.5)
    _box(ax, (8.65, 3.55), 1.9, 0.55, "admin.html",                 fs=7.5)
    _box(ax, (7.7, 2.90), 1.9, 0.55, "find.html",                   fs=7.5)

    _box(ax, (6.7, 2.10), 1.9, 0.55, "bot.js (NLP)",                 fc="#fff3df", bold=True, fs=7.5)
    _box(ax, (8.65, 2.10), 1.9, 0.55, "chat.js / admin.js / find.js", fc="#fff3df", bold=True, fs=7.5)
    _box(ax, (6.7, 1.45), 1.9, 0.55, "intents.json\n(14 intents)",  fc="#eef2f7", fs=7.5)
    _box(ax, (8.65, 1.45), 1.9, 0.55, "stars / glass\nCSS",          fc="#eef2f7", fs=7.5)

    # Storage
    _box(ax, (7.2, 0.85), 1.2, 0.45, "localStorage", fc="#e6f7f8", fs=7.2)
    _box(ax, (8.5, 0.85), 1.4, 0.45, "sessionStorage", fc="#e6f7f8", fs=7.2)

    # iOS shell
    _box(ax, (0.4, 1.6), 2.4, 1.4, "iOS app  (SwiftUI)\nWKWebView wrapper\n+ splash + offline retry",
         fc="#eef2f7", bold=True, fs=8)
    _arrow(ax, (2.8, 2.3), (6.5, 2.3), label="loads same URL")

    # Guest / CEO
    ax.add_patch(mpatches.Circle((1.2, 3.6), 0.18, fill=True, facecolor="white", edgecolor=INK, lw=1))
    ax.text(1.2, 3.3, "User", ha="center", fontsize=9, fontweight="bold")
    _arrow(ax, (1.4, 3.6), (6.5, 3.6))

    fig.tight_layout()
    fig.savefig(out, dpi=210, bbox_inches="tight", facecolor=PAPER)
    plt.close(fig)


# --- 5. Workflow diagram (chatbot dev pipeline) ----------------------------- #
def make_workflow(out: Path) -> None:
    fig, ax = plt.subplots(figsize=(11.2, 3.2))
    ax.set_xlim(0, 12); ax.set_ylim(0, 3.2)
    ax.set_aspect("equal"); ax.axis("off")

    steps = [
        ("Define\nscope",       0.5),
        ("Intents +\nentities", 2.3),
        ("Training\ndata",      4.1),
        ("Conversation\nflow",  5.9),
        ("Train /\ntest",       7.7),
        ("Iterate &\nrefine",   9.5),
        ("Deploy",              11.3),
    ]
    for label, x in steps:
        _box(ax, (x - 0.65, 1.6), 1.30, 0.85, label,
             fc=ACCENT, tc=INK, bold=True, fs=8)
    for (a, ax_x), (b, bx_x) in zip(steps, steps[1:]):
        _arrow(ax, (ax_x + 0.65, 2.0), (bx_x - 0.65, 2.0))

    # Detail strip
    details = [
        "domain.json\nintents.json",
        "14 intents,\n100+ patterns",
        "patterns +\nresponses",
        "slot machine,\nchips",
        "JS unit +\nE2E tests",
        "fix bugs,\ntune patterns",
        "GitHub Pages\nWKWebView",
    ]
    for (label, x), d in zip(steps, details):
        ax.text(x, 0.85, d, ha="center", va="center",
                fontsize=7.2, color=INK_SOFT, style="italic")

    # (caption is rendered by reportlab below the image; no duplicate here)
    fig.tight_layout()
    fig.savefig(out, dpi=210, bbox_inches="tight", facecolor=PAPER)
    plt.close(fig)


# --------------------------------------------------------------------------- #
# PDF assembly                                                                #
# --------------------------------------------------------------------------- #

def build_pdf(figs: dict[str, Path]) -> None:
    styles = getSampleStyleSheet()

    h1 = ParagraphStyle("h1", parent=styles["Title"],
                        fontName="Helvetica-Bold", fontSize=18,
                        textColor=colors.HexColor(INK),
                        spaceAfter=8, alignment=TA_LEFT)
    meta = ParagraphStyle("meta", parent=styles["Normal"],
                          fontName="Helvetica", fontSize=9.5,
                          textColor=colors.HexColor(BRASS_DARK),
                          spaceAfter=10)
    h2 = ParagraphStyle("h2", parent=styles["Heading2"],
                        fontName="Helvetica-Bold", fontSize=12,
                        textColor=colors.HexColor(ACCENT_DARK),
                        spaceBefore=8, spaceAfter=5)
    h3 = ParagraphStyle("h3", parent=styles["Heading3"],
                        fontName="Helvetica-Bold", fontSize=10,
                        textColor=colors.HexColor(INK),
                        spaceBefore=6, spaceAfter=3)
    body = ParagraphStyle("body", parent=styles["BodyText"],
                          fontName="Helvetica", fontSize=10,
                          leading=13, alignment=TA_JUSTIFY,
                          spaceAfter=5)
    bullet = ParagraphStyle("bullet", parent=body,
                            leftIndent=14, bulletIndent=4)
    caption = ParagraphStyle("caption", parent=body,
                             fontName="Helvetica-Oblique", fontSize=8.5,
                             textColor=colors.HexColor("#666"),
                             alignment=TA_CENTER, spaceAfter=10)
    valuep = ParagraphStyle("valuep", parent=body,
                            fontName="Helvetica", fontSize=10.5,
                            leading=15, alignment=TA_LEFT,
                            backColor=colors.HexColor("#f4faff"),
                            leftIndent=14, rightIndent=14,
                            borderPadding=8, spaceAfter=8)

    doc = SimpleDocTemplate(
        str(OUT_PATH), pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm,
        topMargin=2 * cm, bottomMargin=2 * cm,
        title="Phase 1: Conception, Hotel Booking Chatbot",
        author="Egemen Birol",
    )
    story = []

    # ------------------- Cover ------------------- #
    story.append(Paragraph("Phase 1: Conception", h1))
    story.append(Paragraph(
        "Hotel Booking Chatbot for <b>Birol Hotel</b><br/>"
        "IU International University of Applied Sciences<br/>"
        "Course: Project: AI Use Case (CSEMAIPAIUC01), Task 1<br/>"
        "Student: <b>Birol, Egemen</b>, Matriculation 10254279",
        meta))

    # ------------------- Value proposition ------------------- #
    story.append(Paragraph("1. Value proposition", h2))
    story.append(Paragraph(
        "Using the value-proposition canvas from Lecture 01:",
        body))
    story.append(Paragraph(
        "<b>For</b> leisure and business travellers who want to book a hotel "
        "room quickly on their phone,<br/>"
        "<b>Dissatisfied with</b> long multi-step web forms that require "
        "account creation and feel clumsy on a small screen,<br/>"
        "<b>Due to</b> the lack of a single channel that handles the booking "
        "and answers basic questions about the hotel and the city,<br/>"
        "<b>Birol Hotel</b> offers <b>Aria</b>, a chat-based booking assistant,<br/>"
        "<b>That provides</b> a guided conversation, an instant booking reference, "
        "a clear total price, an in-chat card form, a personal receipt page, an "
        "admin dashboard for the hotel, and a 24/7 service that does not need "
        "an account.",
        valuep))

    # ------------------- Aims, MVS, MVP ------------------- #
    story.append(Paragraph("2. Aims, target audience and MVP scope", h2))
    story.append(Paragraph(
        "<b>Aims.</b> The main aim of the chatbot is to collect the information "
        "needed to make a hotel reservation through a short conversation. The "
        "assignment requires three mandatory fields: name, time period, and "
        "number of guests. Payment and breakfast are added as optional extensions. "
        "A second aim is to answer simple questions about the hotel and about "
        "Istanbul, and to give the hotel staff a small admin view of the bookings.",
        body))
    story.append(Paragraph(
        "<b>Minimum Viable Segment (MVS).</b> English-speaking leisure and "
        "business travellers, most of them on a phone. They can be reached "
        "through one channel: a web page (also embedded in a small iOS app).",
        body))
    story.append(Paragraph(
        "<b>Minimum Viable Product (MVP).</b> A static web app with a guided "
        "booking dialogue covering eight slots (name, dates, room type, guests, "
        "breakfast, payment, payment_card, confirm), 16 concierge Q&amp;A "
        "intents, a fallback for unrelated questions, a calendar widget that "
        "shows which dates are full, an in-chat card form, a personal receipt "
        "page, and a password-protected admin page for the hotel.",
        body))

    # ------------------- Why this design ------------------- #
    story.append(Paragraph("3. Structure and process rationale", h2))
    story.append(Paragraph(
        "The dialogue is built as a <b>slot-filling state machine</b> rather "
        "than a free-form language model. The booking domain is small and the "
        "set of fields is fixed, so a simple state machine fits well. It is "
        "also easier to read and grade: the whole dialogue graph is visible in "
        "the source code, and there is no risk of the model inventing a wrong "
        "reservation.",
        body))
    story.append(Paragraph(
        "The system is built as a <b>static web app</b>, hosted on GitHub "
        "Pages. This was chosen so the project can be opened in a browser "
        "without any installation, which makes grading easier. The iOS app is "
        "a small WKWebView wrapper around the same site, so a push to the "
        "repository updates the app on the next launch with no rebuild.",
        body))

    # ------------------- Frameworks comparison ------------------- #
    story.append(Paragraph("4. Frameworks, tools and trade-offs", h2))
    tdata = [
        ["", "Rasa", "Dialogflow", "Custom (chosen)"],
        ["Hosting",  "Self-host server",   "Google Cloud",
         "GitHub Pages (free)"],
        ["Setup at grading time", "Heavy install\n(broken on Py 3.14)",
         "Google account + internet", "Open the URL"],
        ["NLU",      "Built-in pipeline\n(DIET, etc.)",
         "Hosted neural model", "Bag-of-words + cosine + regex"],
        ["Dialog",   "Rule + ML stories", "Contexts / fulfilment",
         "Slot-filling FSM (8 slots)"],
        ["Cost / month", "Server costs",  "Per-call API bill",
         "EUR 0 (Pages free tier)"],
        ["Privacy",  "On your server",   "PII to Google",
         "All client-side"],
        ["iOS path", "Backend + API",    "Backend + API",
         "Same site in WKWebView"],
        ["Auditable","Yes",              "Partly (cloud config)",
         "Yes (every line in repo)"],
    ]
    table = Table(tdata, colWidths=[3.0 * cm, 4.0 * cm, 4.0 * cm, 5.0 * cm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(ACCENT_DARK)),
        ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
        ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",   (0, 0), (-1, -1), 8.6),
        ("BACKGROUND", (-1, 1), (-1, -1), colors.HexColor("#e6f7f8")),
        ("ALIGN",      (0, 0), (-1, -1), "LEFT"),
        ("VALIGN",     (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-2, -1),
         [colors.white, colors.HexColor("#f7f7f9")]),
        ("GRID",       (0, 0), (-1, -1), 0.3, colors.HexColor("#bbb")),
        ("LEFTPADDING",  (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING",   (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 4),
    ]))
    story.append(table)
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        "<b>Decision.</b> The custom static stack was chosen because it can be "
        "opened by the grader without any installation, all data stays on the "
        "device, and the iOS app updates automatically on every push to the "
        "repository. The trade-off is that a hand-written classifier does not "
        "generalise to paraphrases as well as a neural model, but the booking "
        "domain is small and the bot offers a fallback menu when a sentence "
        "does not match any pattern.",
        body))

    # ------------------- Mandatory vs optional ------------------- #
    story.append(Paragraph("5. Information captured", h2))
    story.append(Paragraph(
        "<b>Mandatory (assignment spec):</b> guest name, stay period (check-in "
        "and check-out), number of guests.<br/>"
        "<b>Optional extensions implemented:</b> room type (Standard, Deluxe, "
        "King Suite, Bosphorus Suite at EUR 120, 180, 280 and 420 per night), "
        "breakfast option (+EUR 10 per guest per night), payment method "
        "(credit card, debit card, or pay at the hotel), and a card form for "
        "the two card options that asks the guest to click a Pay button. "
        "The card form only collects the data: it does not run a real charge.",
        body))

    story.append(PageBreak())

    # ------------------- UML 1: Use case ------------------- #
    story.append(Paragraph("6. UML: Use case diagram", h2))
    story.append(Paragraph(
        "The use cases are grouped by area: concierge (cream), booking (teal) "
        "and admin (rose). The Guest is the main actor for the booking and "
        "concierge cases, the CEO is the main actor for the admin dashboard, "
        "and the browser storage is a secondary actor that keeps the bookings "
        "(localStorage) and the personal receipt scope (sessionStorage).",
        body))
    story.append(Image(str(figs["use_case"]), width=17 * cm, height=11 * cm,
                       kind="proportional"))
    story.append(Paragraph(
        "Figure 1. Use case diagram with 14 use cases grouped into three areas. "
        "Include and extend relationships are shown with dashed arrows.",
        caption))

    story.append(PageBreak())

    # ------------------- UML 2: Sequence ------------------- #
    story.append(Paragraph("7. UML: Sequence diagram (booking happy path)", h2))
    story.append(Paragraph(
        "The lifelines show the runtime layers: the web UI (chat.js + "
        "chat.html) sends each user message to the bot (bot.js, "
        "<code>HotelBookingBot.respond</code>), which calls the intent "
        "classifier and the entity extractors. The booking store writes to "
        "localStorage on confirmation. The two interactive widgets (calendar "
        "and card form) are rendered by the UI in response to slot changes "
        "returned by the bot.",
        body))
    story.append(Image(str(figs["sequence"]), width=17 * cm, height=12 * cm,
                       kind="proportional"))
    story.append(Paragraph(
        "Figure 2. Sequence diagram for the booking happy path, including "
        "the calendar widget and the new card-payment step.", caption))

    story.append(PageBreak())

    # ------------------- UML 3: State ------------------- #
    story.append(Paragraph("8. UML: State machine (slot machine)", h2))
    story.append(Paragraph(
        "The dialogue manager is a finite-state machine. A slot is filled by "
        "an entity extractor and the machine advances to the next missing "
        "slot. The three mandatory slots are highlighted in brass (per the "
        "assignment). Concierge intents are answered without changing the "
        "current slot, so the user can ask, for example, <i>where should I "
        "eat?</i> in the middle of a booking without losing their place. The "
        "<code>payment_card</code> state is reached only when the user picks "
        "credit or debit card; pay-at-hotel goes straight to confirm.",
        body))
    story.append(Image(str(figs["state"]), width=17 * cm, height=8 * cm,
                       kind="proportional"))
    story.append(Paragraph(
        "Figure 3. State machine for the booking conversation.", caption))

    # ------------------- UML 4: Component / deployment ------------------- #
    story.append(Paragraph("9. UML: Component and deployment", h2))
    story.append(Paragraph(
        "The whole system runs inside a single web container (the browser, or "
        "a WKWebView in the iOS app). The deployment loop is: push to "
        "GitHub, Pages rebuilds the site, the next page load downloads the "
        "new files. There is no server, no build step and no native binary to "
        "rebuild.",
        body))
    story.append(Image(str(figs["component"]), width=17 * cm, height=10 * cm,
                       kind="proportional"))
    story.append(Paragraph(
        "Figure 4. Component and deployment diagram.", caption))

    story.append(PageBreak())

    # ------------------- Workflow ------------------- #
    story.append(Paragraph("10. Chatbot development workflow", h2))
    story.append(Paragraph(
        "The pipeline taught in Lecture 03/04 (define scope, list intents and "
        "entities, write training data, define the conversation flow, train "
        "and test, iterate, deploy) is followed in this project. Each stage "
        "produces a file in the repository.",
        body))
    story.append(Image(str(figs["workflow"]), width=17 * cm, height=4.5 * cm,
                       kind="proportional"))
    story.append(Paragraph(
        "Figure 5. Project pipeline. The scope is in intents.json, the "
        "training data is in the patterns of each intent, the conversation "
        "flow is in chatbot.py / bot.js, the tests are in test_bot.py and "
        "test_web_bot.js, and deploy is to GitHub Pages.", caption))

    # ------------------- Data model ------------------- #
    story.append(Paragraph("11. Data and knowledge model", h2))
    story.append(Paragraph(
        "<b>Intents (intents.json):</b> 14 intents for the booking flow and "
        "general dialogue (greet, book_room, provide_name, provide_dates, "
        "provide_guests, breakfast_yes, breakfast_no, provide_payment, "
        "confirm_yes, confirm_no, goodbye, thanks, help, fallback) plus 16 "
        "concierge intents covering places_to_visit, food_recommendations, "
        "transport_airport, check_in_time, breakfast_hours, wifi, parking, "
        "amenities, cancellation_policy, pets, currency_info, tipping, "
        "language, hotel_contact, neighborhood, emergency, and room_types.",
        body))
    story.append(Paragraph(
        "<b>Domain entities:</b> Booking (name, check-in, check-out, room "
        "type, room rate, guests, breakfast, payment, payment confirmed, "
        "booking id, status, total in EUR), RoomType (id, name, rate, short "
        "description) and Availability, which maps a date to one of three "
        "states: free, peak-full, or guest-booked.",
        body))
    story.append(Paragraph(
        "<b>Storage:</b> localStorage holds the list of confirmed bookings "
        "(used by the admin page); sessionStorage holds the booking IDs of "
        "the current visit so the receipt page (booking.html) only shows the "
        "current guest's bookings. The admin login flag is also kept in "
        "sessionStorage.",
        body))

    # ------------------- Workplan + Risks ------------------- #
    story.append(Paragraph("12. Workplan and risk register", h2))
    cell = ParagraphStyle("cell", parent=body,
                          fontSize=8.6, leading=11, spaceAfter=0)
    cell_h = ParagraphStyle("cell_h", parent=cell,
                            fontName="Helvetica-Bold", textColor=colors.white)

    def C(t):  return Paragraph(t, cell)
    def CH(t): return Paragraph(t, cell_h)

    plan = [
        [CH("Stage"), CH("Output"), CH("Status")],
        [C("Conception (this document)"),
         C("Concept text, UML diagrams, framework choice"),
         C("this submission")],
        [C("Development"),
         C("Working chatbot, 30 intents, slot machine, UI, iOS shell"),
         C("complete")],
        [C("Reflection"),
         C("10-slide development presentation"),
         C("in progress")],
        [C("Finalization"),
         C("2-page abstract, zip of all files, Phase 1 and 2 with corrections"),
         C("pending feedback")],
    ]
    pt = Table(plan, colWidths=[4.0 * cm, 8.2 * cm, 4.3 * cm])
    pt.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(ACCENT_DARK)),
        ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
        ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",   (0, 0), (-1, -1), 8.6),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.white, colors.HexColor("#f7f7f9")]),
        ("GRID",       (0, 0), (-1, -1), 0.3, colors.HexColor("#bbb")),
        ("LEFTPADDING",(0, 0), (-1, -1), 5),
        ("RIGHTPADDING",(0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(pt)
    story.append(Spacer(1, 4))

    risks = [
        [CH("Risk"), CH("Impact"), CH("Mitigation")],
        [C("Bag-of-words classifier misses paraphrases"),
         C("User feels not understood"),
         C("Fallback reply offers a chip menu (Help, Book a "
           "room) so the user can continue without typing")],
        [C("Stale browser cache after a new deploy"),
         C("Users see old UI"),
         C("<code>?v=</code> version on every asset URL plus "
           "<code>no-cache</code> meta tag on every HTML page")],
        [C("Receipt visible to a different guest"),
         C("Privacy issue"),
         C("Booking IDs are tagged in sessionStorage so the "
           "receipt page only shows the current visit")],
        [C("Admin password is checked in the browser"),
         C("Easy to bypass"),
         C("Documented as a soft gate, used only for the "
           "prototype")],
        [C("No backend, no shared view of all bookings"),
         C("Architecture limit"),
         C("Admin sees only the bookings made on the same "
           "device; a real backend (e.g. Firestore) could be "
           "added later")],
    ]
    rt = Table(risks, colWidths=[5.0 * cm, 2.8 * cm, 8.7 * cm])
    rt.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(BRASS)),
        ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
        ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",   (0, 0), (-1, -1), 8.4),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.white, colors.HexColor("#fbf8f2")]),
        ("GRID",       (0, 0), (-1, -1), 0.3, colors.HexColor("#bbb")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING",(0, 0), (-1, -1), 5),
        ("RIGHTPADDING",(0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(rt)

    # ------------------- AI ethics / sustainability ------------------- #
    story.append(Paragraph("13. AI ethics and sustainability", h2))
    story.append(Paragraph(
        "<b>Privacy.</b> No personal data leaves the user's device. There are "
        "no analytics, no third-party trackers and no server-side logs. The "
        "NLU runs in the browser, and the chat transcript plus the booking "
        "are kept in the browser's local storage. The user can clear the "
        "data by clearing site data in the browser settings.",
        body))
    story.append(Paragraph(
        "<b>Inclusivity.</b> Quick-reply chips reduce typing for users who "
        "are not comfortable writing in English. The shooting-star background "
        "respects the <code>prefers-reduced-motion</code> setting and stops "
        "animating for users who request reduced motion. All controls are "
        "reachable with the keyboard and have ARIA labels.",
        body))
    story.append(Paragraph(
        "<b>Transparency.</b> The card form is clearly labelled as a demo "
        "('Demo only, your card is not actually charged.'). When a question "
        "is outside the chatbot's scope, the bot says so and points to the "
        "Help menu instead of guessing.",
        body))
    story.append(Paragraph(
        "<b>Sustainability.</b> The project does not use a backend, so there "
        "are no idle servers. GitHub Pages is served from a content delivery "
        "network. Each page is below 50 kB before fonts, which makes the "
        "energy use per session very low compared to a typical hotel website.",
        body))

    # ------------------- Footer note ------------------- #
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "<i>Submitted for the Conception phase of the portfolio "
        "(IU CSEMAIPAIUC01). The Phase 2 development presentation and the "
        "Phase 3 abstract follow the same naming convention.</i>",
        ParagraphStyle("foot", parent=body, fontSize=8.5,
                       textColor=colors.HexColor("#666"),
                       alignment=TA_CENTER)))

    # ------------------- Footer renderer ------------------- #
    def footer(canv, doc_):
        canv.saveState()
        canv.setFillColor(colors.HexColor("#666"))
        canv.setFont("Helvetica", 8)
        canv.drawRightString(A4[0] - 2 * cm, 1 * cm,
                             f"Phase 1, Concept   |   Page {canv.getPageNumber()}")
        canv.drawString(2 * cm, 1 * cm,
                        "Birol-Egemen | 10254279 | AIUseCase | Hotel | Concept")
        canv.setStrokeColor(colors.HexColor(ACCENT_DARK))
        canv.setLineWidth(0.6)
        canv.line(2 * cm, 1.4 * cm, A4[0] - 2 * cm, 1.4 * cm)
        canv.restoreState()

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(f"[OK] {OUT_PATH}  ({OUT_PATH.stat().st_size / 1024:.1f} KB)")


# --------------------------------------------------------------------------- #
# Main                                                                        #
# --------------------------------------------------------------------------- #

def main() -> None:
    figs = {
        "use_case":  FIG_DIR / "p1_use_case.png",
        "sequence":  FIG_DIR / "p1_sequence.png",
        "state":     FIG_DIR / "p1_state.png",
        "component": FIG_DIR / "p1_component.png",
        "workflow":  FIG_DIR / "p1_workflow.png",
    }
    print("[*] Rendering UML diagrams ...")
    make_use_case(figs["use_case"])
    make_sequence(figs["sequence"])
    make_state(figs["state"])
    make_component(figs["component"])
    make_workflow(figs["workflow"])
    print("[*] Building PDF ...")
    build_pdf(figs)


if __name__ == "__main__":
    main()
