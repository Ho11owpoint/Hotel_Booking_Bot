// ============================================================
// Birol Hotel — chatbot (browser-side port of the Python bot)
// ============================================================
// No build step, no backend. Lives happily on GitHub Pages.
// Mirrors src/nlp.py, src/booking.py, src/chatbot.py, src/availability.py.
// ============================================================

const HOTEL_NAME = "Birol Hotel";

// ----------------------------------------------------------------
// 1. Intent classifier — bag-of-words + cosine similarity
// ----------------------------------------------------------------
const STOPWORDS = new Set([
  "a","an","the","to","is","of","for","on","in","at","and","or","with",
  "please","can","could","would","i","my","me","we","our","you","your",
]);

function tokenize(text) {
  return text
    .toLowerCase()
    .replace(/[^a-z0-9\s]/g, " ")
    .split(/\s+/)
    .filter(t => t && !STOPWORDS.has(t));
}

function counter(tokens) {
  const c = new Map();
  for (const t of tokens) c.set(t, (c.get(t) || 0) + 1);
  return c;
}

function cosine(a, b) {
  if (!a.size || !b.size) return 0;
  let dot = 0, na = 0, nb = 0;
  for (const v of a.values()) na += v * v;
  for (const v of b.values()) nb += v * v;
  for (const [k, v] of a) if (b.has(k)) dot += v * b.get(k);
  if (!na || !nb) return 0;
  return dot / (Math.sqrt(na) * Math.sqrt(nb));
}

class IntentClassifier {
  constructor(intents, threshold = 0.35) {
    this.threshold = threshold;
    this.intents = {};
    this.patternVectors = [];
    for (const intent of intents.intents) {
      this.intents[intent.tag] = intent;
      for (const p of intent.patterns) {
        this.patternVectors.push([intent.tag, counter(tokenize(p))]);
      }
    }
  }
  classify(message) {
    const q = counter(tokenize(message));
    let bestTag = "fallback", bestScore = 0;
    for (const [tag, vec] of this.patternVectors) {
      const s = cosine(q, vec);
      if (s > bestScore) { bestTag = tag; bestScore = s; }
    }
    if (bestScore < this.threshold) return { tag: "fallback", score: bestScore };
    return { tag: bestTag, score: bestScore };
  }
  response(tag) { return this.intents[tag].responses[0]; }
}

// ----------------------------------------------------------------
// 2. Entity extraction
// ----------------------------------------------------------------
const MONTHS = {
  jan:1, january:1, feb:2, february:2, mar:3, march:3,
  apr:4, april:4, may:5, jun:6, june:6, jul:7, july:7,
  aug:8, august:8, sep:9, sept:9, september:9, oct:10,
  october:10, nov:11, november:11, dec:12, december:12,
};
// Ordered most-specific-first so "couple" wins over "a".
const NUMBER_WORDS = [
  ["one",1],["two",2],["three",3],["four",4],["five",5],
  ["six",6],["seven",7],["eight",8],["nine",9],["ten",10],
  ["couple",2],["pair",2],["single",1],
  ["a",1],["an",1],
];

function extractName(text) {
  const nameRe = /(?:my name is|i am|i'm|this is|call me|it's|name[:\s]+)\s+([a-z][a-z .'-]*?)(?=\s+(?:and|&|,|but|\.|!|\?|-)\s|\s+(?:i'd|i would|i want|who|that)\b|$)/i;
  const m = text.match(nameRe);
  if (m) return cleanName(m[1]);
  const bareRe = /\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b/;
  const m2 = text.match(bareRe);
  if (m2) return cleanName(m2[1]);
  const stripped = text.trim();
  const parts = stripped.split(/\s+/);
  if (parts.length > 1 && parts.length <= 4 && parts.every(p => /^[a-z]/i.test(p))) {
    return cleanName(stripped);
  }
  return null;
}
function cleanName(raw) {
  const particles = new Set(["de","van","von","der"]);
  return raw
    .trim()
    .replace(/[.,!?]+$/, "")
    .split(/\s+/)
    .map(p => particles.has(p.toLowerCase())
      ? p.toLowerCase()
      : p.charAt(0).toUpperCase() + p.slice(1).toLowerCase())
    .join(" ");
}

function extractGuestCount(text) {
  const low = text.toLowerCase();
  const d = low.match(/\b(\d{1,2})\b/);
  if (d) {
    const n = parseInt(d[1], 10);
    if (n >= 1 && n <= 20) return n;
  }
  for (const [w, v] of NUMBER_WORDS) {
    if (new RegExp(`\\b${w}\\b`).test(low)) return v;
  }
  if (/\bjust me\b|\balone\b|\bmyself\b/.test(low)) return 1;
  return null;
}

