import tkinter as tk
from tkinter import messagebox
import json, os, csv
from datetime import datetime

def load_json(path):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_json(data, path):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

products = load_json('products.json')
customers = load_json('customers.json')

root = tk.Tk()
root.title("Програма")
root.geometry("700x600")
root.configure(bg='black')

frame_top = tk.Frame(root, bg='black')
frame_top.pack(pady=10)

log = tk.Text(frame_top, width=80, height=20, bg='white', fg='black', font=('Arial', 12))
log.pack()

frame_entry = tk.Frame(root, bg='black')
frame_entry.pack(pady=10)

entry_label = tk.Label(frame_entry, text="Введіть дані:", fg='white', bg='black', font=('Arial', 12))
entry_label.pack(side='left', padx=5)

entry = tk.Entry(frame_entry, width=60, font=('Arial', 12))
entry.pack(side='left', padx=5)

def log_message(msg):
    log.insert(tk.END, msg + "\n")
    log.see(tk.END)

def add_customer():
    parts = entry.get().split(',')
    if len(parts) != 2:
        log_message("Формат: Ім'я, Тип (PM, PL, PK, PWS, PSS)")
        return
    name, price_type = parts[0].strip(), parts[1].strip()
    if price_type not in ('PM', 'PL', 'PK', 'PWS', 'PSS'):
        log_message("Невірний тип ціни")
        return
    customers[name] = price_type
    save_json(customers, 'customers.json')
    log_message(f"Додано/оновлено клієнта {name} з типом {price_type}")

def add_product():
    parts = entry.get().split(',')
    if len(parts) != 7:
        log_message("Формат: Назва, PM, PL, PK, PWS, PSS, Од.виміру")
        return
    name = parts[0].strip()
    try:
        data = {k: float(v.strip()) for k, v in zip(('PM', 'PL', 'PK', 'PWS', 'PSS'), parts[1:6])}
        data['unit'] = parts[6].strip()
        products[name] = data
        save_json(products, 'products.json')
        log_message(f"Додано товар {name}")
    except:
        log_message("Помилка в даних")

def create_invoice():
    parts = entry.get().split(',')
    if len(parts) != 1:
        log_message("Введіть лише ім'я клієнта")
        return
    customer = parts[0].strip()
    if customer not in customers:
        log_message("Клієнт не знайдений")
        return
    price_type = customers[customer]
    rows = [['Дата', datetime.now().strftime('%Y-%m-%d')], ['Замовник', customer], ['Тип ціни', price_type], [], ['Товар', 'Ціна', 'Од.виміру']]
    total = 0
    for name, data in products.items():
        price = data.get(price_type, 0)
        rows.append([name, price, data['unit']])
        total += price
    rows.append([])
    rows.append(['Загальна сума', total])
    filename = f"накладна_{customer}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        csv.writer(f).writerows(rows)
    log_message(f"Накладна створена: {filename}")

frame_buttons = tk.Frame(root, bg='black')
frame_buttons.pack(pady=10)

tk.Button(frame_buttons, text="Додати клієнта", command=add_customer, bg='gray', fg='white', font=('Arial', 12)).pack(pady=5)
tk.Button(frame_buttons, text="Додати товар", command=add_product, bg='gray', fg='white', font=('Arial', 12)).pack(pady=5)
tk.Button(frame_buttons, text="Створити накладну", command=create_invoice, bg='gray', fg='white', font=('Arial', 12)).pack(pady=5)
tk.Button(frame_buttons, text="Вийти", command=root.destroy, bg='gray', fg='white', font=('Arial', 12)).pack(pady=5)

root.mainloop()

