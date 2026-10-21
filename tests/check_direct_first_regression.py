#!/usr/bin/env python3
"""
Regression test for Direct-First Transport Milestone:
- Cold process startup direct probe (DIRECT_PROBE_TIMEOUT_MS = 2000).
- Fallback to saved proxy settings on timeout.
- State-change success retains direct mode, cancels fallback timer.
- Manual setProxySettings increments generation, cancels fallback timer, supersedes fallback.
- Rotation suspension in ProxyRotationController when direct probe or direct retained is active.
"""

import sys

def check_connections_manager(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    errors = []

    # 1. DIRECT_PROBE_TIMEOUT_MS = 2000
    if "DIRECT_PROBE_TIMEOUT_MS = 2000" not in content:
        errors.append("ConnectionsManager missing DIRECT_PROBE_TIMEOUT_MS = 2000")

    # 2. directProbeAttempted, directProbeActive, directRetainedActive, directProbeGeneration
    for field in ["directProbeAttempted", "directProbeActive", "directRetainedActive", "directProbeGeneration", "directFallbackRunnable"]:
        if field not in content:
            errors.append(f"ConnectionsManager missing field '{field}'")

    # 3. isDirectProbeActive() and isDirectRetainedActive() public getters
    if "public static boolean isDirectProbeActive()" not in content:
        errors.append("ConnectionsManager missing public static boolean isDirectProbeActive()")
    if "public static boolean isDirectRetainedActive()" not in content:
        errors.append("ConnectionsManager missing public static boolean isDirectRetainedActive()")

    # 4. In init(), check proxy_direct_first and guard cold probe
    if "final boolean directFirst = preferences.getBoolean(\"proxy_direct_first\", false);" not in content:
        errors.append("ConnectionsManager.init missing preferences check for 'proxy_direct_first'")
    if "if (directFirst && !directProbeAttempted)" not in content:
        errors.append("ConnectionsManager.init missing directFirst && !directProbeAttempted probe branch")

    # 5. onConnectionStateChanged fresh callback success handling
    if "if (directProbeActive && state == ConnectionStateConnected)" not in content:
        errors.append("ConnectionsManager.onConnectionStateChanged missing directProbeActive && state == ConnectionStateConnected handling")

    # 6. setProxySettings cancels direct probe generation and timers
    if "directProbeGeneration++;" not in content:
        errors.append("ConnectionsManager.setProxySettings missing directProbeGeneration++")
    if "directRetainedActive = false;" not in content:
        errors.append("ConnectionsManager.setProxySettings missing directRetainedActive reset")

    return errors

def check_proxy_rotation_controller(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    errors = []

    # 1. Suspends rotation during direct probe or retained direct active
    if "ConnectionsManager.isDirectProbeActive() || ConnectionsManager.isDirectRetainedActive()" not in content:
        errors.append("ProxyRotationController didReceivedNotification missing check for isDirectProbeActive() || isDirectRetainedActive()")

    return errors

def main():
    cm_path = "TMessagesProj/src/main/java/org/telegram/tgnet/ConnectionsManager.java"
    prc_path = "TMessagesProj/src/main/java/org/telegram/messenger/ProxyRotationController.java"

    cm_errors = check_connections_manager(cm_path)
    prc_errors = check_proxy_rotation_controller(prc_path)

    all_errors = cm_errors + prc_errors

    if all_errors:
        print("[FAIL] Direct-first transport regression checks failed:")
        for err in all_errors:
            print("  - " + err)
        sys.exit(1)
    else:
        print("[PASS] All direct-first transport regression checks passed.")
        sys.exit(0)

if __name__ == "__main__":
    main()
