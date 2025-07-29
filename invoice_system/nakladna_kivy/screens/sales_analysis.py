from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button

class SalesAnalysisScreen(Screen):
    def on_enter(self):
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', spacing=10, padding=20)
        layout.add_widget(Label(text="Sales Analysis"))
        back_btn = Button(text="Назад", size_hint_y=None, height=50)
        back_btn.bind(on_release=self.go_to_main_menu)
        layout.add_widget(back_btn)
        self.add_widget(layout)

    def go_to_main_menu(self, instance):
        self.manager.current = 'main_menu'
