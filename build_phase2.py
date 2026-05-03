"""
Build Phase 2 (Development & Reflection) presentation PDF for the
Birol Hotel chatbot.

Spec compliance (CSEMAIPAIUC01 portfolio brief):
  * "a composite presentation PDF with about 10 slides"   → 10 landscape slides
  * "visual elements that facilitate comprehension"        → diagrams + mockups
  * "it needs to be structured"                            → numbered slides
  * "also include hyperlinks to the frameworks used"       → clickable URLs
  * "the procedure should be described briefly"            → tight bullets
  * Activity coverage (per spec):
      ① Frameworks and tools set up        → slide 3
      ② Components implemented              → slide 4
      ③ Code is commented                   → slide 5
      ④ Training data collected             → slide 6
      ⑤ NLP models trained                  → slides 7 & 8
      ⑥ Iterative optimization              → slide 9

Output: AIUseCase_Hotel_P2/Birol-Egemen_12345678_AIUseCase_Hotel_Submission_Dev.pdf
"""

from __future__ import annotations
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas


# --------------------------------------------------------------------------- #
# Paths                                                                       #
# --------------------------------------------------------------------------- #
ROOT = Path(__file__).parent.resolve()
OUT_DIR = ROOT / "AIUseCase_Hotel_P2"
FIG_DIR = OUT_DIR / "figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)
FIG_DIR.mkdir(parents=True, exist_ok=True)
OUT_PATH = OUT_DIR / "Birol-Egemen_12345678_AIUseCase_Hotel_Submission_Dev.pdf"

# --------------------------------------------------------------------------- #
# Visual identity (matches IU lecture decks: dark BG + cyan accent)           #
# --------------------------------------------------------------------------- #
INK         = "#1f2430"
INK_DEEP    = "#0e1622"
INK_SOFT    = "#3a4154"
ACCENT      = "#5be1e6"   # IU teal
ACCENT_DARK = "#1ea7af"
BRASS       = "#9a7b4f"
BRASS_DARK  = "#7a5f3b"
CREAM       = "#f5f1ea"
PAPER       = "#ffffff"


# --------------------------------------------------------------------------- #
# Diagrams                                                                    #
# --------------------------------------------------------------------------- #

def _box(ax, xy, w, h, text, fc="#ffffff", ec=INK, tc=INK,
         fs=8.5, bold=False, radius=0.10):
    x, y = xy
    box = mpatches.FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0.02,rounding_size={radius}",
        linewidth=1.1, facecolor=fc, edgecolor=ec)
    ax.add_patch(box)
    weight = "bold" if bold else "normal"
    ax.text(x + w / 2, y + h / 2, text,
            ha="center", va="center",
            fontsize=fs, color=tc, fontweight=weight)


def _arrow(ax, p1, p2, label=None, color=INK, ls="-", lw=1.0, fs=7.5):
    ax.annotate("", xy=p2, xytext=p1,
                arrowprops=dict(arrowstyle="->", color=color, lw=lw,
                                linestyle=ls, shrinkA=4, shrinkB=4))
    if label:
        mx, my = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2
        ax.text(mx, my, label, fontsize=fs, color=color,
                ha="center", va="center",
                bbox=dict(boxstyle="round,pad=0.18", facecolor="white",
                          edgecolor="none", alpha=0.9))


def make_pipeline(out: Path) -> None:
    """Slide-friendly chatbot dev pipeline (Lec 03/04 style)."""
    fig, ax = plt.subplots(figsize=(11.0, 2.6))
    ax.set_xlim(0, 12); ax.set_ylim(0, 2.6)
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
        _box(ax, (x - 0.7, 0.9), 1.4, 0.85, label,
             fc=ACCENT, tc=INK, bold=True, fs=8.5)
    for (a, ax_x), (b, bx_x) in zip(steps, steps[1:]):
        _arrow(ax, (ax_x + 0.7, 1.32), (bx_x - 0.7, 1.32))

    artifacts = [
        "intents.json",
        "patterns +\nresponses",
        "test cases",
        "slot machine\nin bot.js",
        "Node + Python\nrunners",
        "fix bugs,\ntune patterns",
        "GitHub Pages\n+ WKWebView",
    ]
    for (label, x), d in zip(steps, artifacts):
        ax.text(x, 0.18, d, ha="center", va="center",
                fontsize=7.2, color=INK_SOFT, style="italic")

    fig.tight_layout()
    fig.savefig(out, dpi=210, bbox_inches="tight", facecolor=PAPER)
    plt.close(fig)


