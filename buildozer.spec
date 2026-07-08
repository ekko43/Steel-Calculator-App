[app]

# (str) Title of your application
title = Steel Section Checker

# (str) Package name (no spaces/special chars)
package.name = steelchecker

# (str) Package domain (reversed, used as unique android package id)
package.domain = org.jeko

# (str) Source code where the main.py lives
source.dir = .

# (list) Source files to include
source.include_exts = py,png,jpg,kv,atlas

# (str) Application versioning
version = 1.0

# (list) Application requirements
# core.py only needs the stdlib 'math' module, so kivy is the only dependency.
requirements = python3,kivy==2.3.1

# (str) Icon of the application
icon.filename = %(source.dir)s/assets/icon.png

# (str) Supported orientation (portrait, landscape, all)
orientation = portrait

# (bool) Fullscreen
fullscreen = 0

# (list) Permissions — none needed, this app does no networking or storage
android.permissions =

# (int) Target Android API
android.api = 34

# (int) Minimum API your APK / AAB will support
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25b

# (list) The Android archs to build for
android.archs = arm64-v8a, armeabi-v7a

# (bool) Accept the Android SDK licenses automatically
android.accept_sdk_license = True

# (str) Format used to package the app for release (apk or aab)
# android.release_artifact = apk


[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug)
log_level = 2

# (int) Display warning if buildozer is run as root
warn_on_root = 1
