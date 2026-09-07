"""
Диагностика ВАЗ OBD2 - Мобильная версия
Оптимизировано для телефона
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.progressbar import ProgressBar
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import NumericProperty, StringProperty
from kivy.graphics import Color, Rectangle
from kivy.uix.switch import Switch

import threading
import time
import re
import sys
import random

# Настройка окна
Window.clearcolor = (0.05, 0.05, 0.05, 1)

# Цвета - ДОБАВЛЕН 'cyan'
COLORS = {
    'bg': (0.05, 0.05, 0.05, 1),
    'card': (0.1, 0.1, 0.1, 1),
    'card2': (0.15, 0.15, 0.15, 1),
    'text': (1, 1, 1, 1),
    'text_secondary': (0.6, 0.6, 0.6, 1),
    'green': (0, 0.9, 0, 1),
    'yellow': (1, 0.85, 0, 1),
    'red': (1, 0.2, 0.2, 1),
    'blue': (0.2, 0.5, 0.9, 1),
    'gray': (0.3, 0.3, 0.3, 1),
    'orange': (1, 0.6, 0, 1),
    'purple': (0.6, 0.2, 0.8, 1),
    'sim_mode': (1, 0.5, 0, 1),
    'cyan': (0, 0.8, 0.8, 1),  # ДОБАВЛЕНО
}

IS_ANDROID = 'android' in sys.platform or 'linux' in sys.platform

class OBD2Real:
    """Реальный OBD2 адаптер через Bluetooth"""
    
    def __init__(self):
        self.socket = None
        self.connected = False
        self.device_address = None
        self.bluetooth_available = False
        self.sim_mode = False
        
        if IS_ANDROID:
            try:
                from jnius import autoclass
                self.BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
                self.BluetoothDevice = autoclass('android.bluetooth.BluetoothDevice')
                self.BluetoothSocket = autoclass('android.bluetooth.BluetoothSocket')
                self.UUID = autoclass('java.util.UUID')
                self.bluetooth_available = True
            except:
                self.bluetooth_available = False
    
    def set_sim_mode(self, enabled):
        self.sim_mode = enabled
        if enabled:
            self.connected = True
        else:
            self.connected = False
            self.disconnect()
    
    def get_devices(self):
        if self.sim_mode:
            return [{'name': 'OBD2 Simulator', 'address': '00:11:22:33:44:55'}]
        
        if not self.bluetooth_available:
            return []
        try:
            adapter = self.BluetoothAdapter.getDefaultAdapter()
            if adapter is None or not adapter.isEnabled():
                return []
            devices = adapter.getBondedDevices()
            device_list = []
            for i in range(devices.size()):
                device = devices.get(i)
                device_list.append({
                    'name': device.getName() or "Без имени",
                    'address': device.getAddress(),
                    'device': device
                })
            return device_list
        except:
            return []
    
    def connect(self, address):
        if self.sim_mode:
            return True, "Симуляция подключена"
        
        if not self.bluetooth_available:
            return False, "Bluetooth не доступен"
        try:
            adapter = self.BluetoothAdapter.getDefaultAdapter()
            if adapter is None:
                return False, "Bluetooth не поддерживается"
            if not adapter.isEnabled():
                return False, "Включите Bluetooth"
            
            device = adapter.getRemoteDevice(address)
            if device is None:
                return False, "Устройство не найдено"
            
            uuid = self.UUID.fromString("00001101-0000-1000-8000-00805F9B34FB")
            self.socket = device.createRfcommSocketToServiceRecord(uuid)
            self.socket.connect()
            self.connected = True
            self.device_address = address
            
            self.send_command("ATZ")
            time.sleep(0.5)
            self.send_command("ATE0")
            time.sleep(0.3)
            self.send_command("ATL0")
            time.sleep(0.3)
            self.send_command("ATS0")
            time.sleep(0.3)
            self.send_command("ATSP0")
            time.sleep(0.5)
            
            return True, "Подключено успешно"
        except Exception as e:
            self.connected = False
            return False, f"Ошибка: {str(e)}"
    
    def disconnect(self):
        self.connected = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        self.socket = None
    
    def send_command(self, command):
        if self.sim_mode:
            time.sleep(0.1)
            return "41" + command[2:] + "00"
        
        if not self.connected or not self.socket:
            return None
        try:
            cmd = f"{command}\r".encode('ascii')
            self.socket.send(cmd)
            time.sleep(0.2)
            response = b''
            timeout = time.time() + 2
            while time.time() < timeout:
                try:
                    data = self.socket.recv(1024)
                    if data:
                        response += data
                        if b'\r' in response or b'>' in response:
                            break
                except:
                    break
            if response:
                response_str = response.decode('ascii', errors='ignore')
                lines = response_str.strip().split('\r')
                for line in lines:
                    line = line.strip()
                    if line and len(line) >= 2:
                        parts = re.findall(r'[0-9A-F]{2,}', line)
                        if parts:
                            return parts[0]
                return None
            return None
        except:
            return None
    
    def read_pid(self, pid):
        if self.sim_mode:
            return self.generate_sim_data(pid)
        
        if not self.connected:
            return None
        response = self.send_command(pid)
        if response and len(response) >= 4:
            try:
                return bytes.fromhex(response[:4])
            except:
                return None
        return None
    
    def generate_sim_data(self, pid):
        rpm = 850 + random.randint(-50, 50)
        temp = 85 + random.randint(-5, 10)
        speed = random.randint(0, 60)
        load = 10 + random.randint(0, 50)
        map_press = 35 + random.randint(0, 20)
        throttle = 5 + random.randint(0, 30)
        maf = 5 + random.randint(0, 15)
        o2 = 0.2 + random.random() * 0.6
        fuel = 50 + random.randint(-10, 20)
        runtime = random.randint(100, 3000)
        
        if pid == '010C':
            val = int(rpm * 4)
            return bytes([val >> 8, val & 0xFF])
        elif pid == '0105':
            return bytes([int(temp + 40)])
        elif pid == '010B':
            return bytes([int(map_press / 3)])
        elif pid == '0111':
            return bytes([int(throttle * 255 / 100)])
        elif pid == '0104':
            return bytes([int(load * 255 / 100)])
        elif pid == '010F':
            return bytes([int(25 + 40)])
        elif pid == '0110':
            val = int(maf * 100)
            return bytes([val >> 8, val & 0xFF])
        elif pid == '0114':
            return bytes([int(o2 * 255 / 100)])
        elif pid == '010A':
            return bytes([int(random.randint(200, 400) / 3)])
        elif pid == '012F':
            return bytes([int(fuel * 255 / 100)])
        elif pid == '011F':
            val = int(runtime)
            return bytes([val >> 8, val & 0xFF])
        elif pid == '010D':
            return bytes([int(speed)])
        elif pid == '0113':
            return bytes([int(30 + 40)])
        elif pid == '0109':
            return bytes([int(random.randint(10, 100) / 3)])
        elif pid == '0146':
            return bytes([int(22 + 40)])
        return bytes([0])
    
    def get_rpm(self):
        data = self.read_pid('010C')
        if data and len(data) >= 2:
            return (data[0] * 256 + data[1]) / 4
        return None
    
    def get_coolant_temp(self):
        data = self.read_pid('0105')
        if data and len(data) >= 1:
            return data[0] - 40
        return None
    
    def get_map_pressure(self):
        data = self.read_pid('010B')
        if data and len(data) >= 1:
            return data[0] * 3
        return None
    
    def get_throttle_position(self):
        data = self.read_pid('0111')
        if data and len(data) >= 1:
            return data[0] * 100 / 255
        return None
    
    def get_engine_load(self):
        data = self.read_pid('0104')
        if data and len(data) >= 1:
            return data[0] * 100 / 255
        return None
    
    def get_air_temp(self):
        data = self.read_pid('010F')
        if data and len(data) >= 1:
            return data[0] - 40
        return None
    
    def get_maf_flow(self):
        data = self.read_pid('0110')
        if data and len(data) >= 2:
            return (data[0] * 256 + data[1]) / 100
        return None
    
    def get_oxygen_sensor(self):
        data = self.read_pid('0114')
        if data and len(data) >= 1:
            return data[0] * 100 / 255
        return None
    
    def get_fuel_pressure(self):
        data = self.read_pid('010A')
        if data and len(data) >= 1:
            return data[0] * 3
        return None
    
    def get_fuel_level(self):
        data = self.read_pid('012F')
        if data and len(data) >= 1:
            return data[0] * 100 / 255
        return None
    
    def get_engine_runtime(self):
        data = self.read_pid('011F')
        if data and len(data) >= 2:
            return (data[0] * 256 + data[1])
        return None
    
    def get_speed(self):
        data = self.read_pid('010D')
        if data and len(data) >= 1:
            return data[0]
        return None
    
    def get_intake_temp(self):
        data = self.read_pid('0113')
        if data and len(data) >= 1:
            return data[0] - 40
        return None
    
    def get_absolute_pressure(self):
        data = self.read_pid('0109')
        if data and len(data) >= 1:
            return data[0] * 3
        return None
    
    def get_ambient_temp(self):
        data = self.read_pid('0146')
        if data and len(data) >= 1:
            return data[0] - 40
        return None

class SpeedometerWidget(BoxLayout):
    """Спидометр для отображения RPM и скорости"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = 140
        self.padding = [5, 5]
        self.spacing = 5
        
        # RPM
        rpm_layout = BoxLayout(orientation='vertical', size_hint_y=0.5, spacing=2)
        rpm_layout.add_widget(Label(text='ОБОРОТЫ', color=COLORS['text_secondary'], 
                                   font_size=10, halign='center'))
        
        self.rpm_label = Label(text='0 RPM', color=COLORS['cyan'], 
                              font_size=20, bold=True, halign='center')
        rpm_layout.add_widget(self.rpm_label)
        
        self.rpm_bar = ProgressBar(max=8000, value=0, size_hint_y=None, height=6)
        self.rpm_bar.background_color = COLORS['gray']
        rpm_layout.add_widget(self.rpm_bar)
        
        self.add_widget(rpm_layout)
        
        # Скорость
        speed_layout = BoxLayout(orientation='vertical', size_hint_y=0.5, spacing=2)
        speed_layout.add_widget(Label(text='СКОРОСТЬ', color=COLORS['text_secondary'], 
                                    font_size=10, halign='center'))
        
        self.speed_label = Label(text='0 km/h', color=COLORS['green'], 
                               font_size=20, bold=True, halign='center')
        speed_layout.add_widget(self.speed_label)
        
        self.speed_bar = ProgressBar(max=200, value=0, size_hint_y=None, height=6)
        self.speed_bar.background_color = COLORS['gray']
        speed_layout.add_widget(self.speed_bar)
        
        self.add_widget(speed_layout)
    
    def update(self, rpm, speed):
        if rpm is not None:
            self.rpm_label.text = f'{int(rpm)} RPM'
            self.rpm_bar.value = min(rpm, 8000)
            if rpm < 700 or rpm > 900:
                self.rpm_label.color = COLORS['yellow']
            else:
                self.rpm_label.color = COLORS['cyan']
        
        if speed is not None:
            self.speed_label.text = f'{int(speed)} km/h'
            self.speed_bar.value = min(speed, 200)
            if speed > 120:
                self.speed_label.color = COLORS['red']
            else:
                self.speed_label.color = COLORS['green']

