from flask import Flask
from database import db
from flask_cors import CORS

app = Flask(__name__)   # ✅ FIRST create app
CORS(app)

# Database config (SQLite)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bookstore.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# ✅ Import routes AFTER app is created
from routes.books import books_bp
from routes.authors import authors_bp
from routes.orders import orders_bp  

# ✅ Register blueprints AFTER import
app.register_blueprint(books_bp)
app.register_blueprint(authors_bp)
app.register_blueprint(orders_bp)

if __name__ == "__main__":
    app.run(debug=True)