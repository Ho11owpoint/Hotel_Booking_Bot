// Birol Hotel — Find your booking
//
// User enters their reference number → we look it up across all
// confirmed bookings on this device and render the receipt inline.
// Soft-token model: the random 8-char hex ID is the access key.

(function () {
  const form    = document.getElementById("findForm");
  const input   = document.getElementById("refInput");
  const errEl   = document.getElementById("findError");
  const result  = document.getElementById("result");

  // If the page was opened with ?ref=BH-XXXX, prefill + auto-submit.
  const params = new URLSearchParams(location.search);
  const initial = params.get("ref") || params.get("id") || "";
  if (initial) {
    input.value = stripPrefix(initial);
    submit();
  }

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    submit();
  });

  function submit() {
    errEl.textContent = "";
    result.innerHTML = "";

    const raw = (input.value || "").trim().toUpperCase();
    if (!raw) {
      shake();
      errEl.textContent = "Please enter your booking reference.";
      return;
    }
    // Accept both "BH-XXXX" and bare "XXXX" forms — we always
    // lookup against the canonical "BH-XXXX".
    const id = raw.startsWith("BH-") ? raw : `BH-${raw}`;

    const booking = window.BirolBot.getBooking(id);
    if (!booking) {
      shake();
      errEl.textContent = "No booking found with that reference. Please double-check and try again.";
      result.innerHTML = "";
      return;
    }

    result.innerHTML = renderCard(booking);

    // Wire copy button
    const copyBtn = result.querySelector("[data-copy]");
    if (copyBtn) {
      copyBtn.addEventListener("click", async () => {
        try {
          await navigator.clipboard.writeText(copyBtn.dataset.copy);
          copyBtn.classList.add("copied");
          copyBtn.textContent = "Copied ✓";
          setTimeout(() => {
            copyBtn.classList.remove("copied");
            copyBtn.textContent = "Copy reference";
          }, 1400);
        } catch { /* clipboard unavailable */ }
      });
    }
    // Smooth-scroll to the result
    result.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function shake() {
    input.classList.remove("shake");
    void input.offsetWidth;
    input.classList.add("shake");
  }

  function stripPrefix(s) {
    return s.replace(/^bh-/i, "");
  }

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

  function fmt(iso) {
    if (!iso) return "—";
    const d = new Date(iso + "T00:00:00");
    return d.toLocaleDateString(undefined, {
      weekday: "short", year: "numeric", month: "short", day: "numeric",
    });
  }

  function renderCard(b) {
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
      <article id="b-${b.booking_id}" class="card focused">
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
