from flask import Flask, request, jsonify
from invoice_system import nakladna

app = Flask(__name__)

@app.route("/generate_invoice", methods=["POST"])
def generate_invoice_route():
    try:
        result = nakladna.generate_invoice()
        return f"✅ Накладну створено: {result}", 200
    except Exception as e:
        return f"❌ Помилка створення: {str(e)}", 500

@app.route("/add_clients", methods=["POST"])
def add_clients_route():
    data = request.json.get("data", "")
    count = nakladna.mass_add_clients(data)
    return f"Додано клієнтів: {count}", 200

@app.route("/add_products", methods=["POST"])
def add_products_route():
    data = request.json.get("data", "")
    count = nakladna.mass_add_products(data)
    return f"Додано товарів: {count}", 200

@app.route("/history", methods=["GET"])
def history_route():
    history = nakladna.get_invoice_history()
    return "\n".join(history), 200

@app.route("/analytics", methods=["GET"])
def analytics_route():
    result = nakladna.get_analytics()
    return result, 200

if __name__ == "__main__":
    app.run(port=8123)
