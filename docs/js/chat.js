// ============================================================
// Birol Hotel — chat page controller (pure client-side)
// ============================================================
// Boots the JS bot, renders chat bubbles, opens the calendar
// widget when the bot enters the 'dates' slot.
// ============================================================

const messages = document.getElementById("messages");
const form     = document.getElementById("chatForm");
const input    = document.getElementById("input");
const sendBtn  = form.querySelector("button[type=submit]");
const resetBtn = document.getElementById("resetBtn");
const calSlot  = document.getElementById("calendarSlot");

let bot = null;
let unavailable = new Set();

// ---- Init: load intents, instantiate the bot, render greeting ----
async function init() {
  try {
    const res = await fetch("data/intents.json");
    const intents = await res.json();
    bot = new window.BirolBot.HotelBookingBot(intents);
  } catch (err) {
    console.error("Could not load intents:", err);
    addMessage("bot", "Sorry — the assistant couldn't load. Please reload the page.");
    return;
  }
  unavailable = new Set(window.BirolBot.unavailableDates());
  addMessage("bot", bot.greet());
}
init();

// ---- Markdown (subset) + bubbles ----
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

// ---- One chat turn ----
async function sendMessage(text) {
  if (!bot) return;
  addMessage("user", text);
  sendBtn.disabled = true;
  input.disabled = true;
  showTyping();
  await new Promise(r => setTimeout(r, 260));
  try {
    const reply = bot.respond(text);
    hideTyping();
    addMessage("bot", reply);
    if (bot.session.currentSlot === "dates") openCalendar();
    else                                     closeCalendar();
  } catch (err) {
    hideTyping();
    addMessage("bot", "Sorry — something went wrong. Please try again.");
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

resetBtn.addEventListener("click", () => {
  if (!bot) return;
  bot.session.reset();
  messages.innerHTML = "";
  addMessage("bot", bot.greet());
  closeCalendar();
  input.focus();
});

// ----------------------------------------------------------------
// Calendar widget (range picker)
// ----------------------------------------------------------------
const MONTH_NAMES = ["January","February","March","April","May","June",
                     "July","August","September","October","November","December"];
const DAYS = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"];

let viewMonth;
let checkIn = null, checkOut = null, hoverDate = null;

function iso(d) {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const dd = String(d.getDate()).padStart(2, "0");
  return `${y}-${m}-${dd}`;
}

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
  const y = viewMonth.getFullYear(), m = viewMonth.getMonth();
  const first = new Date(y, m, 1);
  const daysInMonth = new Date(y, m + 1, 0).getDate();
  const leadOffset = (first.getDay() + 6) % 7;

  const today = new Date(); today.setHours(0, 0, 0, 0);
  const html = [];
  html.push('<div class="cal-panel">');
  html.push('<div class="cal-head">');
  html.push('<button class="cal-nav" data-dir="-1" aria-label="Previous month">‹</button>');
  html.push(`<div class="cal-title">${MONTH_NAMES[m]} ${y}</div>`);
  html.push('<button class="cal-nav" data-dir="1" aria-label="Next month">›</button>');
  html.push('</div>');

  html.push('<div class="cal-grid">');
  for (const d of DAYS) html.push(`<div class="cal-dow">${d}</div>`);
  for (let i = 0; i < leadOffset; i++) html.push('<div class="cal-cell empty"></div>');

  for (let day = 1; day <= daysInMonth; day++) {
    const dt = new Date(y, m, day);
    const id = iso(dt);
    const classes = ["cal-cell"];
    let disabled = false;
    if (dt < today)               { classes.push("past"); disabled = true; }
    if (unavailable.has(id))      { classes.push("full"); disabled = true; }
    if (id === checkIn)           classes.push("checkin");
    if (id === checkOut)          classes.push("checkout");
    if (checkIn && !checkOut && hoverDate && id > checkIn && id <= hoverDate) classes.push("in-range");
    else if (checkIn && checkOut && id > checkIn && id < checkOut)            classes.push("in-range");

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

  html.push('<div class="cal-legend">');
  html.push('<span><i class="sw sw-sel"></i>selected</span>');
  html.push('<span><i class="sw sw-range"></i>in range</span>');
  html.push('<span><i class="sw sw-full"></i>full</span>');
  html.push('</div>');

  html.push('<div class="cal-summary">');
  if (checkIn && checkOut) {
    const n = Math.round((new Date(checkOut) - new Date(checkIn)) / 86_400_000);
    html.push(`<span class="sum"><b>${checkIn}</b> → <b>${checkOut}</b> · ${n} night${n !== 1 ? "s" : ""}</span>`);
  } else if (checkIn) {
    html.push(`<span class="sum">Check-in: <b>${checkIn}</b> — now pick check-out.</span>`);
  } else {
    html.push('<span class="sum">Pick your <b>check-in</b> date.</span>');
  }
  html.push('</div>');

  html.push('<div class="cal-actions">');
  html.push('<button class="cal-btn ghost" data-act="cancel">Cancel</button>');
  html.push(`<button class="cal-btn primary" data-act="confirm" ${checkIn && checkOut ? "" : "disabled"}>Confirm dates</button>`);
  html.push('</div>');
  html.push('</div>');

  calSlot.innerHTML = html.join("");

  calSlot.querySelectorAll(".cal-nav").forEach(btn => {
    btn.addEventListener("click", () => {
      const dir = parseInt(btn.dataset.dir, 10);
      viewMonth = new Date(y, m + dir, 1);
      renderCalendar();
    });
  });
  calSlot.querySelectorAll(".cal-cell:not(.empty):not([disabled])").forEach(btn => {
    btn.addEventListener("click", () => pickDate(btn.dataset.date));
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

function updateRangeHighlight() {
  if (!(checkIn && !checkOut)) return;
  const lo = checkIn, hi = hoverDate || checkIn;
  calSlot.querySelectorAll(".cal-cell:not(.empty)").forEach(cell => {
    const id = cell.dataset.date;
    if (!id || id === checkIn || id === checkOut) return;
    if (id > lo && id <= hi) cell.classList.add("in-range");
    else                     cell.classList.remove("in-range");
  });
}

function pickDate(id) {
  if (checkIn && !checkOut) {
    if (id <= checkIn) { checkIn = id; hoverDate = null; renderCalendar(); return; }
    if (rangeCrossesFull(checkIn, id)) { checkIn = id; checkOut = null; renderCalendar(); return; }
    checkOut = id; hoverDate = null; renderCalendar(); return;
  }
  checkIn = id; checkOut = null; hoverDate = null; renderCalendar();
}
function rangeCrossesFull(a, b) {
  const d1 = new Date(a), d2 = new Date(b);
  const step = new Date(d1); step.setDate(step.getDate() + 1);
  while (step < d2) {
    if (unavailable.has(iso(step))) return true;
    step.setDate(step.getDate() + 1);
  }
  return false;
}