def make_state_machine(out: Path) -> None:
    fig, ax = plt.subplots(figsize=(11.4, 4.2))
    ax.set_xlim(0, 12); ax.set_ylim(0, 4.4)
    ax.set_aspect("equal"); ax.axis("off")

    states = [
        ("greet",        0.6, 2.5),
        ("name",         2.0, 2.5),
        ("dates",        3.5, 2.5),
        ("room_type",    5.1, 2.5),
        ("guests",       6.7, 2.5),
        ("breakfast",    8.3, 2.5),
        ("payment",      9.9, 2.5),
        ("payment_card", 9.9, 1.0),
        ("confirm",      11.4, 2.5),
    ]
    mandatory = {"name", "dates", "guests"}
    for n, x, y in states:
        fc = BRASS if n in mandatory else "white"
        tc = "white" if n in mandatory else INK
        _box(ax, (x - 0.55, y - 0.30), 1.10, 0.60, n,
             fc=fc, tc=tc, bold=True, fs=8.5)

    ax.plot(0.10, 2.50, "o", markersize=12, color=INK)
    _arrow(ax, (0.13, 2.5), (0.05, 2.5), lw=1.1)

    main = ["greet", "name", "dates", "room_type",
            "guests", "breakfast", "payment"]
    pos = {n: (x, y) for (n, x, y) in states}
    for a, b in zip(main, main[1:]):
        x1 = pos[a][0] + 0.55; x2 = pos[b][0] - 0.55
        _arrow(ax, (x1, 2.5), (x2, 2.5))

    _arrow(ax, (10.45, 2.55), (10.85, 2.55), label="hotel pay", fs=7)
    _arrow(ax, (9.9, 2.20), (9.9, 1.30),
           label="card", fs=7, color=BRASS_DARK, lw=1.3)
    _arrow(ax, (10.25, 1.10), (11.35, 2.20),
           label="Pay click", fs=7, color=BRASS_DARK, lw=1.3)

    ax.plot(12.25, 2.50, "o", markersize=14,
            markerfacecolor="white", markeredgecolor=INK, markeredgewidth=1.6)
    ax.plot(12.25, 2.50, "o", markersize=7, color=INK)
    _arrow(ax, (11.95, 2.5), (12.18, 2.5), label="confirm", fs=7)

    _arrow(ax, (11.4, 2.20), (2.0, 1.55), color="#aa3344", lw=1.2,
           label="cancel / restart", fs=7)
    _arrow(ax, (2.0, 1.55), (2.0, 2.20), color="#aa3344", lw=1.2)

    rect = mpatches.FancyBboxPatch(
        (2.5, 3.55), 7.5, 0.45,
        boxstyle="round,pad=0.04,rounding_size=0.10",
        linewidth=0, facecolor="#e6f7f8")
    ax.add_patch(rect)
    ax.text(6.25, 3.78,
            "Concierge intents (places to visit, wifi, parking, …) "
            "are answered transversally and the bot returns to the current slot.",
            ha="center", fontsize=7.5, color=INK)

    ax.text(6.0, 0.18,
            "● Brass = mandatory slots (name, dates, guests, per assignment spec)        "
            "● White = optional / configuration         "
            "● Red = restart edge",
            ha="center", fontsize=7.6, color=INK_SOFT)

    fig.tight_layout()
    fig.savefig(out, dpi=210, bbox_inches="tight", facecolor=PAPER)
    plt.close(fig)


def make_test_growth(out: Path) -> None:
    """Bar chart: how the test count grew across iterative refinement."""
    fig, ax = plt.subplots(figsize=(7.0, 3.6))
    fig.patch.set_facecolor(PAPER)

    milestones = [
        "Phase 1\nbaseline",
        "After\nconfirm-yes\nfix",
        "Web bot\nport",
        "After\nrooms +\npricing",
        "After card\nform + find",
        "Now",
    ]
    py    = [15, 17, 17, 17, 17, 17]
    web   = [0,   0, 18, 29, 35, 35]
    total = [a + b for a, b in zip(py, web)]

    xs = list(range(len(milestones)))
    ax.bar(xs, py,  color=ACCENT_DARK, label="Python tests (Flask)")
    ax.bar(xs, web, bottom=py, color=BRASS, label="JS tests (browser bot)")

    for i, t in enumerate(total):
        ax.text(i, t + 1.5, str(t), ha="center", fontsize=10,
                fontweight="bold", color=INK)

    ax.set_xticks(xs)
    ax.set_xticklabels(milestones, fontsize=8)
    ax.set_ylabel("Tests passing", fontsize=9)
    ax.set_ylim(0, 60)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", alpha=0.25)
    ax.legend(fontsize=8, loc="upper left", frameon=False)
    ax.set_title("Test coverage — grew with every iteration",
                 fontsize=10, color=INK, pad=8)

    fig.tight_layout()
    fig.savefig(out, dpi=210, bbox_inches="tight", facecolor=PAPER)
    plt.close(fig)


