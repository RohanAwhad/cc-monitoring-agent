---
tags:
  - factory
  - source
  - cc-monitoring-agent
source: factory-archivist
date: 2026-05-07
---

# macOS Notifications — osascript Reliability on Sequoia

## Critical Finding

`osascript -e 'display notification ...'` silently fails on macOS Sequoia and later when the terminal app lacks notification permissions. The command exits 0 (no error) but the notification is dropped. This is a chicken-and-egg problem: terminal apps don't appear in System Settings → Notifications until they've successfully delivered a notification.

## Workarounds (ranked by reliability)

1. **`terminal-notifier`** (`brew install terminal-notifier`): Registers as its own Notification Center app, sidesteps the permission issue entirely. Most reliable for automation.
2. **One-time Script Editor permission grant**: Run `display notification` in Script Editor first to trigger permission prompt.
3. **Fallback to `display dialog`**: Works without permissions but creates a modal dialog, not a banner.

## Recommendation for ccm

Use `terminal-notifier` as primary (check availability via `shutil.which`), fall back to `osascript` with a warning about permissions. Document the Sequoia issue in help text.

## Sources

- [macOS Notification Issue](https://forum.latenightsw.com/t/trying-to-use-terminal-for-display-notification/5068)
- [Silent Fail Bug](https://github.com/gsd-build/gsd-2/issues/2632)
- [macOS Notification Best Practices](https://dev.to/jfpio/how-to-get-macos-notifications-for-long-running-processes-even-over-ssh-154d)
