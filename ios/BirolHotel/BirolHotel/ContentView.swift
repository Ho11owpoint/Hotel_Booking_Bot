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
            // Liquid-glass orb — soft radial fill + top specular highlight
            ZStack {
                // Ambient bloom behind the orb
                Circle()
                    .fill(Color(red: 0.70, green: 0.78, blue: 1.0))
                    .frame(width: 120, height: 120)
                    .blur(radius: 18)
                    .opacity(0.18)

                // The orb itself — dark tinted glass
                Circle()
                    .fill(
                        RadialGradient(
                            gradient: Gradient(stops: [
                                .init(color: .white.opacity(0.22), location: 0.0),
                                .init(color: .white.opacity(0.06), location: 0.25),
                                .init(color: .clear,               location: 0.55),
                            ]),
                            center: UnitPoint(x: 0.32, y: 0.28),
                            startRadius: 0,
                            endRadius: 60
                        )
                    )
                    .background(
                        Circle().fill(Color(red: 0.086, green: 0.102, blue: 0.188))
                    )
                    .frame(width: 88, height: 88)
                    .overlay(
                        Circle().strokeBorder(Color.white.opacity(0.22), lineWidth: 1)
                    )
                    .shadow(color: .black.opacity(0.5), radius: 14, x: 0, y: 6)

                // Top specular crescent
                Ellipse()
                    .fill(
                        LinearGradient(
                            colors: [.white.opacity(0.55), .clear],
                            startPoint: .top, endPoint: .bottom
                        )
                    )
                    .frame(width: 60, height: 18)
                    .offset(y: -30)
                    .blur(radius: 2)
                    .opacity(0.85)

                Text("B")
                    .font(.custom("Georgia-Bold", size: 30))
                    .foregroundColor(.white)
            }
            .scaleEffect(pulse ? 1.035 : 0.985)
            .animation(.easeInOut(duration: 1.6).repeatForever(autoreverses: true),
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
                        // Liquid glass pill — bright rim, soft inner fill
                        Capsule().strokeBorder(Color.white.opacity(0.36),
                                               lineWidth: 1)
                    )
                    .background(
                        Capsule().fill(
                            LinearGradient(
                                colors: [.white.opacity(0.18),
                                         .white.opacity(0.04)],
                                startPoint: .top, endPoint: .bottom
                            )
                        )
                    )
                    .shadow(color: .black.opacity(0.4), radius: 6, y: 3)
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
