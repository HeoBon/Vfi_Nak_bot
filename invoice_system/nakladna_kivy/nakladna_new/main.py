from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivy.uix.screenmanager import ScreenManager
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.boxlayout import MDBoxLayout
import storage

class MainMenuScreen(MDScreen):
    def on_enter(self):
        self.clear_widgets()
        root = MDBoxLayout(orientation="horizontal")

        menu = MDBoxLayout(orientation="vertical", spacing=20, padding=20, size_hint_x=0.15)
        content = MDBoxLayout()  # Порожнє місце праворуч для майбутнього контенту

        menu.add_widget(MDRaisedButton(text="📋 Клієнти", on_release=self.go_to_clients))
        menu.add_widget(MDRaisedButton(text="📦 Продукти", on_release=self.go_to_products))
        menu.add_widget(MDRaisedButton(text="📚 Історія", on_release=self.go_to_history))
        menu.add_widget(MDRaisedButton(text="🧮 Масові дії", on_release=self.go_to_batch))
        menu.add_widget(MDRaisedButton(text="🧾 Накладна", on_release=self.go_to_invoice))
        menu.add_widget(MDRaisedButton(text="📊 Аналітика", on_release=self.go_to_analysis))

        root.add_widget(menu)
        root.add_widget(content)
        self.add_widget(root)

    def go_to_clients(self, instance):
        self.manager.current = 'clients'

    def go_to_products(self, instance):
        self.manager.current = 'products'

    def go_to_history(self, instance):
        self.manager.current = 'history'

    def go_to_batch(self, instance):
        self.manager.current = 'products_batch'

    def go_to_invoice(self, instance):
        self.manager.current = 'invoice_create'

    def go_to_analysis(self, instance):
        self.manager.current = 'sales_analysis'

class ClientsViewScreen(MDScreen):
    def on_enter(self):
        self.clear_widgets()
        layout = MDBoxLayout(orientation="vertical", padding=20, spacing=10)
        clients = [client["name"] for client in storage.load_clients()]
        for name in clients:
            row = MDBoxLayout(size_hint_y=None, height=50, padding=10)
            row.add_widget(MDLabel(text=name, halign="left", valign="middle"))
            layout.add_widget(row)
        self.add_widget(layout)

class ProductsViewScreen(MDScreen):
    def on_enter(self):
        self.clear_widgets()
        self.add_widget(MDLabel(text="📦 Список продуктів", halign="center"))

class HistoryViewScreen(MDScreen):
    def on_enter(self):
        self.clear_widgets()
        self.add_widget(MDLabel(text="📚 Історія накладних", halign="center"))

class ProductsBatchScreen(MDScreen):
    def on_enter(self):
        self.clear_widgets()
        self.add_widget(MDLabel(text="🧮 Масові дії з продуктами", halign="center"))

class ClientSelectScreen(MDScreen):
    def on_enter(self):
        self.clear_widgets()
        self.add_widget(MDLabel(text="🧾 Створення накладної", halign="center"))

class SalesAnalysisScreen(MDScreen):
    def on_enter(self):
        self.clear_widgets()
        self.add_widget(MDLabel(text="📊 Аналітика продажів", halign="center"))

class MainApp(MDApp):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainMenuScreen(name='main_menu'))
        sm.add_widget(ClientsViewScreen(name='clients'))
        sm.add_widget(ProductsViewScreen(name='products'))
        sm.add_widget(HistoryViewScreen(name='history'))
        sm.add_widget(ProductsBatchScreen(name='products_batch'))
        sm.add_widget(ClientSelectScreen(name='invoice_create'))
        sm.add_widget(SalesAnalysisScreen(name='sales_analysis'))
        sm.current = 'main_menu'
        return sm

    def on_start(self):
        from kivy.core.window import Window
        storage.ensure_data_files()
        Window.maximize()

if __name__ == '__main__':
    MainApp().run()