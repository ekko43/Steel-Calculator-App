# Steel Section Checker (Android)

A compression-only steel section adequacy checker — AISC 360-22, LRFD & ASD,
SI units — packaged as an installable Android app. This is a Kivy rebuild of
the original PyQt5 desktop tool (PyQt5 cannot run on Android; Kivy is the
Python GUI toolkit that can).

## What's in this repo

| File | Purpose |
|---|---|
| `main.py` | Kivy app — all screens, inputs, section picker, results log |
| `steel_checker_core.py` | **Unmodified** calculation engine & AISC section database (only depends on `math`) |
| `buildozer.spec` | Android packaging config (app id, permissions, target API, etc.) |
| `.github/workflows/build-apk.yml` | Builds the APK automatically in the cloud on every push |

## Get the APK — no local setup required

1. Create a new **public or private** GitHub repository.
2. Upload all the files above, **preserving the folder structure**
   (`.github/workflows/build-apk.yml` must stay in that exact path).
3. Push to the `main` branch (or use the "Run workflow" button under the
   **Actions** tab if the branch isn't `main`).
4. Wait ~15–20 minutes for the first build (it downloads the Android
   SDK/NDK toolchain inside the container; later builds are faster thanks
   to caching).
5. Open the finished run under **Actions → Build Android APK**, scroll to
   **Artifacts**, and download `steel-checker-apk.zip`.
6. Unzip it to get `steelchecker-1.0-arm64-v8a_armeabi-v7a-debug.apk`,
   transfer it to your phone (Google Drive, USB, etc.), and tap it to
   install. You'll need to allow "Install unknown apps" for whichever app
   you use to open the file the first time.

This is a **debug** build, fine for installing on your own phone. It is not
signed for the Play Store — that's a separate step (`buildozer android
release` + signing key) if you ever want to publish it.

The workflow pulls Kivy's official, pre-built `kivy/buildozer` Docker image
and runs it directly (`docker run ... kivy/buildozer android debug`),
rather than relying on a marketplace action that builds its own image on
every run — that extra image-build step is a common source of flaky
"Docker build failed" errors unrelated to your actual app.

## Building locally instead (optional)

Only possible on Linux/macOS (or WSL on Windows):

```bash
pip install buildozer cython
buildozer android debug
# APK appears in ./bin/
```

The first local build also downloads the SDK/NDK and can take a while.

## App features

- All shape types from the original tool: W, WT, HSS Rectangular, HSS
  Round, Single Angle, Double Angle (with 0/3/9 mm back-to-back
  separation), Channel, plus the two built-up types (Channel+W, Plate
  built-up W).
- Searchable section picker (the W and 2L databases have 270–500+ entries
  each, so there's a filter box).
- LRFD and ASD compression check per AISC 360-22 Sec. E3, same formulas as
  the desktop version, via the untouched `steel_checker_core.py`.
- Scrollable running results log so you can compare multiple checks in one
  session.

## Notes / things you may want to change

- `package.domain` in `buildozer.spec` is set to `org.jeko` — change it if
  you want a different reverse-domain app ID before your first real
  release.
- No app icon is set yet; drop a `icon.png` (square, e.g. 512×512) in the
  repo root and uncomment the `icon.filename` line in `buildozer.spec` if
  you want a custom icon instead of the default Kivy one.
- The app requests no Android permissions — it does no networking or file
  storage, everything is calculated on-device from the bundled database.
