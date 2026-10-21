# Direct-first Connection & Proxy Status

A Telegram Android concept: try a direct connection first, fall back to your saved proxy, and make the active connection path clear.

Unofficial Telegram Android feature concept for design/code review. Source proposal, not an official Telegram release or a claim of Telegram endorsement.

## Demo

A real-device demo is being prepared. This repository does not yet include a demo video.

## Experience

- Opt-in **Try direct connection first**, off by default, in a separate native settings card with title, description and switch.
- On cold process startup, attempt a direct Telegram connection for a configured 2-second window; retain direct on the owner account's timely Connected callback, otherwise restore the saved proxy.
- Keep stored proxy configuration separate from effective direct transport. Manual proxy selection cancels pending automatic work. Turning the option off immediately exits direct-first mode and restores a valid saved proxy when available.
- **Direct connection** is a status-only row, visible while the option is enabled; it has no manual action or edit/info icon. Real proxy rows remain selectable/editable.
- A connected-proxy shield beside the collapsed chat header opens the existing proxy screen. Existing native theme and lifecycle components are reused.

Direct connections expose the device's public IP to Telegram's network. This is an opt-in tradeoff, not an anonymity feature. The 2-second value is a scheduled timeout, not a measured hard real-time guarantee under Android sleep or a blocked UI thread. A successful cold-start trial does not introduce ongoing mid-session automatic direct/proxy failover.

## Code and integration

- [`tg-craft.patch`](tg-craft.patch): browsable implementation diff, including new assets and tests, against upstream commit **f32ffeec763f0bdbf4bec25b52d654f77bff733d**.
- [`tests/`](tests): directly browsable checks; run from a patched Telegram source root, not this proposal repository.
- [`assets/`](assets): the two new native vector drawables, also included in the patch.

### Implementation map

- `ConnectionsManager.java`: cold-start direct trial, timeout, owner/deadline checks and cancellation on manual settings.
- `ProxyRotationController.java`: guards against rotation overriding trial/retained direct transport.
- `ProxyListActivity.java`: native settings card, status-only direct row and immediate OFF handling.
- `DialogsActivity.java` / `DialogStoriesCell.java`: effective-route labels and collapsed-header proxy indicator.
- `ActionBar.java` / `SimpleTextView.java`: header drawable state and width handling.
- Debug SDK23 manifest: lint remediation, separate from feature behavior.

All these changes are reviewable in the patch; this repository is not a standalone Android application.
- `receipt.json`: upstream/local revision, patch digest, exported file digests and tested APK digest.
- `LICENSE`: upstream GNU GPL version 2 license text. Retain upstream copyright/license notices and submodule licenses; this patch does not relicense upstream or third-party code.

The patch intentionally uses **zero context** to avoid exporting unrelated credential-bearing manifest context. Apply with `--unidiff-zero` to the exact baseline only. Application source matches the accepted local candidate. One packaging-only test change replaces a machine-specific scratch path with `java.io.tmpdir`; recorded in the receipt. `.gitignore` includes the existing local `.hermes/` exclusion. No APK, signing material, account data, build caches, API credentials, service configuration or full source tree is bundled.

## Obtain baseline and apply

Run in a new directory; do not apply over a dirty checkout:

```sh
git clone --no-checkout https://github.com/DrKLO/Telegram.git Telegram-tg-craft
cd Telegram-tg-craft
git checkout --detach f32ffeec763f0bdbf4bec25b52d654f77bff733d
git submodule update --init --recursive --depth=1
git apply --check --unidiff-zero /path/to/tg-craft.patch
git apply --unidiff-zero /path/to/tg-craft.patch
```

The package's exact-baseline application and exported file digests were checked in an isolated Git index. This is not a clean-machine build of the exported package.

## Build

Follow the upstream `README.md` and Telegram API requirements. Obtain your own `api_id`/API configuration, Firebase setup and signing credentials where required. Upstream contains example/dummy configuration; do not redistribute a public app using someone else's credentials or imply an official Telegram release. Preserve GPL source-distribution obligations and upstream branding requirements.

Verified local environment: Android Studio bundled JBR Java 21, SDK 36, Build Tools 36.0.0, NDK 27.2.12479018, CMake 3.22.1, Gradle wrapper 8.13 and AGP 8.13.2. Use the existing wrapper; no new feature dependencies were added.

```sh
export JAVA_HOME="/path/to/jdk-21"
export ANDROID_HOME="/path/to/Android/sdk"
./gradlew :TMessagesProj_App:assembleAfatDebug :TMessagesProj_App:lintAfatDebug
```

Output: `TMessagesProj_App/build/outputs/apk/afat/debug/app.apk`.

## Checks

From the patched source root, with JDK 21 and Python 3:

```sh
python3 TMessagesProj_AppTests/check_direct_first_regression.py
python3 TMessagesProj_AppTests/check_proxy_header_regression.py
mkdir -p "$TMPDIR/tg-craft-test-classes"
"$JAVA_HOME/bin/javac" -d "$TMPDIR/tg-craft-test-classes" TMessagesProj_AppTests/DirectRowBehaviorRegressionTest.java
"$JAVA_HOME/bin/java" -Djava.io.tmpdir="$TMPDIR" -cp "$TMPDIR/tg-craft-test-classes" org.telegram.apptests.DirectRowBehaviorRegressionTest
```

Set `TMPDIR` to an existing writable temporary directory first. The Python checks are static source-pattern checks, not transport/runtime tests. The Java harness extracts selected production cell methods and runs against UI stubs, with additional structural contracts; it does not execute the Android activity, real animations, accessibility or network stack. Its simple brace parser is intentionally limited.

## Verification and limits

- Accepted local candidate: assembleAfatDebug and lintAfatDebug completed successfully; lint **0 errors, 5 warnings**. Remaining categories: OldTargetApi, SelectedPhotoAccess and ExportedService. No lint suppression or lint baseline was added. Obsolete disabled measurement component registrations were removed, optional telephony hardware declared, analytics deactivation retained; no analytics dependency was added.
- Local static checks and extracted-method harness passed. The direct-row visibility defect was reproduced before repair.
- Physical-phone UI fixes and cold-start/fallback, manual override, background return, multi-account and proxy-rotation scenarios were reported successful by the user. These are user-reported checks, not independently instrumented measurements; no emulator or FPS claims.
- Tested local APK SHA256: `b33a4406e50688f6b982077071f28c63dfe899f204b552d222436419e63d6d2e`. The APK is not distributed here; no bit-for-bit reproducible build claim.
- No clean upstream lint baseline run, clean-machine rebuild, exhaustive concurrency tests or verified post-change codebase index freshness. Native callback meaning, strict timeout timing under sleep, and broader transport races remain review considerations.
- Package secret scan is heuristic and file-scope review only, not a security certification. Review again before any public release. No commit, push, publication or submission is performed by this package.
