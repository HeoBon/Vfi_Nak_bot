import os
import json
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button

class HistoryViewScreen(Screen):
    def on_enter(self):
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', spacing=10, padding=20)

        # Пошукові поля
        search_box = BoxLayout(size_hint_y=None, height=40, spacing=10)
        self.name_input = TextInput(hint_text="Пошук по імені", multiline=False)
        self.date_input = TextInput(hint_text="Пошук по даті", multiline=False)
        self.name_input.bind(text=self.update_history_list)
        self.date_input.bind(text=self.update_history_list)
        search_box.add_widget(self.name_input)
        search_box.add_widget(self.date_input)
        self.sum_input = TextInput(hint_text="Пошук по сумі", multiline=False)
        self.sum_input.bind(text=self.update_history_list)
        search_box.add_widget(self.sum_input)
        layout.add_widget(search_box)

        # Контейнер для історії
        self.history_layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.history_layout.bind(minimum_height=self.history_layout.setter('height'))

        scroll = ScrollView()
        scroll.size_hint_y = 1
        scroll.do_scroll_x = False
        scroll.do_scroll_y = True
        scroll.add_widget(self.history_layout)
        layout.add_widget(scroll)

        # Назад
        back_btn = Button(text="← Назад", size_hint_y=None, height=40)
        back_btn.bind(on_release=self.go_to_main_menu)
        layout.add_widget(back_btn)

        self.add_widget(layout)
        self.update_history_list()

    def go_to_main_menu(self, instance):
        self.manager.current = 'main_menu'

    def update_history_list(self, *args):
        if not hasattr(self, 'history_layout'):
            return
        self.history_layout.clear_widgets()
        history = []
        os.makedirs("data", exist_ok=True)
        if not os.path.exists("data/history.json"):
            with open("data/history.json", "w") as f:
                json.dump([], f)
        if os.path.exists("data/history.json"):
            with open("data/history.json", "r") as f:
                try:
                    history = json.load(f)
                except json.JSONDecodeError:
                    history = []

        name_filter = self.name_input.text.lower().strip() if hasattr(self, 'name_input') else ""
        date_filter = self.date_input.text.strip() if hasattr(self, 'date_input') else ""
        sum_filter = self.sum_input.text.strip() if hasattr(self, 'sum_input') else ""

        found = False
        for record in history:
            name = str(record.get("client", "")).lower()
            date = str(record.get("date", ""))
            total = str(record.get("total", ""))

            if name_filter and name_filter not in name:
                continue
            if date_filter and date_filter not in date:
                continue
            if sum_filter:
                if sum_filter not in total:
                    continue

            found = True
            lbl = Label(text=f"{date} — {record.get('client', '')} — {total} грн", size_hint_y=None, height=30)
            self.history_layout.add_widget(lbl)

        if not found:
            self.history_layout.add_widget(Label(text="Нічого не знайдено", size_hint_y=None, height=30))
