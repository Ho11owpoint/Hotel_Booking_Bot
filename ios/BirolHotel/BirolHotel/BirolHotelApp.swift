//
//  BirolHotelApp.swift
//  BirolHotel
//
//  Thin iOS shell that renders the Birol Hotel booking UI
//  hosted on GitHub Pages inside a WKWebView — so pushing a
//  new commit to the site's repo updates the app instantly.
//

import SwiftUI

@main
struct BirolHotelApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
                .preferredColorScheme(.dark)   // keeps the status bar icons white
        }
    }
}