def make_ui_mocks(out: Path) -> None:
    """Six small phone-shaped panels showing each UI surface."""
    fig, ax = plt.subplots(figsize=(11.6, 5.8))
    ax.set_xlim(0, 12); ax.set_ylim(0, 6.0)
    ax.set_aspect("equal"); ax.axis("off")
    fig.patch.set_facecolor(PAPER)

    def phone(x0, y0, title, draw):
        # Phone outline
        rect = mpatches.FancyBboxPatch(
            (x0, y0), 1.85, 3.7,
            boxstyle="round,pad=0.02,rounding_size=0.18",
            linewidth=1.2, facecolor="#0c0f23", edgecolor=INK)
        ax.add_patch(rect)
        # Title
        ax.text(x0 + 0.92, y0 + 3.5, title,
                ha="center", fontsize=8.5, color=ACCENT,
                fontweight="bold")
        # User-supplied content
        draw(x0, y0)
        # Caption
        return rect

    # 1. Landing
    def draw_landing(x0, y0):
        # hero strip
        ax.add_patch(mpatches.Rectangle(
            (x0 + 0.10, y0 + 1.95), 1.65, 1.30,
            facecolor="#1b2069", edgecolor="none"))
        ax.text(x0 + 0.92, y0 + 2.85, "Birol Hotel",
                ha="center", fontsize=7.5, color="white",
                fontweight="bold", fontstyle="italic")
        ax.text(x0 + 0.92, y0 + 2.55, "twilight on the\nBosphorus",
                ha="center", fontsize=5.5, color="#cdd0df")
        # Orb
        ax.add_patch(mpatches.Circle(
            (x0 + 0.92, y0 + 1.1), 0.32,
            facecolor="#0a0b18", edgecolor="white", linewidth=1.0))
        ax.add_patch(mpatches.Circle(
            (x0 + 0.92, y0 + 1.1), 0.42,
            facecolor="none", edgecolor="white", linewidth=0.4, alpha=0.4))
        ax.text(x0 + 0.92, y0 + 1.65,
                "Click to book\na room with AI",
                ha="center", fontsize=6, color="white",
                fontstyle="italic")

    phone(0.2, 0.7, "1 · Landing", draw_landing)

    # 2. Chat with chips
    def draw_chat(x0, y0):
        # bot bubble
        ax.add_patch(mpatches.FancyBboxPatch(
            (x0 + 0.10, y0 + 2.7), 1.20, 0.32,
            boxstyle="round,pad=0.02,rounding_size=0.06",
            facecolor="#2a2d44", edgecolor="none"))
        ax.text(x0 + 0.13, y0 + 2.85, "How may I help today?",
                fontsize=5.4, color="white")
        # chips
        for i, (txt, col) in enumerate([("Book a room", BRASS),
                                         ("Availability", "#374"),
                                         ("Help", "#374")]):
            ax.add_patch(mpatches.FancyBboxPatch(
                (x0 + 0.10 + i * 0.55, y0 + 2.30), 0.50, 0.22,
                boxstyle="round,pad=0.02,rounding_size=0.10",
                facecolor=col, edgecolor="none"))
            ax.text(x0 + 0.35 + i * 0.55, y0 + 2.41, txt,
                    fontsize=4.5, color="white", ha="center")
        # user
        ax.add_patch(mpatches.FancyBboxPatch(
            (x0 + 0.95, y0 + 1.85), 0.80, 0.30,
            boxstyle="round,pad=0.02,rounding_size=0.06",
            facecolor=BRASS, edgecolor="none"))
        ax.text(x0 + 1.35, y0 + 2.0, "book a room",
                fontsize=5, color="white", ha="center")
        ax.add_patch(mpatches.FancyBboxPatch(
            (x0 + 0.10, y0 + 1.40), 1.50, 0.30,
            boxstyle="round,pad=0.02,rounding_size=0.06",
            facecolor="#2a2d44", edgecolor="none"))
        ax.text(x0 + 0.85, y0 + 1.55, "May I have your full name?",
                fontsize=5, color="white", ha="center")

    phone(2.2, 0.7, "2 · Chat + chips", draw_chat)

    # 3. Calendar widget
    def draw_calendar(x0, y0):
        ax.text(x0 + 0.92, y0 + 3.0, "May 2026",
                ha="center", fontsize=6, color="white",
                fontweight="bold")
        # 7×5 grid
        for c in range(7):
            for r in range(5):
                cx = x0 + 0.18 + c * 0.22
                cy = y0 + 0.5 + (4 - r) * 0.36
                # color: highlight a range row 2 col 2-5; mark a "full"
                if r == 1 and 1 <= c <= 4:
                    fcol = ACCENT_DARK if c in (1, 4) else "#3a4858"
                elif r == 2 and c == 5:
                    fcol = "#5a3030"   # full
                else:
                    fcol = "#2a2d44"
                ax.add_patch(mpatches.Rectangle(
                    (cx, cy), 0.20, 0.30, facecolor=fcol,
                    edgecolor="white", linewidth=0.3))

    phone(4.2, 0.7, "3 · Calendar", draw_calendar)

    # 4. Card form
    def draw_card(x0, y0):
        # Card shape
        ax.add_patch(mpatches.FancyBboxPatch(
            (x0 + 0.12, y0 + 1.80), 1.60, 1.20,
            boxstyle="round,pad=0.02,rounding_size=0.12",
            facecolor="#1a233a", edgecolor="white", linewidth=0.7))
        ax.text(x0 + 0.20, y0 + 2.85, "Credit", fontsize=5,
                color="white", fontstyle="italic", fontweight="bold")
        # chip
        ax.add_patch(mpatches.Rectangle(
            (x0 + 1.45, y0 + 2.78), 0.18, 0.13,
            facecolor="#d8c98a", edgecolor="white", linewidth=0.3))
        # number
        ax.text(x0 + 0.92, y0 + 2.40, "1234 5678 90",
                fontsize=6, color="white",
                family="monospace", ha="center", fontweight="bold")
        # name
        ax.text(x0 + 0.20, y0 + 1.95, "EGEMEN BIROL",
                fontsize=4.6, color="white", family="monospace")
        ax.text(x0 + 1.40, y0 + 1.95, "12/28",
                fontsize=4.6, color="white", family="monospace")
        # Pay button
        ax.add_patch(mpatches.FancyBboxPatch(
            (x0 + 0.45, y0 + 1.20), 1.0, 0.32,
            boxstyle="round,pad=0.02,rounding_size=0.12",
            facecolor=BRASS, edgecolor="white", linewidth=0.7))
        ax.text(x0 + 0.95, y0 + 1.36, "Pay €800",
                fontsize=6, color="white", ha="center", fontweight="bold")

    phone(6.2, 0.7, "4 · Card form", draw_card)

    # 5. Receipt
    def draw_receipt(x0, y0):
        ax.add_patch(mpatches.FancyBboxPatch(
            (x0 + 0.12, y0 + 1.20), 1.60, 1.85,
            boxstyle="round,pad=0.02,rounding_size=0.10",
            facecolor="#1a233a", edgecolor="white", linewidth=0.6))
        ax.text(x0 + 0.92, y0 + 2.85, "✓ Confirmed",
                ha="center", fontsize=5.5,
                color="#9effc9", fontweight="bold")
        ax.text(x0 + 0.92, y0 + 2.60, "Egemen Birol",
                ha="center", fontsize=6.2, color="white",
                fontstyle="italic", fontweight="bold")
        ax.text(x0 + 0.92, y0 + 2.30,
                "May 10  →  May 14",
                ha="center", fontsize=5, color="#cdd0df")
        ax.text(x0 + 0.92, y0 + 2.10, "4 nights · 2 guests",
                ha="center", fontsize=4.5, color="#8087a0")
        ax.text(x0 + 0.92, y0 + 1.70,
                "Total  €800",
                ha="center", fontsize=6.5, color="white",
                fontweight="bold")
        ax.text(x0 + 0.92, y0 + 1.35, "BH-A1B2C3D4",
                ha="center", fontsize=4.8,
                color="#8087a0", family="monospace")

    phone(8.2, 0.7, "5 · Receipt", draw_receipt)

    # 6. CEO admin
    def draw_admin(x0, y0):
        # stat tiles
        for i, (lbl, val) in enumerate(
                [("Bookings", "12"), ("Guests", "27"), ("Nights", "48")]):
            ax.add_patch(mpatches.Rectangle(
                (x0 + 0.10 + i * 0.55, y0 + 2.55), 0.50, 0.45,
                facecolor="#2a2d44", edgecolor="none"))
            ax.text(x0 + 0.35 + i * 0.55, y0 + 2.95, lbl,
                    ha="center", fontsize=4.2, color="#8087a0")
            ax.text(x0 + 0.35 + i * 0.55, y0 + 2.65, val,
                    ha="center", fontsize=8, color="white",
                    fontweight="bold")
        # mini calendar with guest cells
        for c in range(7):
            for r in range(4):
                cx = x0 + 0.18 + c * 0.22
                cy = y0 + 0.6 + (3 - r) * 0.32
                if (r, c) in {(0, 2), (0, 3), (1, 2)}:
                    fcol = "#3674a8"  # guest booked
                elif (r, c) in {(2, 5), (2, 6)}:
                    fcol = "#5a3030"  # peak
                else:
                    fcol = "#2a2d44"
                ax.add_patch(mpatches.Rectangle(
                    (cx, cy), 0.20, 0.26, facecolor=fcol,
                    edgecolor="white", linewidth=0.3))

    phone(10.2, 0.7, "6 · CEO admin", draw_admin)

    fig.tight_layout()
    fig.savefig(out, dpi=210, bbox_inches="tight", facecolor=PAPER)
    plt.close(fig)


