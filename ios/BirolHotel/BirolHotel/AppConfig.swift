//
//  AppConfig.swift
//  BirolHotel
//
//  Central place to point the app at your GitHub Pages deployment.
//  When you push to the repo, Pages rebuilds automatically; when
//  the app launches it pulls the newest HTML/CSS/JS, so updates
//  flow through without rebuilding the app binary.
//

import Foundation

enum AppConfig {

    /// URL of the hosted landing page (GitHub Pages).
    /// This is auto-deployed from the /web folder on every push to main.
    static let landingURL = URL(
        string: "https://ho11owpoint.github.io/Hotel_Booking_Bot/"
    )!

    /// Bust the HTTP cache on every app launch so newly-pushed
    /// changes on GitHub Pages are picked up immediately.
    static var landingURLWithCacheBust: URL {
        let bust = Int(Date().timeIntervalSince1970)
        return URL(
            string: landingURL.absoluteString + "?v=\(bust)"
        ) ?? landingURL
    }
}
