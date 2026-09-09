[app]
title = OBD2 ВАЗ
package.name = obd2vaz
package.domain = org.yourdomain

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 0.1
requirements = python3,kivy

orientation = portrait
fullscreen = 0

android.permissions = INTERNET,BLUETOOTH
android.api = 30
android.minapi = 21
android.ndk = 25b
android.sdk = 30
android.accept_sdk_license = True
android.gradle_dependencies = ''
android.enable_androidx = True
android.use_androidx = True

[buildozer]
log_level = 2
warn_on_root = 1