function extractPayment(text) {
  const low = text.toLowerCase();
  if (/credit|visa|mastercard|amex/.test(low)) return "Credit card";
  if (/debit/.test(low)) return "Debit card";
  if (/paypal/.test(low)) return "PayPal";
  if (/cash|at the hotel|on arrival|at hotel/.test(low)) return "Pay at hotel";
  return null;
}

function extractDates(text, today = new Date()) {
  const y0 = today.getFullYear();
  today.setHours(0, 0, 0, 0);

  // ISO yyyy-mm-dd
  const isos = [...text.matchAll(/(\d{4}-\d{2}-\d{2})/g)].map(m => m[1]);
  if (isos.length >= 2) {
    const a = new Date(isos[0] + "T00:00:00"), b = new Date(isos[1] + "T00:00:00");
    if (!isNaN(a) && !isNaN(b) && b > a) return [a, b];
  }

  // d/m/yyyy (day-first)
  const nums = [...text.matchAll(/(\d{1,2})[./-](\d{1,2})[./-](\d{2,4})/g)];
  if (nums.length >= 2) {
    const parsed = [];
    for (let i = 0; i < 2; i++) {
      let [, d, m, y] = nums[i];
      const yy = y.length === 2 ? 2000 + parseInt(y, 10) : parseInt(y, 10);
      const dt = new Date(yy, parseInt(m, 10) - 1, parseInt(d, 10));
      if (isNaN(dt)) { parsed.length = 0; break; }
      parsed.push(dt);
    }
    if (parsed.length === 2 && parsed[1] > parsed[0]) return parsed;
  }

  // Month-name ranges
  const monthName = parseMonthNameRange(text, today);
  if (monthName) return monthName;

  // "from tomorrow for N nights"
  const rel = text.toLowerCase().match(/(today|tomorrow|tonight)\b.*?\bfor\s+(\d+)\s+nights?/);
  if (rel) {
    const offset = rel[1] === "tomorrow" ? 1 : 0;
    const start = new Date(today); start.setDate(start.getDate() + offset);
    const end   = new Date(start); end.setDate(end.getDate() + parseInt(rel[2], 10));
    return [start, end];
  }

  if (/next weekend/i.test(text)) {
    const daysUntilSat = ((5 - today.getDay()) + 7) % 7 || 7;
    const start = new Date(today); start.setDate(start.getDate() + daysUntilSat);
    const end   = new Date(start); end.setDate(end.getDate() + 2);
    return [start, end];
  }
  return null;
}

function parseMonthNameRange(text, today) {
  const monthAlt = Object.keys(MONTHS).join("|");
  // "May 10 to May 14"
  const pat1 = new RegExp(
    `\\b(${monthAlt})\\s+(\\d{1,2})(?:\\w{0,2})?\\s*(?:to|until|-|–)\\s*(?:(${monthAlt})\\s+)?(\\d{1,2})(?:\\w{0,2})?\\b`,
    "i"
  );
  let m = text.match(pat1);
  if (m) {
    const mon1 = MONTHS[m[1].toLowerCase()];
    const d1   = parseInt(m[2], 10);
    const mon2 = m[3] ? MONTHS[m[3].toLowerCase()] : mon1;
    const d2   = parseInt(m[4], 10);
    return buildYearly(mon1, d1, mon2, d2, today);
  }
  // "10 May to 14 May"
  const pat2 = new RegExp(
    `\\b(\\d{1,2})(?:\\w{0,2})?\\s+(${monthAlt})\\s*(?:to|until|-|–)\\s*(\\d{1,2})(?:\\w{0,2})?\\s+(${monthAlt})\\b`,
    "i"
  );
  m = text.match(pat2);
  if (m) {
    const d1 = parseInt(m[1], 10), mon1 = MONTHS[m[2].toLowerCase()];
    const d2 = parseInt(m[3], 10), mon2 = MONTHS[m[4].toLowerCase()];
    return buildYearly(mon1, d1, mon2, d2, today);
  }
  return null;
}
function buildYearly(m1, d1, m2, d2, today) {
  let year = today.getFullYear();
  let a = new Date(year, m1 - 1, d1), b = new Date(year, m2 - 1, d2);
  if (a < today) { a = new Date(year + 1, m1 - 1, d1); b = new Date(year + 1, m2 - 1, d2); }
  return b > a ? [a, b] : null;
}

