// Node regression tests for the browser-side bot (docs/js/bot.js).
// Run:  node tests/test_web_bot.js

const fs = require("fs");
const assert = require("assert");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");

// Stub the browser globals the bot depends on.
global.window = {};
function makeStorage() {
  return {
    data: {},
    getItem(k) { return this.data[k] || null; },
    setItem(k, v) { this.data[k] = v; },
    removeItem(k) { delete this.data[k]; },
  };
}
global.localStorage   = makeStorage();
global.sessionStorage = makeStorage();

// Load the real bot source.
eval(fs.readFileSync(path.join(ROOT, "docs/js/bot.js"), "utf8"));

const intents = JSON.parse(
  fs.readFileSync(path.join(ROOT, "docs/data/intents.json"), "utf8")
);

function fresh() {
  global.localStorage.data   = {};
  global.sessionStorage.data = {};
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
  // Now bot is on the 'room_type' slot.
  const r = bot.respond("where should I eat");
  assert(/Mikla|Karaköy|Çiya/i.test(r.reply), "should still answer the food question");
  assert(/back to your booking/i.test(r.reply), "should nudge back to the slot");
  assert(/Which room type/i.test(r.reply), "should re-prompt for room");
});

test("booking flow still finishes normally after a mid-flow concierge question", () => {
  const bot = fresh();
  bot.respond("book a room");
  bot.respond("Jane Doe");
  bot.respond("2026-05-10 to 2026-05-14");
  bot.respond("wifi password");   // concierge interlude
  bot.respond("Deluxe Room");
  bot.respond("2");
  bot.respond("yes");
  bot.respond("credit card");
  bot.respond("pay");             // card form Pay click
  const done = bot.respond("yes");
  assert(/confirmed/i.test(done.reply));
  assert(/BH-/.test(done.reply));
});

// ------------------------------------------------------------------
section("Happy path with the new room_type slot");

test("book a room → Deluxe → card → pay → yes; total = €800", () => {
  const bot = fresh();
  bot.respond("hi");
  bot.respond("Jane Doe");
  bot.respond("2026-05-10 to 2026-05-14");

  // Room slot — fallback hint when an unmatched word is given
  const roomPrompt = bot.respond("hello");
  assert(/room/i.test(roomPrompt.reply || ""), "should still ask for a room");

  bot.respond("Deluxe Room");
  bot.respond("2");
  bot.respond("yes");                  // breakfast
  bot.respond("credit card");          // payment slot

  // Now in the new payment_card slot — summary is NOT yet shown.
  assert.strictEqual(bot.session.currentSlot, "payment_card");

  bot.respond("pay");                  // simulates the card-form Pay button
  // Now in confirm slot, summary visible
  assert.strictEqual(bot.session.currentSlot, "confirm");

  const done = bot.respond("yes");
  assert(/confirmed/i.test(done.reply));

  const saved = window.BirolBot.getBookings();
  assert.strictEqual(saved.length, 1);
  const b = saved[0];
  assert.strictEqual(b.name,     "Jane Doe");
  assert.strictEqual(b.roomType, "Deluxe Room");
  assert.strictEqual(b.roomRate, 180);
  assert.strictEqual(b.total_eur, 800);
  assert.strictEqual(b.paymentConfirmed, true);
});

// ------------------------------------------------------------------
section("Room types & pricing");

test("ROOM_TYPES catalogue is exposed", () => {
  const cat = window.BirolBot.ROOM_TYPES;
  assert(Array.isArray(cat) && cat.length === 4);
  const ids = cat.map(r => r.id).sort();
  assert.deepStrictEqual(ids,
    ["bosphorus_suite","deluxe","king_suite","standard"]);
});

test("BREAKFAST surcharge is exposed at €10", () => {
  assert.strictEqual(window.BirolBot.BREAKFAST_PER_GUEST_PER_NIGHT, 10);
});

