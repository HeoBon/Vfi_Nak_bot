from kivy.config import Config
Config.set('graphics', 'multisamples', '0')
from kivy.animation import Animation
Animation._default_transition = 'linear'
Animation._default_duration = 0.0

from kivy.uix.screenmanager import Screen
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel

class ProductsViewScreen(Screen):
    def on_enter(self):
        from kivy.uix.boxlayout import BoxLayout
        # from kivy.uix.textinput import TextInput
        from kivy.uix.spinner import Spinner
        from kivy.uix.scrollview import ScrollView
        from kivy.core.window import Window
        from kivymd.uix.card import MDCard
        from kivymd.uix.button import MDIconButton
        from kivymd.uix.label import MDLabel

        self.clear_widgets()
        self.products = self.load_products() if hasattr(self, 'load_products') else []

        self.layout = BoxLayout(orientation='vertical', spacing=20, padding=10)
        self.layout.size = Window.size
        self.count_label = Label(text="", size_hint_y=None, height=30)
        self.layout.add_widget(self.count_label)

        from kivymd.uix.menu import MDDropdownMenu
        from kivymd.uix.button import MDRaisedButton

        self.selected_price_type = "Усі типи цін"
        self.price_filter_btn = MDRaisedButton(
            text=self.selected_price_type,
            size_hint=(1, None),
            height=50,
            md_bg_color=(0.92, 0.92, 0.96, 1),
            text_color=(0, 0, 0, 1),
            pos_hint={"center_x": 0.5}
        )

        menu_items = []
        for i in ["Усі типи цін", "PM", "PL", "PSS", "PWS", "PK"]:
            def create_callback(value):
                return lambda *args: self.set_price_filter(value)
            menu_items.append({
                "text": i,
                "viewclass": "OneLineListItem",
                "on_release": create_callback(i)
            })
        self.price_menu = MDDropdownMenu(
            caller=self.price_filter_btn,
            items=menu_items,
            width_mult=4
        )
        self.price_filter_btn.bind(on_release=lambda x: self.price_menu.open())
        self.layout.add_widget(self.price_filter_btn)

        from kivymd.uix.textfield import MDTextField
        self.search_input = MDTextField(
            hint_text="Пошук...",
            font_size=22,
            size_hint_y=None,
            height=70,
            mode="rectangle",
            line_color_normal=(0.7, 0.7, 0.7, 1),
            line_color_focus=(0.3, 0.6, 1, 1)
        )
        self.search_input.bind(text=self.debounce_search)
        self.layout.add_widget(self.search_input)

        self.table_container = ScrollView(size_hint=(1, 1))
        self.layout.add_widget(self.table_container)

        btn_layout = BoxLayout(size_hint_y=None, height=100, spacing=10, padding=(20, 0))
        back_card = MDCard(orientation="vertical", size_hint=(1, 1), padding=10, md_bg_color=(0.86, 0.2, 0.2, 1))
        back_icon = MDIconButton(icon="arrow-left", pos_hint={"center_x": 0.5}, theme_text_color="Custom", text_color=(1, 1, 1, 1))
        back_label = MDLabel(text="← Назад", halign="center", font_name="Roboto", font_size=18, theme_text_color="Custom", text_color=(1, 1, 1, 1))
        back_card.add_widget(back_icon)
        back_card.add_widget(back_label)
        back_card.bind(on_release=lambda x: setattr(self.manager, 'current', 'main_menu'))
        btn_layout.add_widget(back_card)
        self.layout.add_widget(btn_layout)

        self._last_search = ""
        self._last_filter = ""

        self.add_widget(self.layout)
        self.update_table()

    def debounce_search(self, instance, value):
        from kivy.clock import Clock
        if hasattr(self, '_search_event'):
            self._search_event.cancel()
        self._search_event = Clock.schedule_once(lambda dt: self.update_table(), 0.3)

    def update_table(self, *args):
        search = self.search_input.text.strip().lower()
        price_filter = self.selected_price_type

        if self._last_search == search and self._last_filter == price_filter:
            return

        self._last_search = search
        self._last_filter = price_filter

        if not search and price_filter == "Усі типи цін":
            filtered = self.products
        else:
            filtered = [
                p for p in self.products
                if (price_filter == "Усі типи цін" or p.get('price_type', '').upper() == price_filter)
                and (
                    search in p['_name']
                    or search in p['_price']
                    or search in p['_unit']
                    or search in p['_ptype']
                )
            ]

        filtered_total = len(filtered)
        MAX_ROWS = 100
        filtered = filtered[:MAX_ROWS]

        total = len(self.products)
        price_filter_text = f" (Тип ціни: {price_filter})" if price_filter != "Усі типи цін" else ""
        self.count_label.text = f"Знайдено товарів: {filtered_total} із {total}{price_filter_text}"

        self.table_container.clear_widgets()
        content_layout = GridLayout(cols=1, spacing=10, size_hint_y=None, padding=5)
        content_layout.bind(minimum_height=content_layout.setter("height"))

        headers = ["Назва", "Тип ціни", "Ціна", "Одиниця"]
        size_hints = [0.5, 0.15, 0.2, 0.15]
        header_card = MDCard(orientation='horizontal', size_hint_y=None, height=60, padding=10, md_bg_color=(0.75, 0.75, 0.75, 1))
        for i, h in enumerate(headers):
            header_card.add_widget(
                MDLabel(text=h, halign="center", bold=True, theme_text_color="Secondary", size_hint_x=size_hints[i])
            )
        content_layout.add_widget(header_card)

        add_widget = content_layout.add_widget
        for idx, product in enumerate(filtered):
            name = product.get('name', '—')
            price_type = product.get('price_type', '-')
            price = str(product.get('price', '-'))
            unit = product.get('unit', '-')

            row_card = MDCard(
                orientation='horizontal',
                size_hint_y=None,
                height=60,
                padding=10,
                md_bg_color=(0.92, 0.92, 0.96, 1) if idx % 2 == 0 else (0.96, 0.96, 0.98, 1),
                radius=[8, 8, 8, 8]
            )
            values = [name, price_type, price, unit]
            for i, val in enumerate(values):
                lbl = MDLabel(
                    text=val,
                    halign="center",
                    size_hint_x=size_hints[i],
                    theme_text_color="Primary",
                    font_size=17,
                    shorten=True,
                    max_lines=1
                )
                row_card.add_widget(lbl)
            add_widget(row_card)

        self.table_container.add_widget(content_layout)

    def load_products(self):
        import os
        import json
        filepath = 'data/products.json'
        if os.path.exists(filepath):
            print("Файл знайдено:", filepath)
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print("Завантажено товарів:", len(data))
                print("Перший товар:", data[0] if data else "Немає товарів")
                for p in data:
                    p['_name'] = p.get('name', '').lower()
                    p['_unit'] = p.get('unit', '').lower()
                    p['_price'] = str(p.get('price', '')).lower()
                    p['_ptype'] = p.get('price_type', '').lower()
                return data
        else:
            # Повернути тестові дані
            return [
                {"name": "Шампунь Lirio", "price_type": "PM", "price": 71.00, "unit": "шт"},
                {"name": "Мило господарське", "price_type": "PL", "price": 55.00, "unit": "комп"}
            ]
    def set_price_filter(self, value):
        self.selected_price_type = value
        self.price_filter_btn.text = value
        self.price_menu.dismiss()
        self.update_table()