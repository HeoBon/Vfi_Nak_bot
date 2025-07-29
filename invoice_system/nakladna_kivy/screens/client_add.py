import json
import os.path
from kivy.uix.screenmanager import Screen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField

class ClientAddScreen(Screen):
    def on_enter(self):
        self.clear_widgets()
        self.size_hint = (1, 1)
        self.client_type = 'фіз'  # тип за замовчуванням
        layout = MDBoxLayout(
            orientation='vertical',
            padding=40,
            spacing=30,
            size_hint=(1, 1)
        )

        self.name_input = MDTextField(
            hint_text="Ім'я клієнта",
            font_size=20,
            size_hint_y=None,
            height=70
        )
        self.price_type_input = MDTextField(
            hint_text="Тип ціни (PM, PL, PSS...)",
            font_size=20,
            size_hint_y=None,
            height=70
        )
        layout.add_widget(self.name_input)
        layout.add_widget(self.price_type_input)

        # Перемикач типу клієнта
        type_layout = MDBoxLayout(size_hint=(1, None), height=70, spacing=20)
        fiz_btn = MDButton(MDButtonText(text="Фіз. особа"), font_size=22, size_hint=(0.5, None), height=70)
        yur_btn = MDButton(MDButtonText(text="Юр. особа"), font_size=22, size_hint=(0.5, None), height=70)
        fiz_btn.md_bg_color = (0.2, 0.6, 1, 1)
        yur_btn.md_bg_color = (0.6, 0.6, 0.6, 1)
        fiz_btn.bind(on_release=lambda x: self.set_client_type_button('фіз', fiz_btn, yur_btn))
        yur_btn.bind(on_release=lambda x: self.set_client_type_button('юр', fiz_btn, yur_btn))

        type_layout.add_widget(fiz_btn)
        type_layout.add_widget(yur_btn)
        layout.add_widget(type_layout)

        self.phone_input = MDTextField(
            hint_text="Телефон (для фіз. осіб)",
            font_size=20,
            size_hint_y=None,
            height=70
        )
        self.edrpou_input = MDTextField(
            hint_text="ЄДРПОУ (для юр. осіб)",
            font_size=20,
            size_hint_y=None,
            height=70
        )
        layout.add_widget(self.phone_input)
        layout.add_widget(self.edrpou_input)

        save_button = MDButton(
            MDButtonText(text="💾 Зберегти"),
            font_size=22,
            md_bg_color=(0.3, 0.6, 1, 1),
            size_hint=(1, None),
            height=70
        )
        save_button.bind(on_release=self.save_client)
        layout.add_widget(save_button)

        back_button = MDButton(
            MDButtonText(text="← Назад"),
            font_size=22,
            md_bg_color=(1, 0.3, 0.3, 1),
            size_hint=(1, None),
            height=70
        )
        back_button.bind(on_release=self.go_back)
        layout.add_widget(back_button)

        self.add_widget(layout)

    def set_client_type_button(self, client_type, fiz_btn, yur_btn):
        self.client_type = client_type
        if client_type == 'фіз':
            fiz_btn.md_bg_color = (0.2, 0.6, 1, 1)
            yur_btn.md_bg_color = (0.6, 0.6, 0.6, 1)
        else:
            fiz_btn.md_bg_color = (0.6, 0.6, 0.6, 1)
            yur_btn.md_bg_color = (0.2, 0.6, 1, 1)

    def set_client_type(self, client_type):
        self.client_type = client_type

    def save_client(self, instance):
        name = self.name_input.text.strip()
        price_type = self.price_type_input.text.strip()
        phone = self.phone_input.text.strip()
        edrpou = self.edrpou_input.text.strip()

        if not name or not price_type:
            print("Будь ласка, введіть ім’я та тип ціни.")
            return

        client = {'name': name, 'price_type': price_type, 'type': self.client_type}

        if self.client_type == 'фіз':
            client['phone'] = phone
        elif self.client_type == 'юр':
            client['edrpou'] = edrpou

        clients = self.load_clients()
        clients.append(client)

        with open("data/clients.json", "w", encoding="utf-8") as f:
            json.dump(clients, f, ensure_ascii=False, indent=2)

        print(f"Клієнт збережено: {client}")
        self.name_input.text = ""
        self.price_type_input.text = ""
        self.phone_input.text = ""
        self.edrpou_input.text = ""

    def load_clients(self):
        if os.path.exists("data/clients.json"):
            with open("data/clients.json", "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def go_back(self, instance):
        self.manager.current = 'main_menu'


if __name__ == '__main__':
    print("Цей файл не слід запускати напряму. Запусти main.py")