test("Bosphorus suite, no breakfast, debit card: 3×420 = €1260", () => {
  const bot = fresh();
  bot.respond("book a room");
  bot.respond("Alice Wong");
  bot.respond("2026-06-05 to 2026-06-08");   // 3 nights
  bot.respond("Bosphorus Suite");
  bot.respond("1");
  bot.respond("no");                          // no breakfast
  bot.respond("debit card");                  // → payment_card
  bot.respond("pay");                         // card form Pay click
  bot.respond("yes");                         // confirm summary
  const b = window.BirolBot.getBookings()[0];
  assert.strictEqual(b.roomType, "Bosphorus Suite");
  assert.strictEqual(b.roomRate, 420);
  assert.strictEqual(b.breakfast, false);
  assert.strictEqual(b.total_eur, 1260);
  assert.strictEqual(b.paymentConfirmed, true);
});

test("room slot prompt offers chips for all 4 room types", () => {
  const bot = fresh();
  bot.respond("book a room");
  bot.respond("Test Guest");
  const r = bot.respond("2026-05-10 to 2026-05-14");
  assert(Array.isArray(r.actions), "should have action chips");
  assert.strictEqual(r.actions.length, 4);
  for (const expected of ["Standard Room","Deluxe Room","King Suite","Bosphorus Suite"]) {
    assert(r.actions.some(a => a.send === expected),
           "missing chip for " + expected);
  }
});

test("breakfast prompt mentions the €10/guest/night charge", () => {
  const bot = fresh();
  bot.respond("book a room");
  bot.respond("Test Guest");
  bot.respond("2026-05-10 to 2026-05-14");
  bot.respond("Standard Room");
  const r = bot.respond("2");
  assert(/€10/.test(r.reply), "breakfast prompt must mention €10");
  assert(/per guest per night/i.test(r.reply));
});

test("breakfast prompt offers yes/no chips", () => {
  const bot = fresh();
  bot.respond("book a room");
  bot.respond("Test Guest");
  bot.respond("2026-05-10 to 2026-05-14");
  bot.respond("Standard Room");
  const r = bot.respond("2");
  const labels = (r.actions || []).map(a => a.label);
  assert(labels.some(l => /include breakfast/i.test(l)));
  assert(labels.some(l => /no breakfast/i.test(l)));
});

test("payment prompt offers all three payment chips", () => {
  const bot = fresh();
  bot.respond("book a room");
  bot.respond("Test Guest");
  bot.respond("2026-05-10 to 2026-05-14");
  bot.respond("Standard Room");
  bot.respond("2");
  const r = bot.respond("yes");
  const labels = (r.actions || []).map(a => a.label);
  assert.deepStrictEqual(labels.sort(),
    ["Credit card", "Debit card", "Pay at hotel"]);
});

test("confirm summary (after card Pay) shows the **Total** line", () => {
  const bot = fresh();
  bot.respond("book a room");
  bot.respond("Jane Doe");
  bot.respond("2026-05-10 to 2026-05-14");
  bot.respond("Deluxe Room");
  bot.respond("2");
  bot.respond("yes");
  bot.respond("credit card");                // → payment_card
  const r = bot.respond("pay");              // → confirm prompt
  assert(/\*\*Total: €800\*\*/.test(r.reply),
         "summary should include **Total: €800** line");
  assert(/Pricing/i.test(r.reply), "summary should have a Pricing block");
});

// ------------------------------------------------------------------
section("Receipt isolation (per-session)");

test("getMyBookings returns only bookings made in this session", () => {
  const bot = fresh();
  bot.respond("book a room");
  bot.respond("Jane Doe");
  bot.respond("2026-05-10 to 2026-05-14");
  bot.respond("Deluxe Room");
  bot.respond("2");
  bot.respond("yes");
  bot.respond("credit card");
  bot.respond("pay");
  bot.respond("yes");

  // Now simulate "another guest" by clearing sessionStorage but
  // keeping localStorage (i.e. their booking is still on the device,
  // but their session is gone).
  global.sessionStorage.data = {};

  const allOnDevice = window.BirolBot.getBookings();
  assert.strictEqual(allOnDevice.length, 1, "device knows about it");

  const minOnly = window.BirolBot.getMyBookings();
  assert.strictEqual(minOnly.length, 0, "but I shouldn't see it any more");
});