class ParamCard(BoxLayout):
    """Карточка параметра для телефона"""
    name = StringProperty('')
    unit = StringProperty('')
    icon = StringProperty('')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = 65
        self.padding = [4, 2]
        self.spacing = 1
        
        with self.canvas.before:
            Color(*COLORS['card'])
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(pos=self.update_rect, size=self.update_rect)
        
        # Верхняя часть: иконка и значение
        top = BoxLayout(size_hint_y=None, height=25, spacing=3)
        
        # Иконка и название
        left = BoxLayout(size_hint_x=0.55)
        self.icon_label = Label(text=self.icon, color=COLORS['text'], 
                              font_size=14, halign='center', size_hint_x=0.25)
        self.name_label = Label(text=self.name, color=COLORS['text_secondary'], 
                              font_size=10, halign='left', bold=True)
        left.add_widget(self.icon_label)
        left.add_widget(self.name_label)
        top.add_widget(left)
        
        # Значение
        self.value_label = Label(text='---', color=COLORS['text'], 
                               font_size=14, bold=True, halign='right', size_hint_x=0.45)
        top.add_widget(self.value_label)
        self.add_widget(top)
        
        # Прогресс-бар
        self.progress = ProgressBar(max=100, value=0, size_hint_y=None, height=4)
        self.progress.background_color = COLORS['gray']
        self.add_widget(self.progress)
        
        # Единицы измерения
        self.unit_label = Label(text=self.unit, color=COLORS['text_secondary'], 
                              font_size=8, halign='right', size_hint_y=None, height=10)
        self.add_widget(self.unit_label)
    
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
    
    def set_value(self, val, min_val=0, max_val=100):
        if val is None:
            self.value_label.text = '---'
            self.value_label.color = COLORS['text_secondary']
            self.progress.value = 0
            self.progress.background_color = COLORS['gray']
            return
        
        self.value_label.text = f'{val:.1f}'
        self.value_label.color = COLORS['text']
        
        # Нормализация для прогресс-бара
        norm_val = (val - min_val) / (max_val - min_val) * 100
        self.progress.value = min(max(norm_val, 0), 100)
        
        # Цвет в зависимости от значения
        if 20 <= norm_val <= 80:
            self.progress.background_color = COLORS['green']
        elif norm_val < 20:
            self.progress.background_color = COLORS['yellow']
        else:
            self.progress.background_color = COLORS['red']

