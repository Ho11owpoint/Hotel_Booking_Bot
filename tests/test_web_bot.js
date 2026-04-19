// Node regression tests for the browser-side bot (docs/js/bot.js).
// Run:  node tests/test_web_bot.js

const fs = require("fs");
const assert = require("assert");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");

// Stub the browser globals the bot depends on.
global.window = {};
global.localStorage = {
  data: {},
  getItem(k) { return this.data[k] || null; },
  setItem(k, v) { this.data[k] = v; },
  removeItem(k) { delete this.data[k]; },
};

// Load the real bot source.
eval(fs.readFileSync(path.join(ROOT, "docs/js/bot.js"), "utf8"));

const intents = JSON.parse(
  fs.readFileSync(path.join(ROOT, "docs/data/intents.json"), "utf8")
);

function fresh() {
  global.localStorage.data = {};
  return new window.BirolBot.HotelBookingBot(intents);
}

let passed = 0, failed = 0;
function test(name, fn) {
  try { fn(); console.log("  ✓ " + name); passed++; }
  catch (e) { console.log("  ✗ " + name + "\n      " + e.message); failed++; }
}
function section(s) { console.log("\n" + s); }

// ------------------------------------------------------------------
section("Concierge Q&A (greet slot)");

test("places to visit → mentions Hagia Sophia", () => {
  const bot = fresh();
  const r = bot.respond("what are the best places to visit in istanbul");
  assert(/Hagia Sophia/i.test(r.reply), "reply should mention Hagia Sophia");
});

test("restaurant recommendations → mentions Mikla", () => {
  const bot = fresh();
  const r = bot.respond("where should I eat");
  assert(/Mikla|Karaköy Lokantası|Çiya/i.test(r.reply), "should mention a known restaurant");
});

test("airport transfer → mentions HAVAIST or taxi", () => {
  const bot = fresh();
  const r = bot.respond("how do I get from the airport");
  assert(/HAVAIST|taxi|transfer/i.test(r.reply));
});

test("wifi → mentions network name", () => {
  const bot = fresh();
  const r = bot.respond("wifi password");
  assert(/BirolHotel-Guest|Wi-Fi|wifi/i.test(r.reply));
});

test("breakfast hours → mentions 07:00", () => {
  const bot = fresh();
  const r = bot.respond("what time is breakfast");
  assert(/07[:.]00|7:00/i.test(r.reply));
});

test("check-in time → mentions 2:00 PM", () => {
  const bot = fresh();
  const r = bot.respond("what time is check in");
  assert(/2[:.]00|14:00|2 PM|14/i.test(r.reply));
});

test("pets policy → welcomes pets", () => {
  const bot = fresh();
  const r = bot.respond("can I bring my dog");
  assert(/pet-friendly|welcome/i.test(r.reply));
});

test("amenities → mentions spa or pool", () => {
  const bot = fresh();
  const r = bot.respond("what amenities do you have");
  assert(/spa|pool|hammam|gym/i.test(r.reply));
});

test("cancellation → mentions 48 hours", () => {
  const bot = fresh();
  const r = bot.respond("what is your cancellation policy");
  assert(/48\s*hour|free cancellation/i.test(r.reply));
});

test("emergency → mentions 112", () => {
  const bot = fresh();
  const r = bot.respond("emergency number");
  assert(/112\b/.test(r.reply));
});

// ------------------------------------------------------------------
section("Off-topic → polite refusal + Help chip");

test("sports score → off-topic fallback, Help chip offered", () => {
  const bot = fresh();
  const r = bot.respond("what is the match score of real madrid vs barca");
  assert(/outside|focus|Birol Hotel|Istanbul/i.test(r.reply));
  assert(Array.isArray(r.actions), "should offer fallback actions");
  assert(r.actions.some(a => a.label === "Help"), "should include Help chip");
});

test("random trivia → off-topic fallback", () => {
  const bot = fresh();
  const r = bot.respond("how tall is mount everest");
  assert(/outside|Birol|Istanbul/i.test(r.reply));
});

// ------------------------------------------------------------------
section("Help intent");

test("help → lists capabilities", () => {
  const bot = fresh();
  const r = bot.respond("help");
  assert(/Booking|Istanbul|Aria/i.test(r.reply));
  assert(Array.isArray(r.actions) && r.actions.length >= 3);
});

test("greet chips include Help", () => {
  const bot = fresh();
  const g = bot.greet();
  assert(g.actions.some(a => a.label === "Help"), "greet actions should contain Help");
});

// ------------------------------------------------------------------
section("Concierge during a booking — transversal");

test("question mid-booking is answered, then re-prompts the current slot", () => {
  const bot = fresh();
  bot.respond("book a room");
  bot.respond("Jane Doe");
  bot.respond("2026-05-10 to 2026-05-14");
  // Now bot is on the 'guests' slot. User asks a concierge question.
  const r = bot.respond("where should I eat");
  assert(/Mikla|Karaköy|Çiya/i.test(r.reply), "should still answer the food question");
  assert(/back to your booking/i.test(r.reply), "should nudge back to the slot");
  assert(/How many guests/i.test(r.reply), "should re-prompt for guests");
});

test("booking flow still finishes normally after a mid-flow concierge question", () => {
  const bot = fresh();
  bot.respond("book a room");
  bot.respond("Jane Doe");
  bot.respond("2026-05-10 to 2026-05-14");
  bot.respond("wifi password");   // concierge interlude
  bot.respond("2");
  bot.respond("yes");
  bot.respond("credit card");
  const done = bot.respond("yes");
  assert(/confirmed/i.test(done.reply));
  assert(/BH-/.test(done.reply));
});

// ------------------------------------------------------------------
section("Happy path still passes");

test("book a room → yes", () => {
  const bot = fresh();
  bot.respond("hi");
  bot.respond("Jane Doe");
  bot.respond("2026-05-10 to 2026-05-14");
  bot.respond("2");
  bot.respond("yes");
  bot.respond("credit card");
  const done = bot.respond("yes");
  assert(/confirmed/i.test(done.reply));
  const saved = window.BirolBot.getBookings();
  assert.strictEqual(saved.length, 1);
  assert.strictEqual(saved[0].name, "Jane Doe");
});

// ------------------------------------------------------------------
section("Help / availability chips present on greet");
test("greet actions: 4 chips including Book / Availability / Places / Help", () => {
  const bot = fresh();
  const labels = bot.greet().actions.map(a => a.label);
  for (const must of ["Book a room", "Room availability", "Places to visit", "Help"]) {
    assert(labels.includes(must), `missing chip: ${must}`);
  }
});

// ------------------------------------------------------------------
console.log(`\n${passed} passed, ${failed} failed`);
process.exit(failed > 0 ? 1 : 0);
