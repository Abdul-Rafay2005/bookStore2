from flask import Flask, render_template, jsonify
from database import db
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bookstore.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# ── Blueprints ────────────────────────────────────────────────────────────────
from routes.books import books_bp
from routes.authors import authors_bp
from routes.orders import orders_bp
from routes.customers import customers_bp

app.register_blueprint(books_bp)
app.register_blueprint(authors_bp)
app.register_blueprint(orders_bp)
app.register_blueprint(customers_bp)

# ── Return JSON errors instead of HTML pages ──────────────────────────────────
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Route not found", "message": str(e)}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Server error", "message": str(e)}), 500

# ── Frontend ──────────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('bookstore_dashboard.html')

# ── Create tables ─────────────────────────────────────────────────────────────
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