class OBD2App(App):
    def build(self):
        # Оптимизация под телефон
        Window.fullscreen = True
        
        self.obd = OBD2Real()
        self.running = False
        self.results = []
        self.devices = []
        self.selected_device = None
        self.read_count = 0
        self.popup_to_close = None
        self.sim_mode = False
        
        # Основной контейнер
        main = BoxLayout(orientation='vertical', padding=3, spacing=3)
        
        # Заголовок
        header = BoxLayout(size_hint_y=None, height=40, padding=[5, 5])
        header.add_widget(Label(text='🚗 OBD2 ВАЗ', font_size=18, 
                               color=COLORS['text'], bold=True))
        
        self.status = Label(text='⚪ Отключено', color=COLORS['red'], 
                          font_size=11, size_hint_x=0.4)
        header.add_widget(self.status)
        main.add_widget(header)
        
        # Переключатель симуляции
        sim_layout = BoxLayout(size_hint_y=None, height=28, padding=[5, 2])
        sim_layout.add_widget(Label(text='🎮 Симуляция', color=COLORS['text_secondary'], 
                                  font_size=11, size_hint_x=0.5))
        
        self.sim_switch = Switch(active=False, size_hint_x=0.2)
        self.sim_switch.bind(active=self.on_sim_switch)
        sim_layout.add_widget(self.sim_switch)
        
        self.sim_status = Label(text='ВЫКЛ', color=COLORS['gray'], 
                               font_size=10, bold=True, size_hint_x=0.2)
        sim_layout.add_widget(self.sim_status)
        main.add_widget(sim_layout)
        
        # Спидометр
        self.speedometer = SpeedometerWidget()
        main.add_widget(self.speedometer)
        
        # Кнопки управления
        btns = BoxLayout(size_hint_y=None, height=38, spacing=3, padding=[2, 2])
        
        self.btn_scan = Button(text='🔍 Поиск', font_size=10,
                             background_color=COLORS['blue'])
        self.btn_scan.bind(on_press=self.scan_devices)
        btns.add_widget(self.btn_scan)
        
        self.btn_connect = Button(text='🔗 Подкл.', font_size=10,
                                background_color=COLORS['green'])
        self.btn_connect.bind(on_press=self.connect_device)
        self.btn_connect.disabled = True
        btns.add_widget(self.btn_connect)
        
        self.btn_start = Button(text='▶ Старт', font_size=10,
                              background_color=COLORS['orange'])
        self.btn_start.bind(on_press=self.start)
        self.btn_start.disabled = True
        btns.add_widget(self.btn_start)
        
        self.btn_stop = Button(text='⏹ Стоп', font_size=10,
                             background_color=COLORS['red'])
        self.btn_stop.bind(on_press=self.stop)
        self.btn_stop.disabled = True
        btns.add_widget(self.btn_stop)
        
        main.add_widget(btns)
        
        # Сетка параметров (2 колонки)
        grid = GridLayout(cols=2, spacing=3, size_hint_y=None, padding=[2, 2])
        grid.bind(minimum_height=grid.setter('height'))
        
        self.params = {}
        self.param_configs = [
            ('RPM', 'Обороты', '⚡', 0, 8000),
            ('LOAD', 'Нагрузка', '📈', 0, 100),
            ('TEMP', 'Температура', '🌡', -40, 150),
            ('AIR_TEMP', 'Темп. воздуха', '🌤', -40, 100),
            ('MAP', 'Давление', '💨', 0, 1000),
            ('ABS_PRESS', 'Абс. давление', '🌪', 0, 1000),
            ('FUEL_PRESS', 'Давл. топлива', '⛽', 0, 1000),
            ('THROT', 'Дроссель', '🔧', 0, 100),
            ('MAF', 'Расход воздуха', '💨', 0, 100),
            ('O2', 'Кислород', '🔬', 0, 100),
            ('FUEL_LEVEL', 'Уровень топлива', '⛽', 0, 100),
            ('SPEED', 'Скорость', '🏎', 0, 250),
            ('RUNTIME', 'Время работы', '⏱', 0, 6000),
            ('INTAKE_TEMP', 'Темп. впуска', '🌡', -40, 150),
            ('AMBIENT_TEMP', 'Темп. окр.', '🌡', -40, 100),
            ('RPM2', 'Обороты 2', '⚡', 0, 8000),
        ]
        
        self.units = {
            'RPM': 'об/мин', 'LOAD': '%', 'TEMP': '°C', 'AIR_TEMP': '°C',
            'MAP': 'mBar', 'ABS_PRESS': 'mBar', 'FUEL_PRESS': 'kPa',
            'THROT': '%', 'MAF': 'g/s', 'O2': '%', 'FUEL_LEVEL': '%',
            'SPEED': 'км/ч', 'RUNTIME': 'сек', 'INTAKE_TEMP': '°C',
            'AMBIENT_TEMP': '°C', 'RPM2': 'об/мин'
        }
        
        for key, name, icon, min_val, max_val in self.param_configs:
            w = ParamCard(name=name, icon=icon, unit=self.units.get(key, ''))
            w.min_val = min_val
            w.max_val = max_val
            grid.add_widget(w)
            self.params[key] = w
        
        scroll = ScrollView(size_hint_y=0.4)
        scroll.add_widget(grid)
        main.add_widget(scroll)
        
        # Лог
        self.log = TextInput(text='📋 Готов к работе\n', 
                           readonly=True,
                           background_color=COLORS['card'], 
                           foreground_color=COLORS['text_secondary'],
                           size_hint_y=0.1, font_size=9,
                           multiline=False)
        main.add_widget(self.log)
        
        # Нижняя панель
        bottom = BoxLayout(size_hint_y=None, height=32, spacing=3, padding=[2, 2])
        
        diag_btn = Button(text='🔍 Диагностика', font_size=10,
                         background_color=COLORS['purple'])
        diag_btn.bind(on_press=self.show_diagnostic)
        bottom.add_widget(diag_btn)
        
        info_btn = Button(text='ℹ️ О программе', font_size=10,
                         background_color=COLORS['gray'])
        info_btn.bind(on_press=self.show_info)
        bottom.add_widget(info_btn)
        
        main.add_widget(bottom)
        
        return main
    
    def on_sim_switch(self, instance, value):
        self.sim_mode = value
        self.obd.set_sim_mode(value)
        
        if value:
            self.sim_status.text = 'ВКЛ'
            self.sim_status.color = COLORS['sim_mode']
            self.status.text = '🎮 СИМУЛЯЦИЯ'
            self.status.color = COLORS['sim_mode']
            self.btn_start.disabled = False
            self.btn_connect.disabled = True
            self.btn_scan.disabled = True
            self.log.text = '🎮 Режим симуляции\n▶ Нажмите "Старт"'
            self.selected_device = {'name': 'OBD2 Simulator', 'address': 'SIM'}
            self.obd.connected = True
            self.show_popup('🎮 Симуляция', 'Режим симуляции включен\n\nДанные генерируются автоматически')
        else:
            self.sim_status.text = 'ВЫКЛ'
            self.sim_status.color = COLORS['gray']
            self.obd.connected = False
            self.status.text = '⚪ Отключено'
            self.status.color = COLORS['red']
            self.btn_start.disabled = True
            self.btn_connect.disabled = True
            self.btn_scan.disabled = False
            self.log.text = '📋 Готов к работе'
            self.obd.disconnect()
        
        for key in self.params:
            self.params[key].set_value(None)
        self.speedometer.update(None, None)
    
    def scan_devices(self, instance):
        if self.sim_mode:
            return
        
        self.log.text = '🔍 Поиск устройств...'
        self.btn_connect.disabled = True
        
        devices = self.obd.get_devices()
        
        if not devices:
            self.log.text = '❌ Устройства не найдены'
            self.show_popup('Ошибка', 'Устройства не найдены\n\nВключите Bluetooth и\nсопрягите OBD2 адаптер')
            return
        
        self.devices = devices
        self.log.text = f'✅ Найдено: {len(devices)}'
        
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text='Выберите адаптер:', color=COLORS['text'], font_size=14))
        
        scroll = ScrollView()
        list_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=5)
        list_layout.bind(minimum_height=list_layout.setter('height'))
        
        for device in devices:
            btn_text = f"{device['name']}\n{device['address']}"
            btn = Button(text=btn_text, size_hint_y=None, height=50, 
                        background_color=COLORS['blue'], font_size=10)
            btn.bind(on_press=lambda x, d=device: self.select_device(d))
            list_layout.add_widget(btn)
        
        scroll.add_widget(list_layout)
        content.add_widget(scroll)
        
        popup = Popup(title='📡 Устройства', content=content, 
                     size_hint=(0.9, 0.7))
        self.popup_to_close = popup
        popup.open()
    
    def select_device(self, device):
        self.selected_device = device
        self.btn_connect.disabled = False
        self.log.text = f'✅ {device["name"][:15]}'
        self.status.text = f'✅ {device["name"][:12]}'
        self.status.color = COLORS['green']
        
        if self.popup_to_close:
            self.popup_to_close.dismiss()
            self.popup_to_close = None
    
    def connect_device(self, instance):
        if self.sim_mode:
            return
        
        if not self.selected_device:
            self.show_popup('Ошибка', 'Сначала выберите устройство')
            return
        
        self.status.text = '⏳ Подключение...'
        self.status.color = COLORS['yellow']
        self.btn_connect.disabled = True
        
        def connect_thread():
            success, message = self.obd.connect(self.selected_device['address'])
            Clock.schedule_once(lambda dt: self.connect_callback(success, message))
        
        thread = threading.Thread(target=connect_thread)
        thread.daemon = True
        thread.start()
    
    def connect_callback(self, success, message):
        if success:
            self.status.text = '✅ Подключено'
            self.status.color = COLORS['green']
            self.btn_start.disabled = False
            self.log.text = '✅ Подключено'
            self.show_popup('Успех', 'Подключено к OBD2 адаптеру')
        else:
            self.status.text = '❌ Ошибка'
            self.status.color = COLORS['red']
            self.btn_connect.disabled = False
            self.log.text = f'❌ {message[:20]}'
            self.show_popup('Ошибка', message)
    
    def start(self, instance):
        if not self.obd.connected and not self.sim_mode:
            self.show_popup('Ошибка', 'Нет подключения к OBD2')
            return
        
        self.running = True
        self.btn_start.disabled = True
        self.btn_stop.disabled = False
        self.results = []
        self.read_count = 0
        
        if self.sim_mode:
            self.status.text = '🎮 Симуляция'
            self.status.color = COLORS['sim_mode']
            self.log.text = '🎮 Запущена симуляция'
        else:
            self.status.text = '🟢 Чтение...'
            self.status.color = COLORS['green']
            self.log.text = '📊 Чтение данных...'
        
        self.thread = threading.Thread(target=self.read_loop)
        self.thread.daemon = True
        self.thread.start()
    
    def stop(self, instance):
        self.running = False
        self.btn_start.disabled = False
        self.btn_stop.disabled = True
        
        if self.sim_mode:
            self.status.text = '🎮 Симуляция'
            self.status.color = COLORS['sim_mode']
        else:
            self.status.text = '⏸ Остановлено'
            self.status.color = COLORS['yellow']
        
        if hasattr(self, 'thread'):
            self.thread.join(timeout=1)
        
        self.log.text = '⏸ Чтение остановлено'
    
    def read_loop(self):
        while self.running:
            try:
                data = {
                    'RPM': self.obd.get_rpm(),
                    'LOAD': self.obd.get_engine_load(),
                    'TEMP': self.obd.get_coolant_temp(),
                    'AIR_TEMP': self.obd.get_air_temp(),
                    'MAP': self.obd.get_map_pressure(),
                    'ABS_PRESS': self.obd.get_absolute_pressure(),
                    'FUEL_PRESS': self.obd.get_fuel_pressure(),
                    'THROT': self.obd.get_throttle_position(),
                    'MAF': self.obd.get_maf_flow(),
                    'O2': self.obd.get_oxygen_sensor(),
                    'FUEL_LEVEL': self.obd.get_fuel_level(),
                    'SPEED': self.obd.get_speed(),
                    'RUNTIME': self.obd.get_engine_runtime(),
                    'INTAKE_TEMP': self.obd.get_intake_temp(),
                    'AMBIENT_TEMP': self.obd.get_ambient_temp(),
                    'RPM2': self.obd.get_rpm(),
                }
                
                self.read_count += 1
                Clock.schedule_once(lambda dt, d=data: self.update_ui(d))
                
                if self.sim_mode:
                    time.sleep(0.3)
                else:
                    time.sleep(0.5)
                
            except Exception as e:
                print(f"Ошибка: {e}")
                time.sleep(1)
    
    def update_ui(self, data):
        # Обновление спиидометра
        rpm = data.get('RPM')
        speed = data.get('SPEED')
        self.speedometer.update(rpm, speed)
        
        # Обновление карточек
        for key, value in data.items():
            if key in self.params:
                param = self.params[key]
                min_val = getattr(param, 'min_val', 0)
                max_val = getattr(param, 'max_val', 100)
                param.set_value(value, min_val, max_val)
        
        # Сбор диагностики (только не в симуляции)
        if not self.sim_mode:
            if rpm is not None:
                if rpm < 700:
                    self.results.append('⚠️ Низкие обороты ХХ')
                elif rpm > 900:
                    self.results.append('⚠️ Высокие обороты ХХ')
            
            temp = data.get('TEMP')
            if temp is not None:
                if temp > 105:
                    self.results.append('⚠️ Перегрев двигателя')
                elif temp < 70:
                    self.results.append('⚠️ Двигатель не прогрет')
            
            map_press = data.get('MAP')
            if map_press is not None and rpm is not None:
                if map_press > 500 and rpm < 1000:
                    self.results.append('⚠️ Подсос воздуха')
            
            throttle = data.get('THROT')
            if throttle is not None:
                if throttle > 80:
                    self.results.append('⚠️ Дроссель открыт сильно')
            
            load = data.get('LOAD')
            if load is not None and rpm is not None:
                if load > 80 and rpm > 2000:
                    self.results.append('⚠️ Высокая нагрузка')
            
            if speed is not None and speed > 120:
                self.results.append('⚠️ Превышение скорости')
            
            fuel = data.get('FUEL_LEVEL')
            if fuel is not None and fuel < 10:
                self.results.append('⚠️ Низкий уровень топлива')
    
    def show_diagnostic(self, instance=None):
        if not self.results:
            self.show_popup('📋 Диагностика', '✅ Проблем не обнаружено!\nВсе параметры в норме.')
            return
        
        unique = list(dict.fromkeys(self.results))
        
        text = '🔍 РЕЗУЛЬТАТЫ ДИАГНОСТИКИ:\n\n'
        for i, res in enumerate(unique[:15], 1):
            text += f'{i}. {res}\n'
        
        if len(unique) > 15:
            text += f'\n... и еще {len(unique)-15} проблем'
        
        text += '\n💡 РЕКОМЕНДАЦИИ:\n'
        for res in unique:
            if 'Перегрев' in res:
                text += '• Проверьте охлаждающую жидкость\n'
                text += '• Проверьте вентилятор\n'
            elif 'обороты' in res or 'RPM' in res:
                text += '• Проверьте дроссельную заслонку\n'
                text += '• Проверьте датчик ХХ\n'
            elif 'Подсос' in res:
                text += '• Проверьте вакуумные шланги\n'
                text += '• Проверьте прокладку коллектора\n'
            elif 'Дроссель' in res:
                text += '• Проверьте трос газа\n'
                text += '• Проверьте датчик дросселя\n'
            elif 'Нагрузка' in res:
                text += '• Проверьте топливную систему\n'
                text += '• Проверьте зажигание\n'
            elif 'Скорость' in res:
                text += '• Соблюдайте скоростной режим\n'
            elif 'топлива' in res:
                text += '• Заправьте автомобиль\n'
        
        self.show_popup('📋 Диагностика', text)
        self.results = []
    
    def show_info(self, instance=None):
        info = '🚗 OBD2 Диагностика ВАЗ\n\n'
        info += 'Версия: 2.0\n'
        info += 'Для телефонов\n\n'
        info += 'Поддерживает:\n'
        info += '• ELM327 (Bluetooth)\n'
        info += '• 16 параметров\n'
        info += '• Режим симуляции\n'
        info += '• Диагностика неисправностей\n\n'
        info += 'Разработано для Pydroid 3'
        self.show_popup('ℹ️ О программе', info)
    
    def show_popup(self, title, message):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        scroll = ScrollView()
        label = Label(text=message, color=COLORS['text'], size_hint_y=None,
                     text_size=(350, None))
        label.bind(texture_size=label.setter('size'))
        scroll.add_widget(label)
        content.add_widget(scroll)
        
        btn = Button(text='OK', size_hint_y=None, height=45,
                    background_color=COLORS['blue'])
        popup = Popup(title=title, content=content, size_hint=(0.9, 0.7))
        btn.bind(on_press=popup.dismiss)
        content.add_widget(btn)
        
        popup.open()
    
    def on_stop(self):
        self.running = False
        if hasattr(self, 'obd'):
            self.obd.disconnect()

if __name__ == '__main__':
    OBD2App().run()