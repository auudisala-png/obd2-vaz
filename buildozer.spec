[app]
title = OBD2 ВАЗ
package.name = obd2vaz
package.domain = org.yourdomain

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 0.1
requirements = python3,kivy,jnius

android.permissions = INTERNET,BLUETOOTH,BLUETOOTH_ADMIN,BLUETOOTH_CONNECT,BLUETOOTH_SCAN,ACCESS_FINE_LOCATION

# Используем более стабильные версии
android.api = 30
android.minapi = 21
android.ndk = 23b
android.sdk = 30

android.gradle_dependencies = 'com.android.support:support-annotations:28.0.0'
android.accept_sdk_license = True
android.ndk_path = /home/runner/.buildozer/android/platform/android-ndk-r23b

# Отключаем некоторые проверки
android.fix_android_gradle_plugin = False
android.gradle_plugin_version = 3.5.0
