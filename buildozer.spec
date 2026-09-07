[app]
title = OBD2 ВАЗ
package.name = obd2vaz
package.domain = org.yourdomain

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 0.1
requirements = python3,kivy,jnius

android.permissions = INTERNET,BLUETOOTH,BLUETOOTH_ADMIN,BLUETOOTH_CONNECT,BLUETOOTH_SCAN,ACCESS_FINE_LOCATION
android.api = 33
android.minapi = 21

# Важно для Kivy
android.gradle_dependencies = 'com.android.support:support-annotations:28.0.0'

# Отключаем автообновление SDK (помогает при ошибках)
android.ndk = 23b

# Отключаем некоторые проверки
android.accept_sdk_license = True
android.ndk_path = /home/user/.buildozer/android/platform/android-ndk-r23b
