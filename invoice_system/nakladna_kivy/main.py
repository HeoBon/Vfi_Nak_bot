ʼ
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.label import MDLabel
from kivy.uix.screenmanager import ScreenManager

# Імпорти всіх екранів
from screens.clients_view import ClientsViewScreen
from screens.client_add import ClientAddScreen
from screens.products_view import ProductsViewScreen
from screens.products_batch import ProductsBatchScreen
from screens.invoice_create import ClientSelectScreen
from screens.sales_analysis import SalesAnalysisScreen
from screens.history_view import HistoryViewScreen

class MainMenuScreen(MDScreen):
    def on_enter(self):
        from kivymd.uix.card import MDCard
        from kivymd.uix.gridlayout import MDGridLayout
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.label import MDLabel
        from kivymd.uix.scrollview import MDScrollView
        from kivymd.app import MDApp

        self.clear_widgets()

        scroll = MDScrollView()
        grid = MDGridLayout(cols=2, spacing=24, padding=24, size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))

        items = [
            ("account-cash", "Перегляд клієнтів", "", 'clients_view'),
            ("account-plus", "Додати клієнта", "", 'client_add'),
            ("package-variant", "Перегляд товарів", "", 'products_view'),
            ("playlist-edit", "Масові дії", "", 'products_batch'),
            ("file-document-edit", "Створити накладну", "", 'invoice_create'),
            ("chart-line", "Аналіз продажів", "", 'sales_analysis'),
            ("history", "Історія накладних", "", 'history_view'),
            ("exit-to-app", "Вийти", "", None)
        ]

        symbols = {
            'clients_view': '👥',
            'client_add': '➕',
            'products_view': '📦',
            'products_batch': '🧮',
            'invoice_create': '🧾',
            'sales_analysis': '📊',
            'history_view': '📚',
            None: '🚪'
        }

        for icon, title, subtitle, screen_name in items:
            card = MDCard(orientation="vertical", size_hint=(1, None), height=160, padding=12, md_bg_color=(0.9, 0.9, 0.95, 1), ripple_behavior=True)
            box = MDBoxLayout(orientation="vertical", spacing=8)
            box.size_hint_y = None
            box.height = 120
            from kivymd.uix.button import MDIconButton
            icon_button = MDIconButton(icon=icon, theme_text_color="Custom", text_color=(0, 0, 0, 1), pos_hint={"center_x": 0.5}, size_hint=(None, None), size=("48dp", "48dp"))
            box.add_widget(icon_button)
            box.add_widget(MDLabel(text=title, halign="center", bold=True, font_style="H6"))
            box.add_widget(MDLabel(text=subtitle, halign="center", theme_text_color="Secondary"))
            card.add_widget(box)

            if screen_name:
                card.bind(on_release=lambda inst, scr=screen_name: self.switch_to(scr))
            else:
                card.bind(on_release=lambda inst: MDApp.get_running_app().stop())
            grid.add_widget(card)
            self.ids = getattr(self, 'ids', {})
            self.ids[screen_name or f"exit_{title}"] = card

        grid.height = len(items) * 200  # Примусове встановлення висоти для прокрутки

        scroll.add_widget(grid)
        self.add_widget(scroll)

    def switch_to(self, screen_name):
        print(f"Switching to: {screen_name}")
        if screen_name in self.manager.screen_names:
            self.manager.current = screen_name
        else:
            print(f"Екран '{screen_name}' не знайдено.")

class MainApp(MDApp):
    def build(self):
        print("Building UI...")
        sm = ScreenManager()
        sm.add_widget(MainMenuScreen(name='main_menu'))
        sm.add_widget(ClientsViewScreen(name='clients_view'))
        sm.add_widget(ClientAddScreen(name='client_add'))
        sm.add_widget(ProductsViewScreen(name='products_view'))
        sm.add_widget(ProductsBatchScreen(name='products_batch'))
        sm.add_widget(ClientSelectScreen(name='invoice_create'))
        sm.add_widget(SalesAnalysisScreen(name='sales_analysis'))
        sm.add_widget(HistoryViewScreen(name='history_view'))
        sm.current = 'main_menu'
        return sm

if __name__ == '__main__':
    print("MainApp starting...")
    MainApp().run()