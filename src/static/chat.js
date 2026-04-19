// Birol Hotel — chat client + calendar range picker
// ---------------------------------------------------
// * Renders chat bubbles with light markdown (**bold**, *italic*).
// * When the bot's dialog state enters the 'dates' slot, an inline
//   calendar pops up. Unavailable dates (from /api/availability) are
//   rendered as 'full' and cannot be picked.
// * The user picks a check-in, then a check-out; on confirm, the range
//   is serialised as 'YYYY-MM-DD to YYYY-MM-DD' and sent as their turn.

const messages   = document.getElementById("messages");
const form       = document.getElementById("chatForm");
const input      = document.getElementById("input");
const sendBtn    = form.querySelector("button[type=submit]");
const resetBtn   = document.getElementById("resetBtn");
const calSlot    = document.getElementById("calendarSlot");

let unavailable = new Set();

// -------------------- Markdown + bubbles -------------------- //
function renderMarkdown(text) {
  const escaped = text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
  return escaped
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*(.+?)\*/g, "<em>$1</em>")
    .replace(/\n/g, "<br>");
}

function addMessage(role, text) {
  const wrap = document.createElement("div");
  wrap.className = `msg ${role}`;
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.innerHTML = renderMarkdown(text);
  wrap.appendChild(bubble);
  messages.appendChild(wrap);
  messages.scrollTop = messages.scrollHeight;
}

function showTyping() {
  const wrap = document.createElement("div");
  wrap.className = "msg bot typing";
  wrap.id = "typing";
  wrap.innerHTML =
    '<div class="bubble"><span class="dot"></span><span class="dot"></span><span class="dot"></span></div>';
  messages.appendChild(wrap);
  messages.scrollTop = messages.scrollHeight;
}
function hideTyping() {
  const el = document.getElementById("typing");
  if (el) el.remove();
}

// -------------------- Chat turn -------------------- //
async function sendMessage(text) {
  addMessage("user", text);
  sendBtn.disabled = true;
  input.disabled = true;
  showTyping();
  try {
    const res = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text }),
    });
    const data = await res.json();
    hideTyping();
    await new Promise(r => setTimeout(r, 180));
    addMessage("bot", data.reply);
    // React to dialog state changes.
    if (data.slot === "dates") {
      openCalendar();
    } else {
      closeCalendar();
    }
  } catch (err) {
    hideTyping();
    addMessage("bot", "Sorry — I couldn't reach the server. Please try again.");
    console.error(err);
  } finally {
    sendBtn.disabled = false;
    input.disabled = false;
    input.focus();
  }
}

form.addEventListener("submit", (e) => {
  e.preventDefault();
  const text = input.value.trim();
  if (!text) return;
  input.value = "";
  sendMessage(text);
});

resetBtn.addEventListener("click", async () => {
  const res = await fetch("/reset", { method: "POST" });
  const data = await res.json();
  messages.innerHTML = "";
  addMessage("bot", data.reply);
  closeCalendar();
  input.focus();
});

// -------------------- Availability -------------------- //
async function loadAvailability() {
  try {
    const res = await fetch("/api/availability");
    const data = await res.json();
    unavailable = new Set(data.unavailable || []);
  } catch (e) {
    console.warn("Could not load availability:", e);
  }
}
loadAvailability();

// -------------------- Calendar widget -------------------- //
const MONTHS = ["January","February","March","April","May","June",
                "July","August","September","October","November","December"];
const DAYS   = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"];

let viewMonth;            // first day of the month being shown
let checkIn = null;       // ISO string
let checkOut = null;      // ISO string
let hoverDate = null;     // ISO string, for range preview

function iso(d) { return d.toISOString().slice(0, 10); }

function openCalendar() {
  checkIn = checkOut = hoverDate = null;
  const today = new Date();
  viewMonth = new Date(today.getFullYear(), today.getMonth(), 1);
  renderCalendar();
  calSlot.classList.add("open");
  calSlot.setAttribute("aria-hidden", "false");
  messages.scrollTop = messages.scrollHeight;
}

function closeCalendar() {
  calSlot.classList.remove("open");
  calSlot.setAttribute("aria-hidden", "true");
  calSlot.innerHTML = "";
}