# --------------------------------------------------------------------------- #
# PDF assembly                                                                 #
# --------------------------------------------------------------------------- #

PAGE = landscape(A4)   # (842, 595) points
W, H = PAGE


def slide_header(c, slide_no, total, title, subtitle=""):
    # Top dark band
    c.setFillColor(colors.HexColor(INK))
    c.rect(0, H - 2.2 * cm, W, 2.2 * cm, fill=1, stroke=0)
    c.setFillColor(colors.HexColor(ACCENT))
    c.rect(0, H - 2.30 * cm, W, 0.10 * cm, fill=1, stroke=0)

    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(2 * cm, H - 1.30 * cm, title)
    if subtitle:
        c.setFont("Helvetica", 10)
        c.setFillColor(colors.HexColor("#c8ced9"))
        c.drawString(2 * cm, H - 1.80 * cm, subtitle)

    c.setFillColor(colors.HexColor(ACCENT))
    c.setFont("Helvetica-Bold", 11)
    c.drawRightString(W - 2 * cm, H - 1.30 * cm, f"{slide_no}/{total}")


def slide_footer(c):
    c.setFillColor(colors.HexColor("#6b7280"))
    c.setFont("Helvetica", 7.8)
    c.drawString(2 * cm, 0.95 * cm,
                 "Birol-Egemen · 12345678 · CSEMAIPAIUC01 · Phase 2 — Development")
    c.drawRightString(W - 2 * cm, 0.95 * cm,
                      "Hotel Booking Chatbot — Aria · Birol Hotel")
    c.setStrokeColor(colors.HexColor(ACCENT_DARK))
    c.line(2 * cm, 1.35 * cm, W - 2 * cm, 1.35 * cm)


def hyperlink(c, x, y, label, url, size=11):
    """Render a clickable hyperlink in IU-blue."""
    c.setFillColor(colors.HexColor("#1a56a8"))
    c.setFont("Helvetica", size)
    c.drawString(x, y, label)
    tw = c.stringWidth(label, "Helvetica", size)
    c.line(x, y - 1, x + tw, y - 1)
    c.linkURL(url, (x, y - 3, x + tw, y + size - 3), relative=0)
    c.setFillColor(colors.HexColor(INK))


def bullet(c, x, y, text, size=11.5):
    c.setFillColor(colors.HexColor(ACCENT_DARK))
    c.setFont("Helvetica-Bold", size)
    c.drawString(x, y, "●")
    c.setFillColor(colors.HexColor(INK))
    c.setFont("Helvetica", size)
    c.drawString(x + 0.6 * cm, y, text)


# --------------------------------------------------------------------------- #
# Slides                                                                       #
# --------------------------------------------------------------------------- #

def slide_1_title(c):
    # Full-bleed dark cover
    c.setFillColor(colors.HexColor(INK_DEEP))
    c.rect(0, 0, W, H, fill=1, stroke=0)
    # Cyan accent block behind title
    c.setFillColor(colors.HexColor(ACCENT))
    c.rect(0, H / 2 - 0.5 * cm, W * 0.58, 3.6 * cm, fill=1, stroke=0)

    c.setFillColor(colors.HexColor(INK_DEEP))
    c.setFont("Helvetica-Bold", 34)
    c.drawString(2 * cm, H / 2 + 1.7 * cm, "Phase 2 — Development")

    c.setFont("Helvetica-Bold", 22)
    c.drawString(2 * cm, H / 2 + 0.45 * cm, "Birol Hotel")

    c.setFillColor(colors.HexColor("#0e1622"))
    c.setFont("Helvetica", 14)
    c.drawString(2 * cm, H / 2 - 0.20 * cm, "Booking Chatbot — Aria")

    c.setFillColor(colors.white)
    c.setFont("Helvetica", 11)
    c.drawString(2 * cm, 3.5 * cm, "Birol, Egemen   ·   Matriculation 12345678")
    c.drawString(2 * cm, 2.9 * cm, "Project: AI Use Case (CSEMAIPAIUC01)  ·  Task 1")
    c.drawString(2 * cm, 2.3 * cm, "IU International University of Applied Sciences")
    c.setFillColor(colors.HexColor(ACCENT))
    c.drawString(2 * cm, 1.6 * cm, "A composite presentation per the portfolio brief — 10 slides")


