try:
    from kivymd.app import MDApp
except ModuleNotFoundError:
    print("❌ Модуль 'kivymd' не знайдено. Активуй середовище або виконай: pip install kivymd")
    raise

from kivymd.uix.screen import MDScreen
from kivy.uix.screenmanager import ScreenManager
from kivymd.uix.label import MDLabel

class MainMenuScreen(MDScreen):
    def on_enter(self):
        self.clear_widgets()
        self.add_widget(MDLabel(text="Привіт! Все працює 👋", halign="center"))

class MainApp(MDApp):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainMenuScreen(name='main_menu'))
        sm.current = 'main_menu'
        return sm

if __name__ == '__main__':
    MainApp().run()