test("getMyBookings returns my booking inside the same session", () => {
  const bot = fresh();
  bot.respond("book a room");
  bot.respond("Jane Doe");
  bot.respond("2026-05-10 to 2026-05-14");
  bot.respond("Deluxe Room");
  bot.respond("2");
  bot.respond("yes");
  bot.respond("credit card");
  bot.respond("pay");
  bot.respond("yes");

  const mine = window.BirolBot.getMyBookings();
  assert.strictEqual(mine.length, 1);
  assert.strictEqual(mine[0].name, "Jane Doe");
});

// ------------------------------------------------------------------
section("Card payment flow");

test("Selecting credit card moves to payment_card, NOT confirm", () => {
  const bot = fresh();
  bot.respond("book a room");
  bot.respond("Test Guest");
  bot.respond("2026-05-10 to 2026-05-14");
  bot.respond("Standard Room");
  bot.respond("2");
  bot.respond("yes");
  const r = bot.respond("credit card");
  assert.strictEqual(bot.session.currentSlot, "payment_card");
  assert(/pre-filled/i.test(r.reply), "should mention pre-filled card");
  assert(/Pay/.test(r.reply));
});

test("Pay-at-hotel SKIPS the card form (straight to confirm)", () => {
  const bot = fresh();
  bot.respond("book a room");
  bot.respond("Test Guest");
  bot.respond("2026-05-10 to 2026-05-14");
  bot.respond("Standard Room");
  bot.respond("2");
  bot.respond("yes");
  const r = bot.respond("pay at hotel");
  assert.strictEqual(bot.session.currentSlot, "confirm");
  assert(/Booking summary/i.test(r.reply));
  assert(/Total/i.test(r.reply));
});

test("'pay' message at payment_card slot advances to confirm", () => {
  const bot = fresh();
  bot.respond("book a room");
  bot.respond("Test Guest");
  bot.respond("2026-05-10 to 2026-05-14");
  bot.respond("Standard Room");
  bot.respond("2");
  bot.respond("yes");
  bot.respond("credit card");
  assert.strictEqual(bot.session.currentSlot, "payment_card");
  bot.respond("pay");
  assert.strictEqual(bot.session.currentSlot, "confirm");
  assert.strictEqual(bot.session.booking.paymentConfirmed, true);
});

test("Without 'pay', confirm is unreachable from payment_card", () => {
  const bot = fresh();
  bot.respond("book a room");
  bot.respond("Test Guest");
  bot.respond("2026-05-10 to 2026-05-14");
  bot.respond("Standard Room");
  bot.respond("2");
  bot.respond("yes");
  bot.respond("credit card");
  // 'yes' here should NOT save the booking (we haven't paid)
  bot.respond("yes");
  assert.strictEqual(window.BirolBot.getBookings().length, 0);
});

// ------------------------------------------------------------------
section("Find by reference (getBooking)");

test("getBooking with valid id returns the booking", () => {
  const bot = fresh();
  bot.respond("book a room");
  bot.respond("Egemen Birol");
  bot.respond("2026-05-10 to 2026-05-14");
  bot.respond("Deluxe Room");
  bot.respond("2");
  bot.respond("yes");
  bot.respond("credit card");
  bot.respond("pay");
  bot.respond("yes");
  const id = window.BirolBot.getBookings()[0].booking_id;
  const found = window.BirolBot.getBooking(id);
  assert(found, "should find by id");
  assert.strictEqual(found.name, "Egemen Birol");
});

test("getBooking with bad id returns null (no error thrown)", () => {
  const found = window.BirolBot.getBooking("BH-NOPE9999");
  assert.strictEqual(found, null);
});

// ------------------------------------------------------------------
section("Concierge: room types intent");

test("'what rooms do you have' → mentions all 4 tiers", () => {
  const bot = fresh();
  const r = bot.respond("what rooms do you have");
  assert(/Standard/i.test(r.reply));
  assert(/Deluxe/i.test(r.reply));
  assert(/King Suite/i.test(r.reply));
  assert(/Bosphorus Suite/i.test(r.reply));
  assert(/€120/.test(r.reply));
  assert(/€420/.test(r.reply));
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
