---
tags:
  - factory
  - source
  - cc-monitoring-agent
source: factory-archivist
date: 2026-05-07
---

# macOS Notifications: terminal-notifier vs osascript (Cycle 4 Update)

## Confirmed Finding

`osascript -e 'display notification ...'` **silently fails** on macOS Sequoia when the terminal app lacks notification permissions. Exits 0, no error, notification dropped. Chicken-and-egg problem: terminal apps don't appear in System Settings > Notifications until they deliver one notification.

## Comparison

| Feature | osascript | terminal-notifier |
|---|---|---|
| Built-in | Yes | No (`brew install`) |
| Sequoia reliable | No — silent fail | Yes — own app entry |
| Attribution | "Script Editor" | Own app name |
| Click-to-focus | Opens Script Editor | Activates target app |

## Sequoia-Specific Caveat

Do NOT use `-sender` flag with `-activate` on terminal-notifier — conflicts on macOS 15.x+.

## Recommended Pattern

Prefer `terminal-notifier` (via `shutil.which()`), fall back to `osascript` with logged warning.

## Sources

- [terminal-notifier](https://github.com/julienXX/terminal-notifier)
- [Sequoia silent fail](https://github.com/gsd-build/gsd-2/issues/2632)
- [Notification forum](https://forum.latenightsw.com/t/trying-to-use-terminal-for-display-notification/5068)
- [Swiss Mac User](https://swissmacuser.ch/native-macos-notifications-from-terminal-scripts/)
