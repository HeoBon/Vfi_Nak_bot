from functools import partial
from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivymd.uix.boxlayout import MDBoxLayout

import json
import os
from kivymd.uix.button import MDIconButton
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField

if not os.path.exists("data"):
    os.makedirs("data")
if not os.path.exists("data/invoices.json"):
    with open("data/invoices.json", "w") as f:
        json.dump([], f)

CLIENTS_FILE = "data/clients.json"
PRODUCTS_FILE = "data/products.json"
INVOICES_FILE = "data/invoices.json"

import threading
class InvoiceCreateScreen(Screen):
    selected_client = ObjectProperty(None)
    def __init__(self, **kwargs):
        self.register_event_type('on_selected_client')
        super().__init__(**kwargs)
        self.invoice_drafts = {}
        self._tab_client_map = {}  # tab -> client_id
        self.client_tabs = []
        self.session_file = "data/session_drafts.json"
        self.load_session_drafts()

    def on_selected_client(self, *args):
        pass

    def on_enter(self):
        self.open_client_select_form()

    def open_client_select_form(self):
        # Show a form for searching/selecting client. We use a popup-like layout.
        from kivy.uix.popup import Popup
        box = BoxLayout(orientation="vertical", spacing=10, padding=10)
        search_input = MDTextField(
            hint_text="Введіть ім’я клієнта або ЄДРПОУ",
            font_size=18,
            size_hint_y=None,
            height=60,
            foreground_color=(0, 0, 0, 1),
        )
        result_container = GridLayout(cols=1, spacing=10, size_hint_y=None)
        result_container.bind(minimum_height=result_container.setter("height"))
        scroll = ScrollView(size_hint=(1, 1), size_hint_y=1)
        scroll.add_widget(result_container)
        box.add_widget(search_input)
        box.add_widget(scroll)
        popup = Popup(title="Вибір клієнта", content=box, size_hint=(0.8, 0.6), auto_dismiss=True)

        def search_clients(instance, value):
            result_container.clear_widgets()
            if not os.path.exists(CLIENTS_FILE) or not value.strip():
                return
            with open(CLIENTS_FILE, 'r') as f:
                clients = json.load(f)
            value_lower = value.lower()
            matches = []
            for client in clients:
                text = f"{client.get('name', '')} ({client.get('type', '')}) - {client.get('phone', '') or client.get('edrpou', '')}"
                if value_lower in text.lower():
                    matches.append((client, text))
            if not matches:
                no_result_label = MDLabel(text="Клієнтів не знайдено", halign="center", font_size=18, theme_text_color="Secondary")
                result_container.add_widget(no_result_label)
                return
            if len(matches) == 1:
                self.select_client(matches[0][0])
                popup.dismiss()
                return
            for client, text in matches:
                row_card = MDCard(orientation="horizontal", size_hint_y=None, height=60, padding=10, md_bg_color=(0.95, 0.95, 0.95, 1), radius=[10])
                label = MDLabel(text=text, halign="left", font_size=20, theme_text_color="Primary")
                row_card.add_widget(label)
                def on_sel(inst, c=client):
                    popup.dismiss()
                    self.select_client(c)
                row_card.bind(on_release=on_sel)
                result_container.add_widget(row_card)
        search_input.bind(text=search_clients)
        popup.open()

    def select_client(self, client):
        # Add client as a tab and open ProductSelectScreen for that client
        client_id = client.get("edrpou", client.get("name"))
        # If tab for this client does not exist, create it
        if client_id not in self.invoice_drafts:
            self.invoice_drafts[client_id] = []
        # Remove previous ProductSelectScreen for this client if exists
        screen_name = f"product_select_{client_id}"
        if self.manager.has_screen(screen_name):
            self.manager.remove_widget(self.manager.get_screen(screen_name))
        # Save mapping and add tab (custom tab panel, not MDTabs)
        # Build tab panel with all current clients
        self.build_tab_panel(selected_client=client)
        # Open ProductSelectScreen for this client
        product_screen = ProductSelectScreen(name=screen_name)
        product_screen.set_client(client)
        product_screen.invoice_items = self.invoice_drafts.get(client_id, []).copy()
        self.manager.add_widget(product_screen)
        self.manager.current = screen_name

    def build_tab_panel(self, selected_client=None):
        # Remove all widgets
        self.clear_widgets()
        # Top panel with tabs for each client
        tab_panel = BoxLayout(orientation='horizontal', size_hint_y=None, height=60, padding=[10, 5], spacing=10)
        # For each client in invoice_drafts, add a tab button
        for client_id in list(self.invoice_drafts.keys()):
            client_obj = self.get_client_by_id(client_id)
            client_name = client_obj.get("name", "Клієнт") if client_obj else client_id
            btn = Button(text=client_name, size_hint_x=None, width=180)
            def select_tab(instance, cid=client_id):
                # Open ProductSelectScreen for this client
                client = self.get_client_by_id(cid)
                if client:
                    self.select_client(client)
            btn.bind(on_release=select_tab)
            tab_panel.add_widget(btn)
        # "+" button to add a new client
        add_btn = Button(text="+", size_hint_x=None, width=60)
        def add_new_client(instance):
            self.open_client_select_form()
        add_btn.bind(on_release=add_new_client)
        tab_panel.add_widget(add_btn)
        # "-" button to remove current client (if any)
        if selected_client is not None:
            remove_btn = Button(text="🗑", size_hint_x=None, width=60)
            def remove_current(instance):
                cid = selected_client.get("edrpou", selected_client.get("name"))
                self.remove_client_tab(cid)
            remove_btn.bind(on_release=remove_current)
            tab_panel.add_widget(remove_btn)
        self.add_widget(tab_panel)


    def remove_client_tab(self, client_id):
        self.invoice_drafts.pop(client_id, None)
        if os.path.exists(self.session_file):
            try:
                with open(self.session_file, "r") as f:
                    data = json.load(f)
                if client_id in data:
                    del data[client_id]
                    with open(self.session_file, "w") as f:
                        json.dump(data, f, indent=2)
            except Exception as e:
                print("Помилка при видаленні чернетки клієнта:", e)
        self.build_tab_panel()


    def get_client_by_id(self, client_id):
        # Find client dict by id from clients.json
        if not os.path.exists(CLIENTS_FILE):
            return None
        with open(CLIENTS_FILE, 'r') as f:
            clients = json.load(f)
        for client in clients:
            cid = client.get("edrpou", client.get("name"))
            if cid == client_id:
                return client
        return None

    def save_session_drafts(self):
        # Save self.invoice_drafts to session_drafts.json
        try:
            with open(self.session_file, "w") as f:
                json.dump(self.invoice_drafts, f, indent=2)
        except Exception as e:
            print("Error saving session drafts:", e)

    def load_session_drafts(self):
        # Load session_drafts.json into self.invoice_drafts
        if os.path.exists(self.session_file):
            try:
                with open(self.session_file, "r") as f:
                    data = json.load(f)
                self.invoice_drafts = data
            except Exception as e:
                print("Error loading session drafts:", e)

    def clear_session_drafts(self):
        # Remove the session file
        try:
            if os.path.exists(self.session_file):
                os.remove(self.session_file)
        except Exception as e:
            print("Error clearing session drafts:", e)


class ProductSelectScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_client = None
        self.invoice_items = []
        self._session_file = "data/session_drafts.json"

    def set_client(self, client):
        self.selected_client = client

    def on_enter(self):
        if self.selected_client:
            self.build_ui()

    def build_ui(self):
        self.clear_widgets()
        from kivy.graphics import Color, RoundedRectangle
        with self.canvas.before:
            Color(0.85, 0.92, 0.98, 1)
            self.bg_rect = RoundedRectangle(size=self.size, pos=self.pos)
        self.bind(size=lambda *x: setattr(self.bg_rect, 'size', self.size),
                  pos=lambda *x: setattr(self.bg_rect, 'pos', self.pos))

        self.layout = GridLayout(cols=1, spacing=15, padding=[20, 10, 20, 10], size_hint=(1, None))
        self.layout.bind(minimum_height=self.layout.setter("height"))

        # --- Custom tabs panel ---
        from kivy.uix.boxlayout import BoxLayout
        tab_panel = BoxLayout(orientation='horizontal', size_hint_y=None, height=60, padding=[10, 5], spacing=10)
        # Get all current clients from invoice_drafts
        invoice_screen = self.manager.get_screen('invoice_create')
        clients = []
        for client_id in list(invoice_screen.invoice_drafts.keys()):
            client = invoice_screen.get_client_by_id(client_id)
            if client:
                clients.append(client)
        # Add a button for each client
        for c in clients:
            btn = Button(text=c.get("name", "Клієнт"), size_hint_x=None, width=180)
            def select_tab(instance, cc=c):
                # Switch to ProductSelectScreen for that client
                screen_name = f"product_select_{cc.get('edrpou', cc.get('name'))}"
                if not self.manager.has_screen(screen_name):
                    ps = ProductSelectScreen(name=screen_name)
                    ps.set_client(cc)
                    ps.invoice_items = invoice_screen.invoice_drafts.get(cc.get("edrpou", cc.get("name")), []).copy()
                    self.manager.add_widget(ps)
                self.manager.current = screen_name
            btn.bind(on_release=select_tab)
            tab_panel.add_widget(btn)
        # "+" button to add a new client
        add_btn = Button(text="+", size_hint_x=None, width=60)
        def add_new_client(instance):
            invoice_screen.open_client_select_form()
        add_btn.bind(on_release=add_new_client)
        tab_panel.add_widget(add_btn)
        self.layout.add_widget(tab_panel, index=0)

        # Показ вибраного клієнта
        client_label = MDLabel(
            text=f"Клієнт: {self.selected_client.get('name', '')} ({self.selected_client.get('type', 'невідомо')})",
            font_size=24,
            size_hint_y=None,
            height=50,
            halign="center"
        )
        self.layout.add_widget(client_label)

        # Пошук товару
        self.product_input = MDTextField(
            hint_text="Пошук товару",
            font_size=30,
            size_hint_y=None,
            height=90,
            foreground_color=(1, 1, 1, 1),
        )
        self.product_input.focus = True
        self.product_input.bind(text=self.on_product_search)
        self.layout.add_widget(self.product_input)

        self.product_results = GridLayout(cols=1, size_hint_y=None, size_hint_x=1)
        self.product_results.bind(minimum_height=self.product_results.setter('height'))

        product_scroll = ScrollView(size_hint=(1, None), size_hint_x=1, height=400)
        product_scroll.add_widget(self.product_results)
        self.layout.add_widget(product_scroll)

        # Перегляд накладної
        self.invoice_preview = GridLayout(cols=1, size_hint_y=None, size_hint_x=1)
        self.invoice_preview.bind(minimum_height=self.invoice_preview.setter('height'))
        preview_scroll = ScrollView(size_hint=(1, None), size_hint_x=1, height=250)
        preview_scroll.add_widget(self.invoice_preview)
        self.layout.add_widget(preview_scroll)
        # Отримати invoice_items з invoice_drafts за client_id перед оновленням перегляду
        client_id = self.selected_client.get("edrpou", self.selected_client.get("name"))
        invoice_screen = self.manager.get_screen('invoice_create')
        self.invoice_items = invoice_screen.invoice_drafts.get(client_id, []).copy()
        # Оновити перегляд накладної згідно з поточними items (draft)
        self.update_invoice_preview()

        # Кнопки
        btn_layout = BoxLayout(size_hint_y=None, size_hint_x=1, height=150, spacing=10, pos_hint={"center_x": 0.5})

        # Close tab card (NEW)
        close_tab_card = MDCard(orientation="vertical", size_hint=(0.4, 1), padding=10, md_bg_color=(0.8, 0.3, 0.3, 1))
        close_icon = MDIconButton(icon="close", text_color=(1, 1, 1, 1), pos_hint={"center_x": 0.5})
        close_label = MDLabel(text="Закрити вкладку", halign="center", font_size=18, text_color=(1, 1, 1, 1))
        close_tab_card.add_widget(close_icon)
        close_tab_card.add_widget(close_label)

        def close_tab(instance):
            manager = self.manager
            client_id = self.selected_client.get("edrpou", self.selected_client.get("name"))
            if manager and manager.has_screen('invoice_create'):
                invoice_screen = manager.get_screen('invoice_create')
                if invoice_screen:
                    invoice_screen.invoice_drafts.pop(client_id, None)
                    invoice_screen.save_session_drafts()
                    manager.remove_widget(self)
                    if len(invoice_screen.invoice_drafts) == 0:
                        manager.current = "main_menu"
                    else:
                        invoice_screen.build_tab_panel()
                        manager.current = "invoice_create"
            else:
                if manager:
                    manager.remove_widget(self)

        close_tab_card.bind(on_release=close_tab)

        # Menu card
        menu_card = MDCard(orientation="vertical", size_hint=(0.4, 1), padding=10, md_bg_color=(0.4, 0.4, 0.4, 1))
        menu_icon = MDIconButton(icon="exit-to-app", text_color=(1, 1, 1, 1), pos_hint={"center_x": 0.5})
        menu_label = MDLabel(text="← До меню", halign="center", font_size=18, text_color=(1, 1, 1, 1))
        menu_card.add_widget(menu_icon)
        menu_card.add_widget(menu_label)
        menu_card.bind(on_release=lambda x: setattr(self.manager, "current", "main_menu"))

        save_card = MDCard(orientation="vertical", size_hint=(0.4, 1), padding=10, md_bg_color=(0.2, 0.6, 0.86, 1))
        save_icon = MDIconButton(icon="content-save", text_color=(1, 1, 1, 1), pos_hint={"center_x": 0.5})
        save_label = MDLabel(text="💾 Зберегти", halign="center", font_name="Roboto", font_size=18, text_color=(1, 1, 1, 1))
        save_card.add_widget(save_icon)
        save_card.add_widget(save_label)
        save_card.bind(on_release=self.save_invoice)

        back_card = MDCard(orientation="vertical", size_hint=(0.4, 1), padding=10, md_bg_color=(0.86, 0.2, 0.2, 1))
        back_icon = MDIconButton(icon="arrow-left", text_color=(1, 1, 1, 1), pos_hint={"center_x": 0.5})
        back_label = MDLabel(text="← Назад", halign="center", font_name="Roboto", font_size=18, text_color=(1, 1, 1, 1))
        back_card.add_widget(back_icon)
        back_card.add_widget(back_label)
        back_card.bind(on_release=self.go_back)

        # Add in order: close_tab_card, menu_card, save_card, back_card
        btn_layout.add_widget(close_tab_card)
        btn_layout.add_widget(menu_card)
        btn_layout.add_widget(save_card)
        btn_layout.add_widget(back_card)
        self.layout.add_widget(btn_layout)

        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(self.layout)
        self.add_widget(scroll)

    def on_product_search(self, instance, value):
        self.product_results.clear_widgets()
        # Check if client is selected
        if not self.selected_client:
            self.product_results.add_widget(Label(text="Спочатку виберіть клієнта", size_hint_y=None, size_hint_x=1, height=50, font_size=18))
            return
        if not os.path.exists(PRODUCTS_FILE):
            return
        with open(PRODUCTS_FILE, 'r') as f:
            products = json.load(f)
        if not value.strip():
            return
        value_lower = value.lower()
        client_price_type = self.selected_client.get('price_type', '').strip().upper()
        matched_products = []
        for p in products:
            if p.get('price_type', '').strip().upper() != client_price_type:
                continue
            name = str(p.get('name', '')).lower()
            if value_lower in name:
                matched_products.append(p)
                if len(matched_products) > 30:
                    break
        if len(matched_products) == 1:
            self.add_product(matched_products[0])
            return
        for product in matched_products:
            name = str(product.get('name', 'Без назви'))
            price = str(product.get('price', '0'))
            card = MDCard(orientation="horizontal", size_hint_y=None, height=70, padding=10, md_bg_color=(0.93, 0.95, 1, 1), radius=[12])
            label = MDLabel(text=f"{name}", font_size=20, size_hint_x=0.7, theme_text_color="Primary")
            price_label = MDLabel(text=f"{price} грн", halign="right", font_size=20, size_hint_x=0.3, theme_text_color="Secondary")
            card.add_widget(label)
            card.add_widget(price_label)
            card.bind(on_release=lambda inst, p=product: self.add_product(p))
            self.product_results.add_widget(card)
        # If no products were added, show "not found"
        if not self.product_results.children:
            self.product_results.add_widget(Label(text="Товарів не знайдено", size_hint_y=None, size_hint_x=1, height=50, font_size=18))

    def add_product(self, product, *args):
        from kivy.uix.popup import Popup
        from kivy.uix.floatlayout import FloatLayout
        from kivy.graphics import Color, RoundedRectangle
        try:
            content = FloatLayout()
            with content.canvas.before:
                Color(0.15, 0.15, 0.15, 1)
                self.bg_rect = RoundedRectangle(size=content.size, pos=content.pos, radius=[20])
                content.bind(size=lambda *x: setattr(self.bg_rect, 'size', content.size),
                             pos=lambda *x: setattr(self.bg_rect, 'pos', content.pos))
            qty_input = MDTextField(
                hint_text="Кількість",
                font_size=40,
                size_hint=(0.8, None),
                height=90,
                pos_hint={"center_x": 0.5, "center_y": 0.6},
                foreground_color=(1, 1, 1, 1)
            )
            qty_input.focus = True
            confirm_btn = Button(text="Додати", size_hint=(0.4, None), height=40,
                                 pos_hint={"center_x": 0.3, "center_y": 0.3})
            cancel_btn = Button(text="Скасувати", size_hint=(0.4, None), height=40,
                                pos_hint={"center_x": 0.7, "center_y": 0.3})

            popup = Popup(title="Вкажіть кількість", content=content,
                          size_hint=(0.8, 0.5), auto_dismiss=False,
                          background_color=(0.95, 0.95, 0.95, 1))
            content.add_widget(qty_input)
            content.add_widget(confirm_btn)
            content.add_widget(cancel_btn)

            def on_confirm(instance):
                try:
                    qty = int(qty_input.text.strip())
                    if qty > 0:
                        product_copy = product.copy()
                        product_copy["quantity"] = qty
                        self.invoice_items.append(product_copy)
                        # Синхронізувати з чернеткою вкладки цього клієнта
                        client_id = self.selected_client.get("edrpou", self.selected_client.get("name"))
                        invoice_screen = self.manager.get_screen('invoice_create')
                        invoice_screen.invoice_drafts[client_id] = self.invoice_items.copy()
                        invoice_screen.save_session_drafts()
                        self.update_invoice_preview()
                except:
                    pass
                popup.dismiss()
                self.product_input.focus = True

            def on_cancel(instance):
                popup.dismiss()

            confirm_btn.bind(on_release=on_confirm)
            cancel_btn.bind(on_release=on_cancel)
            qty_input.bind(on_text_validate=on_confirm)
            popup.open()

        except Exception as e:
            print("Помилка при додаванні товару:", e)

    def update_invoice_preview(self):
        self.invoice_preview.clear_widgets()
        for index, item in enumerate(self.invoice_items):
            row = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)
            lbl = Label(text=f"{item['name']} — {item['price']} грн x {item.get('quantity', 1)}", font_size=20, font_name="Roboto", color=(0, 0, 0, 1), size_hint_x=0.8)
            del_btn = Button(text="✖", size_hint_x=0.2)
            def delete_item(instance, idx=index):
                self.invoice_items.pop(idx)
                # update the session
                client_id = self.selected_client.get("edrpou", self.selected_client.get("name"))
                invoice_screen = self.manager.get_screen('invoice_create')
                invoice_screen.invoice_drafts[client_id] = self.invoice_items.copy()
                invoice_screen.save_session_drafts()
                self.update_invoice_preview()
            del_btn.bind(on_release=delete_item)
            row.add_widget(lbl)
            row.add_widget(del_btn)
            self.invoice_preview.add_widget(row)

    def save_invoice(self, instance):
        if not self.selected_client or not self.invoice_items:
            return
        invoice = {
            'client': self.selected_client,
            'items': self.invoice_items
        }
        from datetime import datetime

        history_file = "data/history.json"
        history_entry = {
            "client": self.selected_client.get("name", ""),
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "items": self.invoice_items
        }
        if not os.path.exists(history_file):
            os.makedirs("data", exist_ok=True)
            with open(history_file, "w") as f:
                json.dump([], f)

        with open(history_file, "r") as f:
            history = json.load(f)

        history.append(history_entry)

        with open(history_file, "w") as f:
            json.dump(history, f, indent=2)

        invoices = []
        if os.path.exists(INVOICES_FILE):
            with open(INVOICES_FILE, 'r') as f:
                invoices = json.load(f)
        invoices.append(invoice)
        with open(INVOICES_FILE, 'w') as f:
            json.dump(invoices, f, indent=2)
        self.invoice_items = []
        # Очистити відповідний запис з чернеток
        invoice_screen = self.manager.get_screen('invoice_create')
        client_id = self.selected_client.get("edrpou", self.selected_client.get("name"))
        invoice_screen.invoice_drafts.pop(client_id, None)
        invoice_screen.save_session_drafts()
        # If no more drafts, clear session file
        if not invoice_screen.invoice_drafts:
            invoice_screen.clear_session_drafts()
        # Remove the current client's tab and navigate to invoice_create
        client_id = self.selected_client.get("edrpou", self.selected_client.get("name"))
        self.manager.remove_widget(self)
        invoice_screen.build_tab_panel()
        if self.manager and self.manager.has_screen("invoice_create"):
            self.manager.current = "invoice_create"

    def go_back(self, instance):
        # Зберегти invoice_items у відповідну чернетку вкладки
        invoice_screen = self.manager.get_screen('invoice_create')
        client_id = self.selected_client.get("edrpou", self.selected_client.get("name"))
        invoice_screen.invoice_drafts[client_id] = self.invoice_items
        invoice_screen.save_session_drafts()
        # Повернення до створення накладної
        self.manager.current = 'invoice_create'

InvoiceCreateScreen = InvoiceCreateScreen
# Новий клас вкладки для клієнта (більше не використовується з кастомною панеллю)