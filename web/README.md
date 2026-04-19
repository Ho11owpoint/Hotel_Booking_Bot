# Birol Hotel — static web app (for GitHub Pages)

This folder is a **100% static** version of the booking chatbot. All the
Python logic from `src/` has been ported to browser JavaScript, so the
whole experience runs with no backend.

That's what lets the iOS app stay in sync with GitHub — push, wait ~30 s
for Pages to rebuild, relaunch the app.

## Structure

```
web/
├── index.html              Landing page (hotel hero view + booking button)
├── chat.html               Chat interface (dialog + calendar picker)
├── styles/
│   ├── landing.css         Twilight-navy landing theme
│   └── chat.css            Iridescent chat theme
├── js/
│   ├── bot.js              Full bot: NLP + entities + state machine + store
│   └── chat.js             UI controller (bubbles + calendar widget)
├── data/
│   └── intents.json        Same training patterns the Python bot uses
└── assets/
    └── hotel-hero.svg      Twilight illustration of the hotel
```

## Enabling GitHub Pages

1. **Settings → Pages** in your repo.
2. **Source**: "Deploy from a branch".
3. **Branch**: `main`, **Folder**: `/web`.
4. Save; within a minute your site is live at
   `https://YOUR-USERNAME.github.io/Hotel_Booking_Bot/`.

## Running locally

```bash
cd web
python -m http.server 8000
# then open http://127.0.0.1:8000
```

Or any static file server — the site has zero build step.

## Where the bookings live

Confirmed bookings are stored in `localStorage` under the key
`birol.bookings`. Open the browser devtools to inspect them, or run

```js
JSON.parse(localStorage.getItem("birol.bookings"))
```

in the console.