// ----------------------------------------------------------------
// 3. Availability (deterministic; mirrors availability.py)
// ----------------------------------------------------------------
const PEAK_BLOCKS = [
  ["2026-07-10", "2026-07-20"],
  ["2026-08-08", "2026-08-15"],
  ["2026-12-27", "2027-01-03"],
  ["2027-04-22", "2027-04-28"],
];

// Deterministic 0/1 derived from date string (simple hash, stable in JS).
function detBit(iso) {
  let h = 0;
  for (let i = 0; i < iso.length; i++) {
    h = ((h << 5) - h + iso.charCodeAt(i)) | 0;
  }
  return h & 1;
}

function unavailableDates(start = new Date(), horizonDays = 365) {
  start = new Date(start); start.setHours(0, 0, 0, 0);
  const end = new Date(start); end.setDate(end.getDate() + horizonDays);
  const set = new Set();

  for (const [s, e] of PEAK_BLOCKS) {
    const a = new Date(s + "T00:00:00"), b = new Date(e + "T00:00:00");
    const lo = a < start ? start : a;
    const hi = b > end ? end : b;
    for (const d = new Date(lo); d <= hi; d.setDate(d.getDate() + 1)) {
      set.add(isoDate(d));
    }
  }

  for (const d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) {
    if (d.getDay() === 6 && detBit(isoDate(d))) set.add(isoDate(d));
  }

  return [...set].sort();
}

function isoDate(d) {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
}

/**
 * Human-readable availability summary for the concierge chip.
 * Mirrors the peak-block labels from availability.py but generates
 * text that can be printed as a chat bubble.
 */
function availabilityReport() {
  const fmt = iso => {
    const [y, m, d] = iso.split("-").map(Number);
    const monthNames = ["Jan","Feb","Mar","Apr","May","Jun",
                        "Jul","Aug","Sep","Oct","Nov","Dec"];
    return `${monthNames[m - 1]} ${d}`;
  };
  const peaks = [
    ["2026-07-10", "2026-07-20", "Istanbul summer peak"],
    ["2026-08-08", "2026-08-15", "Mid-August peak"],
    ["2026-12-27", "2027-01-03", "Christmas & New Year"],
    ["2027-04-22", "2027-04-28", "Spring holiday"],
  ];
  const today = new Date();
  const blocked = unavailableDates();

  const lines = [];
  lines.push(`**Upcoming availability at ${HOTEL_NAME}**`);
  lines.push("");
  lines.push("We're open most days across the next 12 months. Fully booked:");
  for (const [s, e, label] of peaks) {
    const start = new Date(s + "T00:00:00");
    if (start < today) continue;
    const y = start.getFullYear();
    const en = new Date(e + "T00:00:00");
    const range = y === en.getFullYear()
      ? `${fmt(s)} – ${fmt(e)}, ${y}`
      : `${fmt(s)} ${y} – ${fmt(e)} ${en.getFullYear()}`;
    lines.push(`• ${range} — ${label}`);
  }
  const weekendsFull = blocked.filter(d => {
    const dt = new Date(d + "T00:00:00");
    const inPeak = peaks.some(([s, e]) =>
      dt >= new Date(s + "T00:00:00") && dt <= new Date(e + "T00:00:00"));
    return !inPeak && dt.getDay() === 6;
  }).length;
  lines.push(`• Plus about ${weekendsFull} peak Saturdays scattered across the year`);
  lines.push("");
  lines.push("Pick any other date in the calendar and you're good to go.");
  return lines.join("\n");
}

// ----------------------------------------------------------------
// 4. Booking domain + local store
// ----------------------------------------------------------------
const SLOTS = ["name", "dates", "guests", "breakfast", "payment", "confirm"];
const STORE_KEY = "birol.bookings";

class Booking {
  constructor() {
    this.name = null;
    this.checkin = null;
    this.checkout = null;
    this.guests = null;
    this.breakfast = null;
    this.payment = null;
    this.booking_id = null;
    this.status = "draft";
  }
  nights() {
    if (!(this.checkin && this.checkout)) return 0;
    const a = new Date(this.checkin + "T00:00:00");
    const b = new Date(this.checkout + "T00:00:00");
    return Math.round((b - a) / 86_400_000);
  }
  summary() {
    const bf = this.breakfast ? "included" : "not included";
    return `**Booking summary**
- Guest: ${this.name}
- Check-in: ${this.checkin}
- Check-out: ${this.checkout}
- Nights: ${this.nights()}
- Guests: ${this.guests}
- Breakfast: ${bf}
- Payment: ${this.payment}

Shall I confirm this booking? (yes / no)`;
  }
}