def slide_2_objectives(c):
    slide_header(c, 2, 10, "Phase 2 objectives",
                 "What the assignment brief requires this deck to cover")

    c.setFillColor(colors.HexColor(INK))
    c.setFont("Helvetica", 11)
    c.drawString(2 * cm, H - 3.3 * cm,
                 "Six development activities (per CSEMAIPAIUC01, §1.1.2):")

    items = [
        "①  The frameworks and tools are set up.                      → Slide 3",
        "②  The components outlined in the diagram are implemented.    → Slide 4",
        "③  The code is commented.                                     → Slide 5",
        "④  The training data for the chatbot is collected.            → Slide 6",
        "⑤  The NLP models are trained.                                → Slides 7 + 8",
        "⑥  Iterative optimization of the system.                      → Slide 9",
    ]
    y = H - 4.5 * cm
    for it in items:
        bullet(c, 2.4 * cm, y, it)
        y -= 0.85 * cm

    c.setFillColor(colors.HexColor("#666"))
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(2 * cm, 4.3 * cm,
                 "Plus: visual elements that facilitate comprehension · structured · "
                 "hyperlinks to the frameworks used · brief procedure descriptions.")
    c.drawString(2 * cm, 3.7 * cm,
                 "Slide 10 closes with a live UI demo and the public URLs.")
    slide_footer(c)


def slide_3_frameworks(c):
    slide_header(c, 3, 10, "① Frameworks & tools set up",
                 "What we used, what we considered, why we chose what we chose")

    # Two columns
    col1_x = 2 * cm
    col2_x = W / 2 + 0.8 * cm

    c.setFillColor(colors.HexColor(ACCENT_DARK))
    c.setFont("Helvetica-Bold", 13)
    c.drawString(col1_x, H - 3.3 * cm, "Used in this build")
    c.drawString(col2_x, H - 3.3 * cm, "Considered & rejected")

    # Left col — used
    items_left = [
        ("Python 3.10+",            "https://www.python.org",
         "language for the original prototype"),
        ("Flask 3.x",               "https://flask.palletsprojects.com",
         "minimal web server (Phase 1 prototype)"),
        ("Vanilla HTML/CSS/JS",     "https://developer.mozilla.org/en-US/docs/Web",
         "no build step, ports cleanly to Pages"),
        ("GitHub Pages",            "https://pages.github.com",
         "auto-deploy on every push to main"),
        ("WKWebView (iOS)",         "https://developer.apple.com/documentation/webkit/wkwebview",
         "thin SwiftUI shell around the same site"),
    ]
    y = H - 4.2 * cm
    for label, url, why in items_left:
        hyperlink(c, col1_x, y, label, url, size=11.5)
        c.setFillColor(colors.HexColor("#555"))
        c.setFont("Helvetica-Oblique", 9.5)
        c.drawString(col1_x, y - 0.45 * cm, why)
        y -= 1.2 * cm

    # Right col — considered
    items_right = [
        ("Rasa",       "https://rasa.com",
         "production-grade, but install fails on Py 3.14;\nheavy for a 6-slot form"),
        ("Dialogflow", "https://cloud.google.com/dialogflow",
         "hosted neural NLU; needs Google account and\ninternet access at grading time"),
        ("spaCy",      "https://spacy.io",
         "great real NER, but ~50 MB model download\nfor a closed-domain bot — overkill"),
        ("scikit-learn TF-IDF", "https://scikit-learn.org",
         "would still work, but adds a dependency for\nno meaningful gain over our hand-rolled cosine"),
    ]
    y = H - 4.2 * cm
    for label, url, why in items_right:
        hyperlink(c, col2_x, y, label, url, size=11.5)
        c.setFillColor(colors.HexColor("#555"))
        c.setFont("Helvetica-Oblique", 9.5)
        for line in why.split("\n"):
            c.drawString(col2_x, y - 0.45 * cm, line)
            y -= 0.42 * cm
        y -= 0.78 * cm

    # Decision banner
    c.setFillColor(colors.HexColor("#e6f7f8"))
    c.rect(2 * cm, 2.6 * cm, W - 4 * cm, 1.4 * cm, fill=1, stroke=0)
    c.setFillColor(colors.HexColor(INK))
    c.setFont("Helvetica-Bold", 11)
    c.drawString(2.4 * cm, 3.5 * cm, "Decision  →  custom static stack")
    c.setFont("Helvetica", 10)
    c.drawString(2.4 * cm, 2.95 * cm,
                 "Decisive factors: zero-setup for the grader, no PII leaves the device, "
                 "and the iOS app auto-updates on every git push.")

    slide_footer(c)


def slide_4_components(c):
    slide_header(c, 4, 10, "② Components implemented",
                 "Mapping the Phase 1 architecture onto real files in the repo")

    c.setFillColor(colors.HexColor(INK))
    c.setFont("Courier", 10)
    tree = [
        "Hotel_Booking_Bot/",
        "|-- docs/                          static site (deployed via GitHub Pages)",
        "|   |-- index.html                 landing - 'Click to book a room with AI'",
        "|   |-- chat.html                  chat interface (calendar + card form)",
        "|   |-- booking.html               receipt page (per-session)",
        "|   |-- find.html                  find a booking by reference",
        "|   |-- admin.html                 password-gated CEO dashboard",
        "|   |-- js/",
        "|   |   |-- bot.js                 NLP + slot machine + booking store",
        "|   |   |-- chat.js                chat UI controller + calendar + card form",
        "|   |   |-- booking.js             receipt rendering",
        "|   |   |-- admin.js               admin login + occupancy grid",
        "|   |   `-- find.js                booking lookup by id",
        "|   |-- styles/                    landing/chat/booking/admin/find + stars",
        "|   |-- data/intents.json          14 main + 16 concierge intents - ~120 patterns",
        "|   `-- assets/hotel-hero.svg      twilight illustration",
        "|-- src/                           original Flask prototype (Phase 1)",
        "|   |-- app.py - chatbot.py - nlp.py - booking.py - availability.py",
        "|   `-- templates - static",
        "|-- tests/                         52 tests passing",
        "|   |-- test_bot.py                17 Python tests (Flask bot)",
        "|   `-- test_web_bot.js            35 JS tests (browser bot)",
        "|-- ios/BirolHotel/                SwiftUI WKWebView wrapper",
        "`-- AIUseCase_Hotel_P1 / P2 / P3   PebblePad submission folders",
    ]
    y = H - 3.0 * cm
    for ln in tree:
        c.drawString(2 * cm, y, ln)
        y -= 0.45 * cm

    slide_footer(c)


