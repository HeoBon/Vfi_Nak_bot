from kivy.uix.screenmanager import Screen
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.core.clipboard import Clipboard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRectangleFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.anchorlayout import MDAnchorLayout
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.button import MDIconButton
from functools import partial

class ProductsBatchScreen(Screen):
    def on_enter(self):
        self.clear_widgets()
        layout = MDBoxLayout(orientation='vertical', spacing=12, padding=16)

        # Container for product input and dropdowns
        input_card = MDCard(md_bg_color=(0.97, 0.97, 0.97, 1), padding=12, size_hint=(1, 0.5), radius=[12, 12, 12, 12])
        input_layout = MDFloatLayout()

        # Product input field
        self.product_input = MDTextField(
            hint_text='Введіть продукцію у форматі: Назва (шт або комп); Ціна\nНаприклад:\nХліб (шт); 25\nЧай (комп); 90',
            size_hint=(0.95, None),
            height=180,
            multiline=True,
            write_tab=True,
            use_handles=True,
            pos_hint={'x': 0, 'top': 1},
            mode='rectangle',
            font_size='14sp',
        )
        self.product_input.bind(on_text=self.format_pasted_text)
        input_layout.add_widget(self.product_input)

        # Price type dropdown field with icon button
        self.price_type_field = MDTextField(
            hint_text="Тип ціни",
            readonly=True,
            size_hint=(0.4, None),
            height=40,
            pos_hint={'x': 0, 'y': 0},
            mode="rectangle",
            font_size='14sp',
            padding=[12, 12, 12, 12],
        )
        input_layout.add_widget(self.price_type_field)

        # VAT dropdown field with icon button
        self.vat_field = MDTextField(
            hint_text="ПДВ",
            readonly=True,
            size_hint=(0.4, None),
            height=40,
            pos_hint={'right': 1, 'y': 0},
            mode="rectangle",
            font_size='14sp',
            padding=[12, 12, 12, 12],
        )
        input_layout.add_widget(self.vat_field)

        # Create dropdown menus after fields exist
        def open_price_type_menu(instance):
            if not hasattr(self, 'price_type_menu') or not self.price_type_menu:
                self.price_type_menu = MDDropdownMenu(
                    caller=self.price_type_field,
                    items=[{"text": i, "on_release": partial(self.set_price_type, i)} for i in ('PM', 'PL', 'PSS', 'PWS', 'PK')],
                )
            self.price_type_menu.caller = self.price_type_field
            self.price_type_menu.open()
        # self.price_type_field.bind(on_focus=lambda instance, value: open_price_type_menu(instance) if value else None)

        price_type_icon = MDIconButton(
            icon="menu-down",
            pos_hint={'right': 0.4, 'y': 0},
            size_hint=(None, None),
            size=(32, 32),
            on_release=lambda _: self.open_price_type_menu()
        )
        input_layout.add_widget(price_type_icon)

        def open_vat_menu(instance):
            if not hasattr(self, 'vat_menu') or not self.vat_menu:
                self.vat_menu = MDDropdownMenu(
                    caller=self.vat_field,
                    items=[{"text": i, "on_release": partial(self.set_vat_type, i)} for i in ('без ПДВ', 'ПДВ 7%', 'ПДВ 20%')],
                )
            self.vat_menu.caller = self.vat_field
            self.vat_menu.open()
        # self.vat_field.bind(on_focus=lambda instance, value: open_vat_menu(instance) if value else None)

        vat_icon = MDIconButton(
            icon="menu-down",
            pos_hint={'right': 1, 'y': 0},
            size_hint=(None, None),
            size=(32, 32),
            on_release=lambda _: self.open_vat_menu()
        )
        input_layout.add_widget(vat_icon)

        input_card.add_widget(input_layout)
        layout.add_widget(input_card)

        paste_button = MDRectangleFlatButton(
            text="Вставити з буфера",
            size_hint=(1, None),
            height=44,
            on_release=self.paste_from_clipboard,
        )
        layout.add_widget(paste_button)

        clear_type_button = MDRectangleFlatButton(
            text="Очистити товари за типом ціни",
            size_hint=(1, None),
            height=44,
            on_release=self.clear_products_by_price_type,
        )
        layout.add_widget(clear_type_button)

        clear_all_button = MDRectangleFlatButton(
            text="Очистити всі товари",
            size_hint=(1, None),
            height=44,
            on_release=self.clear_all_products,
        )
        layout.add_widget(clear_all_button)

        delete_product_button = MDRectangleFlatButton(
            text="Видалити окремий товар",
            size_hint=(1, None),
            height=44,
            on_release=self.delete_single_product,
        )
        layout.add_widget(delete_product_button)

        save_button = MDRectangleFlatButton(
            text="Зберегти",
            size_hint=(1, None),
            height=44,
            on_release=self.save_products,
        )
        layout.add_widget(save_button)

        back_button = MDRectangleFlatButton(
            text="Назад",
            size_hint=(1, None),
            height=44,
            on_release=self.go_back,
        )
        layout.add_widget(back_button)

        scroll_view = ScrollView()
        scroll_view.add_widget(layout)
        self.add_widget(scroll_view)

    def open_price_type_menu(self, *args):
        if not hasattr(self, 'price_type_menu') or not self.price_type_menu:
            self.price_type_menu = MDDropdownMenu(
                caller=self.price_type_field,
                items=[{"text": i, "on_release": partial(self.set_price_type, i)} for i in ('PM', 'PL', 'PSS', 'PWS', 'PK')],
            )
        self.price_type_menu.caller = self.price_type_field
        self.price_type_menu.open()

    def open_vat_menu(self, *args):
        if not hasattr(self, 'vat_menu') or not self.vat_menu:
            self.vat_menu = MDDropdownMenu(
                caller=self.vat_field,
                items=[{"text": i, "on_release": partial(self.set_vat_type, i)} for i in ('без ПДВ', 'ПДВ 7%', 'ПДВ 20%')],
            )
        self.vat_menu.caller = self.vat_field
        self.vat_menu.open()

    def format_pasted_text(self, instance, value):
        lines = value.splitlines()
        formatted = '\n'.join(line.strip() for line in lines if line.strip())
        if instance.text != formatted:
            instance.text = formatted

    def paste_from_clipboard(self, instance):
        pasted_text = Clipboard.paste()
        self.product_input.text += '\n' + pasted_text

    def save_products(self, instance):
        price_type = self.price_type_field.text
        vat_type = self.vat_field.text
        raw_text = self.product_input.text.strip()
        lines = [line.strip() for line in raw_text.splitlines() if line.strip()]

        products = []

        for line in lines:
            try:
                if ';' not in line:
                    continue
                name_part, price_part = line.split(';', 1)
                name_part = name_part.strip()
                price = float(price_part.strip().replace(',', '.'))

                # Очікується формат "Назва (шт)" або "Назва (комп)"
                if '(' in name_part and ')' in name_part:
                    name = name_part[:name_part.rfind('(')].strip()
                    unit = name_part[name_part.rfind('(')+1:name_part.rfind(')')].strip().lower()
                else:
                    name = name_part
                    unit = ''

                if unit not in ['шт', 'комп']:
                    unit = 'шт'

                products.append({
                    'name': name,
                    'price': price,
                    'unit': unit,
                    'price_type': price_type,
                    'vat': vat_type
                })
            except Exception as e:
                print(f"Помилка при обробці рядка '{line}': {e}")

        print("Збережено продукти:", products)

        import json
        import os

        file_path = "data/products.json"
        existing_products = []
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                existing_products = json.load(f)

        # Add all products regardless of duplicates
        existing_products += products

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(existing_products, f, ensure_ascii=False, indent=2)

        self.product_input.text = ''

    def go_back(self, instance):
        self.manager.current = 'main_menu'

    def clear_products_by_price_type(self, instance):
        import json
        import os
        file_path = "data/products.json"
        if not os.path.exists(file_path):
            return
        with open(file_path, "r", encoding="utf-8") as f:
            all_products = json.load(f)
        price_type = self.price_type_field.text
        all_products = [p for p in all_products if p.get('price_type') != price_type]
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(all_products, f, ensure_ascii=False, indent=2)

    def clear_all_products(self, instance):
        import json
        file_path = "data/products.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)
    def delete_single_product(self, instance):
        from kivy.uix.popup import Popup
        from kivy.uix.textinput import TextInput
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.button import Button
        import json
        import os

        box = BoxLayout(orientation='vertical', spacing=10, padding=10)
        input_field = TextInput(hint_text="Введіть точну назву товару для видалення", multiline=False)
        box.add_widget(input_field)

        def confirm_deletion(_):
            name_to_delete = input_field.text.strip().lower()
            file_path = "data/products.json"
            if not os.path.exists(file_path):
                popup.dismiss()
                return
            with open(file_path, "r", encoding="utf-8") as f:
                all_products = json.load(f)
            all_products = [p for p in all_products if p.get('name', '').lower() != name_to_delete]
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(all_products, f, ensure_ascii=False, indent=2)
            popup.dismiss()

        confirm_btn = Button(text="Видалити", size_hint_y=None, height=40)
        confirm_btn.bind(on_release=confirm_deletion)
        box.add_widget(confirm_btn)

        popup = Popup(title="Видалити товар", content=box, size_hint=(0.9, 0.5))
        popup.open()
    def set_price_type(self, value):
        self.price_type_field.text = value
        if hasattr(self, 'price_type_menu') and self.price_type_menu:
            self.price_type_menu.dismiss()

    def set_vat_type(self, value):
        self.vat_field.text = value
        if hasattr(self, 'vat_menu') and self.vat_menu:
            self.vat_menu.dismiss()