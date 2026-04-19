// ============================================================
// Birol Hotel — CEO / Admin dashboard
// ============================================================
// Password: "egemen" (client-side gate only — prototype).
// Once in, renders:
//   * High-level stats (bookings / guests / room-nights)
//   * An occupancy calendar overlaying real guest bookings on
//     top of the peak-block availability model
//   * A sortable list of every saved booking
// ============================================================

(function () {
  const PASSWORD    = "egemen";
  const SESSION_KEY = "birol.admin.session";

  const gate        = document.getElementById("gate");
  const gateForm    = document.getElementById("gateForm");
  const pwInput     = document.getElementById("pwInput");
  const gateError   = document.getElementById("gateError");
  const dashboard   = document.getElementById("dashboard");
  const logoutBtn   = document.getElementById("logoutBtn");

  // ---------- Session ----------
  if (sessionStorage.getItem(SESSION_KEY) === "ok") {
    unlock();
  }

  gateForm.addEventListener("submit", (e) => {
    e.preventDefault();
    if (pwInput.value === PASSWORD) {
      sessionStorage.setItem(SESSION_KEY, "ok");
      gateError.textContent = "";
      unlock();
    } else {
      gateError.textContent = "Incorrect password.";
      pwInput.classList.remove("shake");
      // force reflow to restart the animation
      // eslint-disable-next-line no-unused-expressions
      void pwInput.offsetWidth;
      pwInput.classList.add("shake");
      pwInput.select();
    }
  });

  logoutBtn.addEventListener("click", () => {
    sessionStorage.removeItem(SESSION_KEY);
    dashboard.classList.add("hidden");
    logoutBtn.classList.add("hidden");
    gate.classList.remove("hidden");
    pwInput.value = "";
    pwInput.focus();
  });

  function unlock() {
    gate.classList.add("hidden");
    dashboard.classList.remove("hidden");
    logoutBtn.classList.remove("hidden");
    renderAll();
  }

  // ---------- Rendering ----------
  function renderAll() {
    const bookings    = window.BirolBot.getBookings();
    const peakSet     = new Set(window.BirolBot.unavailableDates());
    const { byDate, totalNights } = indexBookings(bookings);

    renderStats(bookings, totalNights);
    renderCalendar(byDate, peakSet);
    renderBookingsList(bookings);
  }

  function indexBookings(bookings) {
    // Map: "yyyy-mm-dd" -> Array<Booking> active that night
    const byDate = new Map();
    let totalNights = 0;
    for (const b of bookings) {
      if (!b.checkin || !b.checkout) continue;
      const start = new Date(b.checkin  + "T00:00:00");
      const end   = new Date(b.checkout + "T00:00:00");
      for (const d = new Date(start); d < end; d.setDate(d.getDate() + 1)) {
        const iso = isoDate(d);
        if (!byDate.has(iso)) byDate.set(iso, []);
        byDate.get(iso).push(b);
        totalNights++;
      }
    }
    return { byDate, totalNights };
  }

  function renderStats(bookings, totalNights) {
    const guests = bookings.reduce((s, b) => s + (b.guests || 0), 0);
    document.getElementById("statTotal").textContent  = bookings.length;
    document.getElementById("statGuests").textContent = guests;
    document.getElementById("statNights").textContent = totalNights;
  }

  // ---------- Calendar ----------
  const MONTH_NAMES = [
    "January","February","March","April","May","June",
    "July","August","September","October","November","December",
  ];
  const DAYS = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"];

  // State for the admin calendar
  let viewMonth = (() => {
    const t = new Date();
    return new Date(t.getFullYear(), t.getMonth(), 1);
  })();

  function renderCalendar(byDate, peakSet) {
    const host = document.getElementById("calendar");
    const y = viewMonth.getFullYear(), m = viewMonth.getMonth();
    const first = new Date(y, m, 1);
    const daysInMonth = new Date(y, m + 1, 0).getDate();
    const leadOffset  = (first.getDay() + 6) % 7;

    const today = new Date(); today.setHours(0, 0, 0, 0);

    const html = [];
    html.push('<div class="cal-head">');
    html.push('<button class="cal-nav" data-dir="-1" aria-label="Previous month">‹</button>');
    html.push(`<div class="cal-title">${MONTH_NAMES[m]} ${y}</div>`);
    html.push('<button class="cal-nav" data-dir="1" aria-label="Next month">›</button>');
    html.push('</div>');

    html.push('<div class="cal-grid">');
    for (const d of DAYS) html.push(`<div class="cal-dow">${d}</div>`);
    for (let i = 0; i < leadOffset; i++) html.push('<div class="cal-cell empty"></div>');

    for (let day = 1; day <= daysInMonth; day++) {
      const dt  = new Date(y, m, day);
      const iso = isoDate(dt);
      const classes = ["cal-cell"];
      let mark = "";
      let badge = "";
      let tip = "";

      if (dt < today) classes.push("past");

      const bs = byDate.get(iso) || [];
      if (bs.length) {
        classes.push("guest");
        badge = `<span class="badge">${bs.length}</span>`;
        const lines = bs.map(b => `${b.name} (${b.guests}g) · ${b.booking_id}`);
        tip = `${iso}\n${lines.join("\n")}`;
      } else if (peakSet.has(iso)) {
        classes.push("peak");
        mark = '<span class="mark">full</span>';
      }

      html.push(
        `<div class="${classes.join(" ")}"
              ${tip ? `data-tip="${tip.replace(/"/g, "&quot;")}" tabindex="0"` : ""}>
           <span class="n">${day}</span>
           ${badge}${mark}
         </div>`
      );
    }
    html.push('</div>');

    host.innerHTML = html.join("");
    host.querySelectorAll(".cal-nav").forEach(btn => {
      btn.addEventListener("click", () => {
        const dir = parseInt(btn.dataset.dir, 10);
        viewMonth = new Date(y, m + dir, 1);
        renderCalendar(byDate, peakSet);
      });
    });
  }

  // ---------- Bookings list ----------
  function renderBookingsList(bookings) {
    const list  = document.getElementById("bookingsList");
    const count = document.getElementById("bookingsCount");

    if (!bookings.length) {
      count.textContent = "";
      list.innerHTML = `
        <div class="empty-panel">
          No bookings yet.
          <small>Bookings made on this device will appear here.</small>
        </div>`;
      return;
    }

    // Most recent first (booking IDs are random, so fall back to chronological by checkin)
    bookings.sort((a, b) => (b.checkin || "").localeCompare(a.checkin || ""));

    count.textContent = `${bookings.length} total`;

    list.innerHTML = bookings.map(b => {
      const initials = (b.name || "?")
        .split(/\s+/).slice(0, 2).map(s => s[0] || "").join("").toUpperCase();
      const meta = [
        `${fmt(b.checkin)} → ${fmt(b.checkout)}`,
        `${b.guests}g`,
        b.breakfast ? "☕" : "",
        b.payment || "",
      ].filter(Boolean).join(" · ");
      return `
        <a class="booking-row" href="booking.html?id=${b.booking_id}">
          <div class="avatar">${initials}</div>
          <div>
            <div class="name">${escapeHtml(b.name || "Guest")}</div>
            <div class="meta">${escapeHtml(meta)}</div>
          </div>
          <div class="ref">${b.booking_id}</div>
        </a>
      `;
    }).join("");
  }

  // ---------- Helpers ----------
  function isoDate(d) {
    const y  = d.getFullYear();
    const m  = String(d.getMonth() + 1).padStart(2, "0");
    const dd = String(d.getDate()).padStart(2, "0");
    return `${y}-${m}-${dd}`;
  }
  function fmt(iso) {
    if (!iso) return "—";
    const d = new Date(iso + "T00:00:00");
    return d.toLocaleDateString(undefined, {
      month: "short", day: "numeric",
    });
  }
  function escapeHtml(s) {
    return (s || "").replace(/[&<>"']/g, c => ({
      "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;",
    }[c]));
  }
})();