def slide_5_comments(c):
    slide_header(c, 5, 10, "③ Code is commented",
                 "Every module begins with a docstring; functions carry intent")

    # Left snippet: bot.js header
    c.setFillColor(colors.HexColor("#0e1622"))
    c.rect(2 * cm, 3 * cm, (W - 4 * cm) / 2 - 0.3 * cm, H - 6.5 * cm,
           fill=1, stroke=0)
    c.setFillColor(colors.HexColor(ACCENT))
    c.setFont("Courier-Bold", 10)
    c.drawString(2.3 * cm, H - 3.5 * cm, "// docs/js/bot.js")

    c.setFillColor(colors.white)
    c.setFont("Courier", 9.2)
    snippet1 = [
        "// =========================================================",
        "// Birol Hotel — chatbot",
        "// =========================================================",
        "// No build step, no backend. Lives happily on GitHub Pages.",
        "// Mirrors src/nlp.py, src/booking.py, src/chatbot.py.",
        "// =========================================================",
        "",
        "/** Bag-of-words cosine-similarity intent matcher.",
        " *  Trained by loading the patterns from intents.json. */",
        "class IntentClassifier { ... }",
        "",
        "/** Pull a plausible full name out of a free-form reply.",
        " *  Falls back to 'two+ capitalised words' so a bare",
        " *  reply like 'Egemen Birol' still works. */",
        "function extractName(text) { ... }",
        "",
        "/** Hotel-side conversation state. nextMissingSlot()",
        " *  returns the next slot to fill in canonical order. */",
        "class BookingConversation { ... }",
    ]
    y = H - 4.0 * cm
    for ln in snippet1:
        c.drawString(2.4 * cm, y, ln)
        y -= 0.42 * cm

    # Right snippet: chatbot.py header
    c.setFillColor(colors.HexColor("#0e1622"))
    c.rect(W / 2 + 0.3 * cm, 3 * cm,
           (W - 4 * cm) / 2 - 0.3 * cm, H - 6.5 * cm,
           fill=1, stroke=0)
    c.setFillColor(colors.HexColor(ACCENT))
    c.setFont("Courier-Bold", 10)
    c.drawString(W / 2 + 0.6 * cm, H - 3.5 * cm, "# src/chatbot.py")

    c.setFillColor(colors.white)
    c.setFont("Courier", 9.2)
    snippet2 = [
        "\"\"\"",
        "Dialog manager: glues NLP + booking state into a",
        "single respond() method.",
        "",
        "Design:",
        "  * The classifier tells us *what* the user wants.",
        "  * The booking state tells us *which slot* we still",
        "    need to fill.",
        "  * respond() reconciles the two: it prefers filling",
        "    the next missing slot from the message (so the",
        "    user can volunteer information out of order),",
        "    but also handles transversal intents (greet,",
        "    help, goodbye, restart).",
        "\"\"\"",
        "",
        "class HotelBookingBot:",
        "    \"\"\"Stateful hotel-booking chatbot.\"\"\"",
        "    HOTEL_NAME = \"Birol Hotel\"",
        "    ...",
    ]
    y = H - 4.0 * cm
    for ln in snippet2:
        c.drawString(W / 2 + 0.6 * cm, y, ln)
        y -= 0.42 * cm

    # Repo link
    c.setFillColor(colors.HexColor(INK))
    c.setFont("Helvetica", 10)
    c.drawString(2 * cm, 2.4 * cm, "Full source online: ")
    hyperlink(c, 6 * cm, 2.4 * cm,
              "github.com/Ho11owpoint/Hotel_Booking_Bot",
              "https://github.com/Ho11owpoint/Hotel_Booking_Bot",
              size=10)

    slide_footer(c)


