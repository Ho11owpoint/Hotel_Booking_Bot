// Birol Hotel — booking details page (guest view).
//
// Visibility model:
//   * If the URL has ?id=BH-XXX, show that specific booking. The id
//     is a 32-bit-ish random token, so it acts as a soft access link
//     for the guest who booked it.
//   * Otherwise, show ONLY the bookings made in this browser session
//     (sessionStorage tag), so guests on a shared device don't see
//     each other's reservations.
// CEO sees everything from /admin.html instead.

(function () {
  const list = document.getElementById("bookingList");
  const params = new URLSearchParams(location.search);
  const focusId = params.get("id");

  let bookings;
  if (focusId) {
    const b = window.BirolBot.getBooking(focusId);
    bookings = b ? [b] : [];
  } else {
    bookings = window.BirolBot.getMyBookings();
  }

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

  if (focusId) {
    const el = document.getElementById("b-" + focusId);
    if (el) el.scrollIntoView({ behavior: "smooth", block: "center" });
  }

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
      } catch { /* clipboard unavailable */ }
    });
  });

  /** Compute total for legacy bookings that don't have total_eur stored. */
  function totalFor(b) {
    if (typeof b.total_eur === "number") return b.total_eur;
    if (!(b.checkin && b.checkout && b.roomRate)) return null;
    const nights = Math.round(
      (new Date(b.checkout) - new Date(b.checkin)) / 86_400_000
    );
    let t = nights * b.roomRate;
    if (b.breakfast) t += (b.guests || 0) * nights * 10;
    return t;
  }

  function card(b, focused) {
    const nights = b.checkin && b.checkout
      ? Math.round((new Date(b.checkout) - new Date(b.checkin)) / 86_400_000)
      : 0;
    const bf = b.breakfast ? "Included" : "Not included";
    const total = totalFor(b);
    const totalLine = total != null
      ? `<div><dt>Total</dt><dd class="total">€${total}</dd></div>`
      : "";
    const roomLine = b.roomType
      ? `<div><dt>Room</dt><dd>${b.roomType}${b.roomRate ? ` · €${b.roomRate}/night` : ""}</dd></div>`
      : "";

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
          ${roomLine}
          <div><dt>Check-in</dt><dd>${fmt(b.checkin)}</dd></div>
          <div><dt>Check-out</dt><dd>${fmt(b.checkout)}</dd></div>
          <div><dt>Guests</dt><dd>${b.guests}</dd></div>
          <div><dt>Breakfast</dt><dd>${bf}</dd></div>
          <div><dt>Payment</dt><dd>${b.payment || "—"}</dd></div>
          ${totalLine}
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