function saveBooking(booking) {
  booking.booking_id = "BH-" + Math.random().toString(16).slice(2, 10).toUpperCase();
  booking.status = "confirmed";
  const all = JSON.parse(localStorage.getItem(STORE_KEY) || "[]");
  all.push({ ...booking });
  localStorage.setItem(STORE_KEY, JSON.stringify(all));
  return booking.booking_id;
}

class BookingConversation {
  constructor() { this.reset(); }
  reset() {
    this.booking = new Booking();
    this.currentSlot = "greet";
    this.fallbackCount = 0;
  }
  nextMissingSlot() {
    const b = this.booking;
    if (!b.name) return "name";
    if (!(b.checkin && b.checkout)) return "dates";
    if (!b.guests) return "guests";
    if (b.breakfast === null) return "breakfast";
    if (!b.payment) return "payment";
    return "confirm";
  }
}

// ----------------------------------------------------------------
// 5. Dialog manager
// ----------------------------------------------------------------
const YES_WORDS = ["yes","yeah","yep","yup","sure","ok","okay","correct",
                   "confirm","proceed","please do","book it","go ahead",
                   "affirmative","of course","absolutely"];
const NO_WORDS  = ["no","nope","nah","cancel","stop","restart","start over",
                   "wrong","incorrect","negative"];

function isAffirmative(msg, intent) {
  if (intent === "confirm_yes") return true;
  const low = msg.toLowerCase().trim().replace(/[.,!?]+$/, "");
  return YES_WORDS.some(w => low === w || low.startsWith(w + " ") || ` ${low} `.includes(` ${w} `));
}
function isNegative(msg, intent) {
  if (intent === "confirm_no") return true;
  const low = msg.toLowerCase().trim().replace(/[.,!?]+$/, "");
  return NO_WORDS.some(w => low === w || low.startsWith(w + " ") || ` ${low} `.includes(` ${w} `));
}

class HotelBookingBot {
  constructor(intents) {
    this.classifier = new IntentClassifier(intents);
    this.session = new BookingConversation();
  }

  // Standard quick-reply chips shown after the greeting and any return
  // to the 'greet' state. Keeps the UI guided and premium-feeling.
  greetActions() {
    return [
      { label: "Book a room",                         send: "book a room" },
      { label: "Information about room availability", send: "show availability" },
    ];
  }

  greet() {
    return {
      reply:
        `Hello! Welcome to ${HOTEL_NAME}. I'm Aria, your booking concierge. ` +
        "How may I help you today?",
      actions: this.greetActions(),
    };
  }

  /**
   * Produce the bot's next reply.
   *
   * @returns {{reply: string, actions?: Array<{label:string, send?:string, href?:string}>}}
   */
  respond(message) {
    message = (message || "").trim();
    if (!message) return { reply: "I didn't catch that — could you say it again?" };

    const { tag: intent } = this.classifier.classify(message);

    // --- Transversal intents ---
    if (intent === "goodbye") {
      this.session.reset();
      return {
        reply: `Thank you for choosing ${HOTEL_NAME}. Safe travels!`,
        actions: this.greetActions(),
      };
    }
    if (intent === "help") {
      return { reply: this.classifier.response("help"), actions: this.greetActions() };
    }
    if (intent === "thanks") {
      return { reply: this.classifier.response("thanks") };
    }

    // --- Availability summary (only useful outside an active booking) ---
    if (intent === "availability_info" && this.session.currentSlot === "greet") {
      return { reply: availabilityReport(), actions: this.greetActions() };
    }

    // --- Confirm slot: keyword-based yes/no, not tag-based ---
    if (this.session.currentSlot === "confirm") {
      if (isAffirmative(message, intent)) {
        const snapshot = { ...this.session.booking };
        const id = saveBooking(snapshot);
        const ci = snapshot.checkin;
        this.session.reset();
        return {
          reply:
            `Your booking is **confirmed**!
Reference number: **${id}**

We look forward to welcoming you to ${HOTEL_NAME} on ${ci}. ` +
            "Anything else I can help with?",
          actions: [
            { label: "See my booking", href: `booking.html?id=${id}` },
            { label: "Book another",   send: "book a room" },
          ],
        };
      }
      if (isNegative(message, intent)) {
        this.session.reset();
        return { reply: "No problem — let's start again. May I have your name, please?" };
      }
      this.session.fallbackCount++;
      if (this.session.fallbackCount >= 3) {
        this.session.reset();
        return {
          reply: "I'm having trouble understanding. Let's start fresh.",
          actions: this.greetActions(),
        };
      }
      return { reply: this.fallbackHint() };
    }

    // --- Greet / first contact ---
    if (this.session.currentSlot === "greet") {
      if (intent === "greet" || intent === "book_room") {
        this.session.currentSlot = "name";
        return {
          reply: `Lovely — let's book your stay at ${HOTEL_NAME}. May I have your **full name**, please?`,
        };
      }
      if (this.tryFillSlotFromMessage(message)) {
        return { reply: this.promptForNextSlot() };
      }
      return this.greet();
    }

    // --- Inside the booking: try to extract ---
    if (this.tryFillSlotFromMessage(message)) {
      this.session.fallbackCount = 0;
      return { reply: this.promptForNextSlot() };
    }

    this.session.fallbackCount++;
    if (this.session.fallbackCount >= 3) {
      this.session.reset();
      return {
        reply: "I'm having trouble understanding. Let's start fresh.",
        actions: this.greetActions(),
      };
    }
    return { reply: this.fallbackHint() };
  }

