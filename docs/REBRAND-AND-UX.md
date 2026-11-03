# FDGCast Studio — Rebrand & usability specification

Status: implementation plan; NOT a claim that the current OBS-based alpha has been rebranded.

## Product identity
- Product: FDGCast Studio
- Publisher: Forged Destiny Gaming
- Release channel: Alpha / prerelease
- Preserve OBS Studio and third-party copyright notices and GPL obligations.
- Change application identity at source level, including executable metadata, window title, icon, taskbar, About screen, settings/config paths and installer identity. Do not merely rename obs64.exe.

## Design principles
1. Beginner-first, advanced tools remain accessible.
2. Use clear everyday labels, with explanations and tooltips.
3. Dark, high-contrast theme; accessible focus states; scalable type.
4. Never obscure disconnections, dropped frames or output failures.
5. Maintain compatibility with OBS scene collections, plugins and capture pipeline.

## Main workspace
- Left navigation: Dashboard, Scenes, Sources, Audio, Multistream, Chat, Activity, Settings.
- Center: live preview and scene controls.
- Right: stream health, platform connection status, and contextual help.
- Bottom: large Start/Stop Streaming, Start/Stop Recording, and Studio Mode controls.
- Status indicators distinguish Connected, Reconnecting, Disconnected, and Not configured.

## Onboarding
- Guided setup: camera/microphone, stream platforms, output quality, recording path, and test stream.
- Provide sensible presets (Performance / Balanced / Quality), and expose bitrate/encoder controls under Advanced.
- Explain stream key privacy and warn before exposing secrets.

## Settings information architecture
- General: language, startup, notifications.
- Streaming: platform destinations, multistream, reconnect.
- Video & Audio: canvas/output resolution, frame rate, microphones, monitoring.
- Recording: format, quality, destination, replay buffer.
- Advanced: encoders, networking, plugins, diagnostics.

## Phased implementation
1. Inventory actual OBS source archive and application entry points; add tracked source patches and reproducible patch application to CI.
2. Rebrand compiled application identity, resources, icon, metadata, About and settings isolation.
3. Implement a coherent dark theme and navigation improvements without breaking OBS docks.
4. Add first-run wizard, help text, presets, and clear connection/error states.
5. Integrate FDGCast companion features as modules with integration tests.
6. Verify clean Windows install, uninstall, OBS coexistence, plugin compatibility, GPL notices and signed release process.

## Release gates
- No full-rebrand claim until application title, taskbar icon, process identity, About screen, config location and startup behavior are verified on Windows.
- No feature claims for companion integrations until tested.
- Publish prereleases only after successful build and installer smoke tests.