def slide_6_training_data(c):
    slide_header(c, 6, 10, "④ Training data collected",
                 "30 intents · ~120 patterns · curated, no scraped data")

    # Left: intent table
    c.setFillColor(colors.HexColor(INK))
    c.setFont("Helvetica-Bold", 11)
    c.drawString(2 * cm, H - 3.3 * cm, "Intent catalogue")

    cats = [
        ("Booking flow",     ACCENT_DARK,
         "greet · book_room · provide_name · provide_dates ·\n"
         "provide_guests · breakfast_yes / no · provide_payment ·\n"
         "confirm_yes / no · room_types"),
        ("Concierge Q&A",    BRASS,
         "places_to_visit · food_recommendations · transport_airport ·\n"
         "check_in_time · breakfast_hours · wifi · parking · amenities ·\n"
         "cancellation_policy · pets · currency_info · tipping ·\n"
         "language · hotel_contact · neighborhood · emergency"),
        ("Meta",             "#666",
         "help · thanks · goodbye · fallback · availability_info"),
    ]
    y = H - 4.0 * cm
    for cat, col, body in cats:
        c.setFillColor(colors.HexColor(col))
        c.setFont("Helvetica-Bold", 10)
        c.drawString(2 * cm, y, cat)
        c.setFillColor(colors.HexColor(INK))
        c.setFont("Helvetica", 9)
        for line in body.split("\n"):
            y -= 0.38 * cm
            c.drawString(2.3 * cm, y, line)
        y -= 0.55 * cm

    # Right: JSON snippet
    c.setFillColor(colors.HexColor("#0e1622"))
    c.rect(W / 2 + 0.3 * cm, 2.6 * cm,
           (W - 4 * cm) / 2 - 0.3 * cm, H - 6.0 * cm,
           fill=1, stroke=0)
    c.setFillColor(colors.HexColor(ACCENT))
    c.setFont("Courier-Bold", 10)
    c.drawString(W / 2 + 0.6 * cm, H - 3.5 * cm, "// docs/data/intents.json")

    c.setFillColor(colors.white)
    c.setFont("Courier", 9)
    sample = [
        "{",
        "  \"tag\": \"places_to_visit\",",
        "  \"patterns\": [",
        "    \"places to visit\",",
        "    \"what to visit\",",
        "    \"attractions\",",
        "    \"sightseeing\",",
        "    \"tourist spots\",",
        "    \"best places\",",
        "    \"istanbul attractions\",",
        "    \"things to do\",",
        "    \"must see\",",
        "    ... 10 more",
        "  ],",
        "  \"responses\": [",
        "    \"**Top places to visit in Istanbul:**\\n\\n",
        "      • **Hagia Sophia** ...\\n",
        "      • **Blue Mosque** ...\\n",
        "      • **Topkapi Palace** ...\\n",
        "      ...\"",
        "  ]",
        "}",
    ]
    y = H - 4.0 * cm
    for ln in sample:
        c.drawString(W / 2 + 0.6 * cm, y, ln)
        y -= 0.40 * cm

    slide_footer(c)


def slide_7_classifier(c):
    slide_header(c, 7, 10, "⑤ NLP — Intent classifier",
                 "Bag-of-words + cosine similarity, trained on intents.json")

    # Bullets on left
    items = [
        "Tokenise:  lowercase, strip punctuation, drop English stopwords",
        "Vectorise: Counter-based bag-of-words for query and every pattern",
        "Match:     cosine similarity → (intent, confidence)",
        "Threshold: confidence < 0.35 → fallback intent",
        "Concierge gate: confidence ≥ 0.4 to fire transversally",
        "Cost: O(N × |query|), N ≈ 120 patterns. Sub-millisecond on a phone.",
    ]
    y = H - 3.3 * cm
    for it in items:
        bullet(c, 2 * cm, y, it, size=10.5)
        y -= 0.7 * cm

    # Code snippet (bottom right)
    code_x = W / 2 + 0.3 * cm
    code_y = 2.4 * cm
    code_w = (W - 4 * cm) / 2 - 0.3 * cm
    code_h = H - 6.5 * cm
    c.setFillColor(colors.HexColor("#0e1622"))
    c.rect(code_x, code_y, code_w, code_h, fill=1, stroke=0)
    c.setFillColor(colors.HexColor(ACCENT))
    c.setFont("Courier-Bold", 10)
    c.drawString(code_x + 0.3 * cm, code_y + code_h - 0.6 * cm,
                 "// docs/js/bot.js  —  classify()")

    snippet = [
        "classify(message) {",
        "  const q = counter(tokenize(message));",
        "  let bestTag = 'fallback', bestScore = 0;",
        "  for (const [tag, vec] of this.patternVectors) {",
        "    const s = cosine(q, vec);",
        "    if (s > bestScore) {",
        "      bestTag = tag; bestScore = s;",
        "    }",
        "  }",
        "  if (bestScore < this.threshold)",
        "    return { tag: 'fallback', score: bestScore };",
        "  return { tag: bestTag, score: bestScore };",
        "}",
    ]
    c.setFillColor(colors.white)
    c.setFont("Courier", 9.2)
    y = code_y + code_h - 1.2 * cm
    for ln in snippet:
        c.drawString(code_x + 0.4 * cm, y, ln)
        y -= 0.42 * cm

    slide_footer(c)


def slide_8_extractors(c):
    slide_header(c, 8, 10, "⑤ NLP — Entity extractors & dialog flow",
                 "Regex-based slot fillers · slot-filling FSM (Lec 02)")

    # Left: list of extractors
    extractors = [
        ("Name",     "extractName(text)",
         "‘my name is X’ regex with conjunction stop  ·  ‘Two Capitalised Words’ fallback"),
        ("Dates",    "extractDates(text)",
         "ISO  ·  d/m/yyyy  ·  ‘May 10 to May 14’  ·  ‘tomorrow for 3 nights’"),
        ("Guests",   "extractGuestCount(text)",
         "digits  +  number-words ('a couple' → 2, 'just me' → 1)"),
        ("Room",     "findRoomType(text)",
         "exact name  +  keyword fallback (deluxe / king / bosphorus)"),
        ("Payment",  "extractPayment(text)",
         "credit card · debit · paypal · pay-at-hotel keywords"),
    ]
    c.setFillColor(colors.HexColor(INK))
    c.setFont("Helvetica-Bold", 11)
    c.drawString(2 * cm, H - 3.3 * cm, "Five extractors fill the slots")
    y = H - 4.0 * cm
    for name, fn, why in extractors:
        c.setFillColor(colors.HexColor(ACCENT_DARK))
        c.setFont("Helvetica-Bold", 10)
        c.drawString(2 * cm, y, name)
        c.setFillColor(colors.HexColor(INK))
        c.setFont("Courier", 9)
        c.drawString(4 * cm, y, fn)
        c.setFillColor(colors.HexColor("#555"))
        c.setFont("Helvetica-Oblique", 8.7)
        c.drawString(2.3 * cm, y - 0.42 * cm, why)
        y -= 1.05 * cm

    # Right: state machine image
    c.drawImage(str(FIG_DIR / "state_machine.png"),
                W / 2 + 0.3 * cm, 2.4 * cm,
                width=(W - 4 * cm) / 2 - 0.3 * cm, height=H - 6.0 * cm,
                preserveAspectRatio=True, anchor="c", mask="auto")
    c.setFillColor(colors.HexColor("#666"))
    c.setFont("Helvetica-Oblique", 8.4)
    c.drawCentredString(W / 2 + 0.3 * cm + ((W - 4 * cm) / 2 - 0.3 * cm) / 2,
                        2.0 * cm,
                        "Conversation flow — slot-filling FSM (8 productive states + final).")

    slide_footer(c)


