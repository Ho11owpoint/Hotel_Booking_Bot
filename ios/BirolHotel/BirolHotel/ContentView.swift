//
//  ContentView.swift
//  BirolHotel
//
//  Hosts the WebView full-screen (Dynamic-Island aware) with
//  a branded splash while the first page loads and a retry
//  screen if the network is unreachable.
//

import SwiftUI

struct ContentView: View {
    @State private var isLoading = true
    @State private var loadError: String? = nil

    var body: some View {
        ZStack {
            // Twilight navy background — the same palette the web
            // landing uses, so the splash blends into the page.
            LinearGradient(
                colors: [
                    Color(red: 0.047, green: 0.059, blue: 0.137),   // #0c0f23
                    Color(red: 0.039, green: 0.051, blue: 0.110),   // #0a0d1c
                    Color(red: 0.020, green: 0.027, blue: 0.059),   // #05070f
                ],
                startPoint: .top,
                endPoint: .bottom
            )
            .ignoresSafeArea()

            // WebView — the real UI.
            WebView(
                url: AppConfig.landingURLWithCacheBust,
                isLoading: $isLoading,
                loadError: $loadError
            )
            .opacity(loadError == nil ? 1 : 0)
            .ignoresSafeArea(edges: [.bottom, .horizontal])

            // Splash (visible during the first load)
            if isLoading && loadError == nil {
                SplashView()
                    .transition(.opacity)
            }

            // Error state
            if let err = loadError {
                OfflineView(message: err, retry: {
                    loadError = nil
                    isLoading = true
                })
            }
        }
        .statusBarHidden(false)
    }
}

// MARK: - Splash

private struct SplashView: View {
    @State private var pulse = false

    var body: some View {
        VStack(spacing: 20) {
            // Chromatic rim ring
            ZStack {
                Circle()
                    .fill(AngularGradient(
                        colors: [
                            .pink, .orange, .yellow, .green,
                            .cyan, .blue, .purple, .pink
                        ],
                        center: .center))
                    .frame(width: 98, height: 98)
                    .blur(radius: 14)
                    .opacity(0.6)
                Circle()
                    .strokeBorder(AngularGradient(
                        colors: [
                            .pink, .orange, .yellow, .green,
                            .cyan, .blue, .purple, .pink
                        ],
                        center: .center),
                        lineWidth: 2)
                    .frame(width: 88, height: 88)
                Text("B")
                    .font(.custom("Georgia-Bold", size: 32))
                    .foregroundColor(.white)
            }
            .scaleEffect(pulse ? 1.04 : 0.98)
            .animation(.easeInOut(duration: 1.4).repeatForever(autoreverses: true),
                       value: pulse)

            Text("Birol Hotel")
                .font(.custom("Georgia", size: 22))
                .foregroundColor(.white)
                .tracking(4)

            Text("Loading the latest booking assistant…")
                .font(.system(size: 13))
                .foregroundColor(.white.opacity(0.55))
        }
        .onAppear { pulse = true }
    }
}

// MARK: - Offline fallback

private struct OfflineView: View {
    let message: String
    let retry: () -> Void

    var body: some View {
        VStack(spacing: 14) {
            Text("Can't reach the server")
                .font(.custom("Georgia", size: 20))
                .foregroundColor(.white)

            Text(message)
                .font(.system(size: 13))
                .multilineTextAlignment(.center)
                .foregroundColor(.white.opacity(0.6))
                .padding(.horizontal, 40)

            Button(action: retry) {
                Text("Try again")
                    .font(.system(size: 14, weight: .semibold))
                    .foregroundColor(.white)
                    .padding(.horizontal, 22).padding(.vertical, 10)
                    .background(
                        Capsule()
                            .strokeBorder(
                                AngularGradient(
                                    colors: [
                                        .pink, .orange, .yellow, .green,
                                        .cyan, .blue, .purple, .pink
                                    ],
                                    center: .center),
                                lineWidth: 1.5)
                    )
                    .background(Capsule().fill(Color.white.opacity(0.04)))
            }
            .padding(.top, 6)
        }
        .padding()
    }
}

// MARK: - Preview

#Preview {
    ContentView()
        .preferredColorScheme(.dark)
}