  tryFillSlotFromMessage(message) {
    const b = this.session.booking;
    let filled = false;

    if (!b.name) {
      const n = extractName(message);
      if (n) { b.name = n; filled = true; }
    }
    if (!(b.checkin && b.checkout)) {
      const range = extractDates(message);
      if (range) {
        b.checkin  = isoDate(range[0]);
        b.checkout = isoDate(range[1]);
        filled = true;
      }
    }
    if (!b.guests && this.session.currentSlot === "guests") {
      const g = extractGuestCount(message);
      if (g) { b.guests = g; filled = true; }
    }
    if (b.breakfast === null && this.session.currentSlot === "breakfast") {
      const low = message.toLowerCase();
      if (/\b(yes|sure|yeah|yep|please|include|with)\b/.test(low)) {
        b.breakfast = true; filled = true;
      } else if (/\b(no|nope|nah|without|skip|room only)\b/.test(low)) {
        b.breakfast = false; filled = true;
      }
    }
    if (!b.payment && (this.session.currentSlot === "payment" || this.session.currentSlot === "breakfast")) {
      const p = extractPayment(message);
      if (p) { b.payment = p; filled = true; }
    }
    return filled;
  }

  promptForNextSlot() {
    const nxt = this.session.nextMissingSlot();
    this.session.currentSlot = nxt;
    const b = this.session.booking;
    switch (nxt) {
      case "name": return "May I have your **full name**, please?";
      case "dates":
        return `Thank you, **${b.name}**! When would you like to stay with us? ` +
               "Please share your **check-in and check-out dates** " +
               "(e.g. *2026-05-10 to 2026-05-14*).";
      case "guests":
        return `Got it — ${b.checkin} to ${b.checkout} (${b.nights()} night` +
               `${b.nights() !== 1 ? "s" : ""}). **How many guests** will be staying?`;
      case "breakfast":
        return `Noted — ${b.guests} guest${b.guests !== 1 ? "s" : ""}. ` +
               "Would you like to **include breakfast**? (yes / no)";
      case "payment":
        return "How would you like to pay: **credit card**, **debit card**, or **pay at the hotel**?";
      case "confirm": return b.summary();
    }
    return "Let me know how I can help further.";
  }

  fallbackHint() {
    const hints = {
      name:      "Sorry, I didn't get that. Could you share your full name?",
      dates:     "I couldn't parse the dates. Please try e.g. *2026-05-10 to 2026-05-14*.",
      guests:    "Could you tell me the number of guests as a digit (e.g. *2*)?",
      breakfast: "Would you like breakfast? Please answer *yes* or *no*.",
      payment:   "Please choose: credit card, debit card, or pay at the hotel.",
      confirm:   "Shall I confirm the booking? Please answer *yes* or *no*.",
    };
    return hints[this.session.currentSlot] || this.classifier.response("fallback");
  }
}

// Expose
window.BirolBot = {
  HotelBookingBot,
  unavailableDates,
  HOTEL_NAME,
  getBookings: () => JSON.parse(localStorage.getItem(STORE_KEY) || "[]"),
  getBooking: (id) => {
    const all = JSON.parse(localStorage.getItem(STORE_KEY) || "[]");
    return all.find(b => b.booking_id === id) || null;
  },
};
