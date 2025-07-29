from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button

class MainMenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        screens = {
            'clients_view': 'Clients View',
            'client_add': 'Add Client',
            'products_view': 'Products View',
            'products_batch': 'Products Batch',
            'invoice_create': 'Create Invoice',
            'sales_analysis': 'Sales Analysis',
            'history_view': 'History View'
        }
        for screen_name, btn_text in screens.items():
            btn = Button(text=btn_text)
            btn.bind(on_release=lambda instance, scr=screen_name: self.switch_to(scr))
            layout.add_widget(btn)
        self.add_widget(layout)

    def switch_to(self, screen_name):
        print(f"Switching to: {screen_name}")
        if screen_name in self.manager.screen_names:
            self.manager.current = screen_name
        else:
            print(f"Екран '{screen_name}' не додано до ScreenManager!")