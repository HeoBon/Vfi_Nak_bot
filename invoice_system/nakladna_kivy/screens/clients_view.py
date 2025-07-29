import os
import json
from kivy.uix.screenmanager import Screen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton
from kivymd.uix.list import MDListItem, MDListItemHeadlineText, MDListItemSupportingText
from kivymd.uix.card import MDCard

class ClientsViewScreen(Screen):
    def on_enter(self):
        self.clear_widgets()

        self.layout = MDBoxLayout(orientation='vertical', spacing=20, padding=20)
        self.search_input = MDTextField(
            hint_text="Пошук за ім’ям...",
            font_size=20,
            size_hint_y=None,
            height=70,
            mode="rectangle",
        )
        self.search_input.bind(text=self.update_client_list)
        self.layout.add_widget(self.search_input)

        self.clients_list_layout = MDBoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        self.clients_list_layout.bind(minimum_height=self.clients_list_layout.setter('height'))

        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(self.clients_list_layout)
        self.layout.add_widget(scroll)

        btn_layout = MDBoxLayout(size_hint_y=None, height=120, spacing=10)

        back_card = MDCard(orientation="vertical", size_hint=(1, 1), padding=10, md_bg_color=(0.86, 0.2, 0.2, 1))
        back_icon = MDIconButton(icon="arrow-left", text_color=(1, 1, 1, 1), pos_hint={"center_x": 0.5})
        back_label = MDLabel(text="← Назад", halign="center", font_name="Roboto", font_size=18, text_color=(1, 1, 1, 1))
        back_card.add_widget(back_icon)
        back_card.add_widget(back_label)
        back_card.bind(on_release=self.go_back)

        btn_layout.add_widget(back_card)
        self.layout.add_widget(btn_layout)

        self.add_widget(self.layout)

        self.clients = self.load_clients()
        print("on_enter виконано, clients завантажено:", self.clients)
        self.update_client_list()

    def update_client_list(self, *args):
        search_query = self.search_input.text.lower() if hasattr(self, 'search_input') else ''
        self.clients_list_layout.clear_widgets()
        print("Очищено layout клієнтів, кількість клієнтів у self.clients:", len(self.clients))
        print("Пошуковий запит:", search_query)

        filtered_clients = []
        for c in self.clients:
            name = c.get('name', '').lower()
            phone = c.get('phone', '').lower()
            edrpou = c.get('edrpou', '').lower()
            if search_query in name or search_query in phone or search_query in edrpou:
                filtered_clients.append(c)
        filtered_clients.sort(key=lambda c: c.get('type', ''))

        print("Знайдено клієнтів:", len(filtered_clients))
        if not filtered_clients:
            item = MDListItem(
                MDListItemHeadlineText(text="Клієнтів не знайдено")
            )
            self.clients_list_layout.add_widget(item)
        else:
            for client in filtered_clients:
                name = client.get('name', 'Невідомо')
                type_ = client.get('type', 'невідомо')
                price_type = client.get('price_type', '-')
                extra_info = client.get('edrpou') if type_ == 'юр' else client.get('phone', '-')

                item = MDListItem(
                    MDListItemHeadlineText(text=name),
                    MDListItemSupportingText(text=f"Тип: {type_} | {extra_info} | Ціна: {price_type}")
                )
                self.clients_list_layout.add_widget(item)

    def go_back(self, instance):
        self.manager.current = 'main_menu'

    def load_clients(self):
        client_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'clients.json')
        if os.path.exists(client_file):
            with open(client_file, "r", encoding="utf-8") as f:
                clients = json.load(f)
            print("Шлях до файлу клієнтів:", client_file)
            print("Кількість клієнтів у файлі:", len(clients))
            return clients
        print("Файл клієнтів не знайдено.")
        return []