function renderCalendar() {
  const y = viewMonth.getFullYear();
  const m = viewMonth.getMonth();
  const first = new Date(y, m, 1);
  const daysInMonth = new Date(y, m + 1, 0).getDate();
  // 0=Mon start week offset
  const leadOffset = (first.getDay() + 6) % 7;

  const today = new Date();
  today.setHours(0, 0, 0, 0);

  // Header
  const html = [];
  html.push('<div class="cal-panel">');
  html.push('<div class="cal-head">');
  html.push('<button class="cal-nav" data-dir="-1" aria-label="Previous month">‹</button>');
  html.push(`<div class="cal-title">${MONTHS[m]} ${y}</div>`);
  html.push('<button class="cal-nav" data-dir="1" aria-label="Next month">›</button>');
  html.push('</div>');

  html.push('<div class="cal-grid">');
  for (const d of DAYS) html.push(`<div class="cal-dow">${d}</div>`);

  // Leading blanks
  for (let i = 0; i < leadOffset; i++) html.push('<div class="cal-cell empty"></div>');

  for (let day = 1; day <= daysInMonth; day++) {
    const dt = new Date(y, m, day);
    const id = iso(dt);
    const classes = ["cal-cell"];
    let disabled = false;

    if (dt < today) { classes.push("past"); disabled = true; }
    if (unavailable.has(id)) { classes.push("full"); disabled = true; }
    if (id === checkIn) classes.push("checkin");
    if (id === checkOut) classes.push("checkout");

    // Range highlight
    if (checkIn && !checkOut) {
      if (hoverDate && id > checkIn && id <= hoverDate) classes.push("in-range");
    } else if (checkIn && checkOut && id > checkIn && id < checkOut) {
      classes.push("in-range");
    }

    const title = disabled
      ? (unavailable.has(id) ? "Fully booked" : "Past date")
      : id;

    html.push(
      `<button class="${classes.join(" ")}"
         data-date="${id}"
         ${disabled ? "disabled" : ""}
         title="${title}">
         <span class="n">${day}</span>
         ${unavailable.has(id) ? '<span class="mark">full</span>' : ""}
       </button>`
    );
  }
  html.push('</div>');

  // Legend + footer
  html.push('<div class="cal-legend">');
  html.push('<span><i class="sw sw-sel"></i>selected</span>');
  html.push('<span><i class="sw sw-range"></i>in range</span>');
  html.push('<span><i class="sw sw-full"></i>full</span>');
  html.push('</div>');

  html.push('<div class="cal-summary">');
  if (checkIn && checkOut) {
    const nights = Math.round(
      (new Date(checkOut) - new Date(checkIn)) / 86_400_000
    );
    html.push(
      `<span class="sum"><b>${checkIn}</b> → <b>${checkOut}</b> · ${nights} night${nights !== 1 ? "s" : ""}</span>`
    );
  } else if (checkIn) {
    html.push(`<span class="sum">Check-in: <b>${checkIn}</b> — now pick check-out.</span>`);
  } else {
    html.push('<span class="sum">Pick your <b>check-in</b> date.</span>');
  }
  html.push('</div>');

  html.push('<div class="cal-actions">');
  html.push('<button class="cal-btn ghost" data-act="cancel">Cancel</button>');
  html.push(
    `<button class="cal-btn primary" data-act="confirm"
       ${checkIn && checkOut ? "" : "disabled"}>
       Confirm dates
     </button>`
  );
  html.push('</div>');
  html.push('</div>');

  calSlot.innerHTML = html.join("");

  // Wire events
  calSlot.querySelectorAll(".cal-nav").forEach(btn => {
    btn.addEventListener("click", () => {
      const dir = parseInt(btn.dataset.dir, 10);
      viewMonth = new Date(y, m + dir, 1);
      renderCalendar();
    });
  });
  calSlot.querySelectorAll(".cal-cell:not(.empty):not([disabled])").forEach(btn => {
    btn.addEventListener("click", () => pickDate(btn.dataset.date));
    // Lightweight in-place hover preview — no full re-render, so the click
    // event on the same cell isn't lost when the DOM is swapped out.
    btn.addEventListener("mouseenter", () => {
      if (checkIn && !checkOut) {
        hoverDate = btn.dataset.date;
        updateRangeHighlight();
      }
    });
  });
  calSlot.querySelector('[data-act="cancel"]').addEventListener("click", () => {
    closeCalendar();
    addMessage("user", "(cancelled calendar)");
    input.focus();
  });
  const confirmBtn = calSlot.querySelector('[data-act="confirm"]');
  if (confirmBtn) {
    confirmBtn.addEventListener("click", () => {
      if (!(checkIn && checkOut)) return;
      const msg = `${checkIn} to ${checkOut}`;
      closeCalendar();
      sendMessage(msg);
    });
  }
}

/** Toggle .in-range on existing cells without rebuilding the DOM. */
function updateRangeHighlight() {
  if (!(checkIn && !checkOut)) return;
  const lo = checkIn;
  const hi = hoverDate || checkIn;
  calSlot.querySelectorAll(".cal-cell:not(.empty)").forEach(cell => {
    const id = cell.dataset.date;
    if (!id || id === checkIn || id === checkOut) return;
    if (id > lo && id <= hi) cell.classList.add("in-range");
    else cell.classList.remove("in-range");
  });
}

function pickDate(id) {
  // Prevent picking a range that spans a full date.
  if (checkIn && !checkOut) {
    if (id <= checkIn) {
      checkIn = id; hoverDate = null;
      renderCalendar();
      return;
    }
    // Any blocked date between checkIn and id?
    if (rangeCrossesFull(checkIn, id)) {
      // Restart: treat new click as the new check-in.
      checkIn = id;
      checkOut = null;
      renderCalendar();
      return;
    }
    checkOut = id;
    hoverDate = null;
    renderCalendar();
    return;
  }
  // Fresh pick.
  checkIn = id;
  checkOut = null;
  hoverDate = null;
  renderCalendar();
}

function rangeCrossesFull(a, b) {
  const d1 = new Date(a);
  const d2 = new Date(b);
  const step = new Date(d1);
  step.setDate(step.getDate() + 1);
  while (step < d2) {
    if (unavailable.has(iso(step))) return true;
    step.setDate(step.getDate() + 1);
  }
  return false;
}
