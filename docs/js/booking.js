// Birol Hotel — booking details page.
// Reads confirmed bookings out of localStorage (via window.BirolBot.getBookings)
// and renders them as premium digital-receipt cards.

(function () {
  const list = document.getElementById("bookingList");
  const bookings = window.BirolBot.getBookings();

  const params = new URLSearchParams(location.search);
  const focusId = params.get("id");

  if (!bookings.length) {
    list.innerHTML = `
      <div class="empty">
        <div class="empty-icon">✦</div>
        <h2>No bookings yet</h2>
        <p>Once you complete a booking it will appear here.</p>
      </div>`;
    return;
  }

  // Newest first.
  bookings.sort((a, b) => (b.booking_id || "").localeCompare(a.booking_id || ""));

  const fmt = iso => {
    if (!iso) return "—";
    const d = new Date(iso + "T00:00:00");
    return d.toLocaleDateString(undefined, {
      weekday: "short", year: "numeric", month: "short", day: "numeric",
    });
  };

  list.innerHTML = bookings.map(b => card(b, b.booking_id === focusId)).join("");

  // Scroll the focused booking into view
  if (focusId) {
    const el = document.getElementById("b-" + focusId);
    if (el) el.scrollIntoView({ behavior: "smooth", block: "center" });
  }

  // Wire up copy-reference buttons
  list.querySelectorAll("[data-copy]").forEach(btn => {
    btn.addEventListener("click", async () => {
      try {
        await navigator.clipboard.writeText(btn.dataset.copy);
        btn.classList.add("copied");
        btn.textContent = "Copied ✓";
        setTimeout(() => {
          btn.classList.remove("copied");
          btn.textContent = "Copy reference";
        }, 1400);
      } catch { /* no clipboard */ }
    });
  });

  function card(b, focused) {
    const nights =
      b.checkin && b.checkout
        ? Math.round(
            (new Date(b.checkout) - new Date(b.checkin)) / 86_400_000
          )
        : 0;
    const bf = b.breakfast ? "Included" : "Not included";
    return `
      <article id="b-${b.booking_id}" class="card ${focused ? "focused" : ""}">
        <div class="card-top">
          <div class="status">
            <span class="dot"></span>
            ${b.status === "confirmed" ? "Confirmed" : b.status}
          </div>
          <div class="ref">
            <span class="ref-label">Reference</span>
            <span class="ref-id">${b.booking_id}</span>
          </div>
        </div>

        <div class="card-hero">
          <p class="eyebrow">Birol Hotel · Istanbul</p>
          <h2>${b.name || "Guest"}</h2>
          <p class="stay">
            <b>${fmt(b.checkin)}</b>
            <span class="arrow">→</span>
            <b>${fmt(b.checkout)}</b>
          </p>
          <p class="nights">${nights} night${nights !== 1 ? "s" : ""} · ${b.guests} guest${b.guests !== 1 ? "s" : ""}</p>
        </div>

        <dl class="details">
          <div><dt>Check-in</dt><dd>${fmt(b.checkin)}</dd></div>
          <div><dt>Check-out</dt><dd>${fmt(b.checkout)}</dd></div>
          <div><dt>Guests</dt><dd>${b.guests}</dd></div>
          <div><dt>Breakfast</dt><dd>${bf}</dd></div>
          <div><dt>Payment</dt><dd>${b.payment || "—"}</dd></div>
          <div><dt>Status</dt><dd class="status-cell">${b.status}</dd></div>
        </dl>

        <div class="card-actions">
          <button type="button" class="btn-ghost" data-copy="${b.booking_id}">
            Copy reference
          </button>
          <button type="button" class="btn-ghost" onclick="window.print()">
            Print / save PDF
          </button>
        </div>
      </article>
    `;
  }
})();