def slide_9_optimization(c):
    slide_header(c, 9, 10, "⑥ Iterative optimization",
                 "Bugs found, fixed, and locked in with regression tests")

    fixes = [
        ("\"a couple\" was extracted as 1 guest",
         "fixed by reordering the NUMBER_WORDS list so 'couple' wins over 'a'"),
        ("\"I'm Alice and I'd like to stay…\" captured the whole clause",
         "added a conjunction lookahead to the name regex"),
        ("ISO date \"2026-05-14\" was being parsed as 14 guests",
         "gated extractGuestCount() to only fire when current_slot == guests"),
        ("Bare \"yes\" at the confirm step matched breakfast_yes",
         "rewrote the confirm slot with keyword-based yes/no helpers"),
        ("Stale browser cache hid newly-deployed code",
         "added ?v= cache-bust on every asset URL + meta no-cache headers"),
        ("Card form had to cleanly insert between payment and confirm",
         "introduced new payment_card slot; pay-at-hotel skips it"),
        ("Guests on the same device saw each other's receipts",
         "tagged saved booking IDs in sessionStorage; booking.html filters"),
    ]
    y = H - 3.3 * cm
    for problem, fix in fixes:
        c.setFillColor(colors.HexColor(BRASS_DARK))
        c.setFont("Helvetica-Bold", 10)
        c.drawString(2 * cm, y, "✗")
        c.setFillColor(colors.HexColor(INK))
        c.setFont("Helvetica", 10)
        c.drawString(2.5 * cm, y, problem)
        c.setFillColor(colors.HexColor(ACCENT_DARK))
        c.setFont("Helvetica-Bold", 10)
        c.drawString(2 * cm, y - 0.40 * cm, "✓")
        c.setFillColor(colors.HexColor("#444"))
        c.setFont("Helvetica-Oblique", 9.4)
        c.drawString(2.5 * cm, y - 0.40 * cm, fix)
        y -= 1.0 * cm

    # Test growth chart on the right
    c.drawImage(str(FIG_DIR / "test_growth.png"),
                W / 2 + 0.5 * cm, 2.4 * cm,
                width=(W - 4 * cm) / 2 - 0.5 * cm, height=H - 7 * cm,
                preserveAspectRatio=True, anchor="c", mask="auto")

    slide_footer(c)


def slide_10_demo(c):
    slide_header(c, 10, 10, "Live demo & outcome",
                 "Six surfaces of the deployed product — try them online")

    # Big mock image
    c.drawImage(str(FIG_DIR / "ui_mocks.png"),
                1.5 * cm, 4.0 * cm,
                width=W - 3 * cm, height=H - 8 * cm,
                preserveAspectRatio=True, anchor="c", mask="auto")

    # URLs row
    # Use compact display labels but keep the full URL as the link target
    # so nothing gets clipped at the right page margin.
    label_x   = 2 * cm
    url_x     = 5 * cm
    label_x_r = W / 2 + 1 * cm
    url_x_r   = W / 2 + 5 * cm

    items = [
        (label_x,   3.3 * cm, "Try it now:",        "ho11owpoint.github.io/Hotel_Booking_Bot/",
         "https://ho11owpoint.github.io/Hotel_Booking_Bot/"),
        (label_x,   2.7 * cm, "Source code:",       "github.com/Ho11owpoint/Hotel_Booking_Bot",
         "https://github.com/Ho11owpoint/Hotel_Booking_Bot"),
        (label_x_r, 3.3 * cm, "Find your booking:", ".../find.html",
         "https://ho11owpoint.github.io/Hotel_Booking_Bot/find.html"),
        (label_x_r, 2.7 * cm, "CEO admin:",         ".../admin.html",
         "https://ho11owpoint.github.io/Hotel_Booking_Bot/admin.html"),
    ]
    for lx, y, lbl, disp, url in items:
        c.setFillColor(colors.HexColor(INK))
        c.setFont("Helvetica-Bold", 10)
        c.drawString(lx, y, lbl)
        ux = url_x if lx == label_x else url_x_r
        hyperlink(c, ux, y, disp, url, size=10)

    slide_footer(c)


# --------------------------------------------------------------------------- #
# Main                                                                        #
# --------------------------------------------------------------------------- #

def build() -> None:
    print("[*] Rendering diagrams ...")
    make_pipeline(FIG_DIR / "pipeline.png")
    make_state_machine(FIG_DIR / "state_machine.png")
    make_test_growth(FIG_DIR / "test_growth.png")
    make_ui_mocks(FIG_DIR / "ui_mocks.png")

    print("[*] Building PDF ...")
    c = canvas.Canvas(str(OUT_PATH), pagesize=PAGE)
    c.setTitle("Phase 2 — Development · Hotel Booking Chatbot · Birol Hotel")
    c.setAuthor("Egemen Birol")

    slide_1_title(c);       c.showPage()
    slide_2_objectives(c);  c.showPage()
    slide_3_frameworks(c);  c.showPage()
    slide_4_components(c);  c.showPage()
    slide_5_comments(c);    c.showPage()
    slide_6_training_data(c); c.showPage()
    slide_7_classifier(c);  c.showPage()
    slide_8_extractors(c);  c.showPage()
    slide_9_optimization(c); c.showPage()
    slide_10_demo(c);       c.showPage()

    c.save()
    print(f"[OK] {OUT_PATH}  ({OUT_PATH.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    build()
