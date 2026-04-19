# Birol Hotel — iOS app

A thin SwiftUI app that hosts the Birol Hotel booking site (hosted on
GitHub Pages) inside a `WKWebView`. Because the UI lives on the web,
**any commit you push to GitHub updates the app instantly** — no
rebuild, no App Store review, no re-install.

Designed and tuned for **iPhone 14 Pro** (393 × 852 pt, Dynamic Island aware).

---

## 1. One-time setup

### Prerequisites
* A Mac (for Xcode — required for iOS development)
* **Xcode 15+**
* An **Apple ID** (free — you do *not* need a paid Apple Developer account)
* A GitHub account with this repo forked or pushed there

### A. Enable GitHub Pages for your repo

1. Push the whole `Hotel_Booking_Bot` project to a repo on GitHub (e.g.
   `github.com/YOUR-USERNAME/Hotel_Booking_Bot`).
2. Go to **Settings → Pages**.
3. Under **Build and deployment → Source**, pick **"Deploy from a branch"**.
4. Branch: `main` (or whatever your default is). Folder: **`/docs`**.
5. Click **Save**. Pages gives you a URL like
   `https://YOUR-USERNAME.github.io/Hotel_Booking_Bot/`.
6. Open it in a browser — you should see the landing page with the
   Birol Hotel hero and the circular booking button.

Every `git push` to that branch now triggers a redeploy in ~30 s.

### B. Point the iOS app at your Pages URL

Open `ios/BirolHotel/BirolHotel/AppConfig.swift`:

```swift
static let landingURL = URL(
    string: "https://YOUR-USERNAME.github.io/Hotel_Booking_Bot/"
)!
```

Replace `YOUR-USERNAME` with your GitHub username (and the repo name if you
renamed it).

### C. Open the Xcode project

```
open ios/BirolHotel/BirolHotel.xcodeproj
```

Xcode opens the project. File tree should show **BirolHotel** with:
`BirolHotelApp.swift`, `ContentView.swift`, `WebView.swift`,
`AppConfig.swift`, `Assets.xcassets`, `Info.plist`.

### D. Sign with your personal Apple ID

1. In Xcode, select the **BirolHotel** target → **Signing & Capabilities**.
2. Check **Automatically manage signing**.
3. Team: choose your **Personal Team** (your Apple ID). If you don't see
   one, add your Apple ID under **Xcode → Settings → Accounts**.
4. The *Bundle Identifier* must be globally unique — change
   `com.birolhotel.app` to e.g. `com.yourname.birolhotel`.

### E. Install on your iPhone 14 Pro

1. Plug the iPhone into the Mac via USB.
2. Unlock it and "Trust This Computer".
3. In Xcode's device selector (top bar), pick **Your iPhone**.
4. Hit **Run** (⌘ R).
5. First time only: on the iPhone, go to **Settings → General → VPN &
   Device Management**, find your Apple ID, and **Trust** the developer
   profile.

Done — the app is installed. Every 7 days (personal Apple ID
limitation) you'll need to re-run from Xcode to refresh the signature,
but that's it.

---

## 2. How auto-update works

```
 ┌───────────────┐   git push   ┌──────────────┐   30 s  ┌──────────────┐
 │  Your repo    │ ───────────▶ │ GitHub Pages │ ──────▶ │ Updated HTML │
 └───────────────┘              └──────────────┘         └──────┬───────┘
                                                                │ every app launch
                                                                ▼
                                                       ┌──────────────────┐
                                                       │  Birol Hotel app │
                                                       │  (WKWebView)     │
                                                       └──────────────────┘
```

* On launch, `AppConfig.landingURLWithCacheBust` appends a `?v=<timestamp>`
  query param so `WKWebView` bypasses its cache and fetches the newest
  page.
* `URLRequest.cachePolicy = .reloadIgnoringLocalCacheData` reinforces this.
* Local data *stored inside the WebView* (e.g. localStorage-saved
  bookings) persists across launches — only the HTML/CSS/JS is refetched.
* Manual refresh: pull-to-refresh anywhere in the app.

---

## 3. Project layout

```
ios/
└── BirolHotel/
    ├── BirolHotel.xcodeproj/            ← double-click to open in Xcode
    │   └── project.pbxproj
    └── BirolHotel/
        ├── BirolHotelApp.swift          ← @main entry point
        ├── ContentView.swift            ← splash + offline UI, hosts WebView
        ├── WebView.swift                ← UIViewRepresentable<WKWebView>
        ├── AppConfig.swift              ← put your GitHub Pages URL here
        ├── Info.plist                   ← dark mode, portrait, etc.
        └── Assets.xcassets/             ← app icon + accent colour placeholders
```

---

## 4. Customisation quick-reference

| What you want to change               | File                                 |
|---------------------------------------|--------------------------------------|
| The URL the app loads                 | `BirolHotel/AppConfig.swift`         |
| App display name                      | `BirolHotel/Info.plist` → `CFBundleDisplayName` |
| Splash screen / loading UI            | `BirolHotel/ContentView.swift`       |
| Cache behaviour, back-gestures        | `BirolHotel/WebView.swift`           |
| Anything UI-facing (pages, chat, etc.)| `../docs/` (deployed via GitHub Pages) |

---

## 5. Troubleshooting

| Symptom                                                        | Fix |
|----------------------------------------------------------------|-----|
| White screen on launch                                         | Verify `AppConfig.landingURL` points at an HTTPS URL that returns 200. Test it in Safari on the iPhone first. |
| Pages URL returns 404                                          | Confirm *Settings → Pages* is set to serve the `/docs` folder of your default branch. The first deploy takes ~1 min. |
| "Untrusted Developer" alert on first launch                    | Settings → General → VPN & Device Management → trust your Apple ID. |
| App re-downloads HTML every launch (slow)                      | Expected — that's how updates flow in. Pages caches are CDN-fast so this is usually <1 s. |
| Local bookings disappeared                                     | They live in WebView localStorage and are cleared if iOS evicts the WebKit store. Not a bug — bookings are a prototype. |
| App expires after 7 days                                       | Personal Apple ID limitation — re-run from Xcode. Or join the $99/year Apple Developer Program for 1-year signing. |

---

## 6. Further work (next phases)

* Swap GitHub Pages for a proper backend if you want multi-user bookings
  (right now every phone has its own localStorage store).
* Replace the WebView chat screen with a native SwiftUI chat + native
  `UICalendarView` for a more Apple-native feel, keeping the landing
  page as web content.
* Add a service worker on the web side so the chat works offline.
