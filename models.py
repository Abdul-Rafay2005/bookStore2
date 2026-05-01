from database import db
from datetime import datetime

# =========================
# 🔗 Book ↔ Author (Many-to-Many)
# =========================
book_author = db.Table(
    'book_author',
    db.Column('book_id', db.Integer, db.ForeignKey('books.book_id'), primary_key=True),
    db.Column('author_id', db.Integer, db.ForeignKey('authors.author_id'), primary_key=True)
)

# =========================
# 🔗 Book ↔ Category (Many-to-Many)
# =========================
book_category = db.Table(
    'book_category',
    db.Column('book_id', db.Integer, db.ForeignKey('books.book_id'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('categories.category_id'), primary_key=True)
)

# =========================
# 📚 BOOK
# =========================
class Book(db.Model):
    __tablename__ = 'books'

    book_id     = db.Column(db.Integer, primary_key=True)
    title       = db.Column(db.String(200), nullable=False)
    isbn        = db.Column(db.String(20), unique=True, nullable=True)
    price       = db.Column(db.Float, nullable=False)
    stock       = db.Column(db.Integer, default=0)
    low_stock_threshold = db.Column(db.Integer, default=5)
    publisher   = db.Column(db.String(150), nullable=True)
    published_year = db.Column(db.Integer, nullable=True)
    description = db.Column(db.Text, nullable=True)
    cover_url   = db.Column(db.String(300), nullable=True)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    authors     = db.relationship('Author', secondary=book_author, backref='books')
    categories  = db.relationship('Category', secondary=book_category, backref='books')
    order_items = db.relationship('OrderItem', backref='book', lazy=True)
    supply_logs = db.relationship('SupplyLog', backref='book', lazy=True)

    @property
    def is_low_stock(self):
        return self.stock <= self.low_stock_threshold

    def to_dict(self):
        return {
            "book_id": self.book_id,
            "title": self.title,
            "isbn": self.isbn,
            "price": self.price,
            "stock": self.stock,
            "low_stock": self.is_low_stock,
            "publisher": self.publisher,
            "published_year": self.published_year,
            "description": self.description,
            "cover_url": self.cover_url,
            "authors": [a.to_dict() for a in self.authors],
            "categories": [c.to_dict() for c in self.categories],
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

# =========================
# 👤 AUTHOR
# =========================
class Author(db.Model):
    __tablename__ = 'authors'

    author_id = db.Column(db.Integer, primary_key=True)
    name      = db.Column(db.String(100), nullable=False)
    bio       = db.Column(db.Text, nullable=True)
    email     = db.Column(db.String(120), unique=True, nullable=True)

    def to_dict(self):
        return {
            "author_id": self.author_id,
            "name": self.name,
            "bio": self.bio,
            "email": self.email,
            "book_count": len(self.books)
        }

# =========================
# 🏷️ CATEGORY
# =========================
class Category(db.Model):
    __tablename__ = 'categories'

    category_id = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            "category_id": self.category_id,
            "name": self.name,
            "description": self.description,
            "book_count": len(self.books)
        }

# =========================
# 🧍 CUSTOMER
# =========================
class Customer(db.Model):
    __tablename__ = 'customers'

    customer_id = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(100), nullable=False)
    email       = db.Column(db.String(120), unique=True, nullable=False)
    phone       = db.Column(db.String(20), nullable=True)
    address     = db.Column(db.Text, nullable=True)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    orders = db.relationship('Order', backref='customer', lazy=True)

    @property
    def total_spent(self):
        return sum(o.total_price for o in self.orders)

    @property
    def order_count(self):
        return len(self.orders)

    def to_dict(self):
        return {
            "customer_id": self.customer_id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "address": self.address,
            "order_count": self.order_count,
            "total_spent": self.total_spent,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

# =========================
# 🧾 ORDER
# =========================
class Order(db.Model):
    __tablename__ = 'orders'

    order_id       = db.Column(db.Integer, primary_key=True)
    customer_id    = db.Column(db.Integer, db.ForeignKey('customers.customer_id'), nullable=True)
    total_price    = db.Column(db.Float, default=0)
    status         = db.Column(db.String(20), default='pending')  # pending, confirmed, shipped, delivered, cancelled
    payment_method = db.Column(db.String(30), nullable=True)      # cash, card, online
    notes          = db.Column(db.Text, nullable=True)
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    items = db.relationship('OrderItem', backref='order', lazy=True)

    def to_dict(self):
        return {
            "order_id": self.order_id,
            "customer": self.customer.to_dict() if self.customer else None,
            "total_price": self.total_price,
            "status": self.status,
            "payment_method": self.payment_method,
            "notes": self.notes,
            "item_count": len(self.items),
            "items": [
                {
                    "book_id": item.book_id,
                    "book_title": item.book.title,
                    "quantity": item.quantity,
                    "unit_price": item.unit_price,
                    "subtotal": item.subtotal
                }
                for item in self.items
            ],
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

# =========================
# 📦 ORDER ITEM
# =========================
class OrderItem(db.Model):
    __tablename__ = 'order_items'

    id         = db.Column(db.Integer, primary_key=True)
    order_id   = db.Column(db.Integer, db.ForeignKey('orders.order_id'), nullable=False)
    book_id    = db.Column(db.Integer, db.ForeignKey('books.book_id'), nullable=False)
    quantity   = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)  # Snapshot price at time of order

    @property
    def subtotal(self):
        return self.quantity * self.unit_price

# =========================
# 🏭 SUPPLIER
# =========================
class Supplier(db.Model):
    __tablename__ = 'suppliers'

    supplier_id = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(100), nullable=False)
    email       = db.Column(db.String(120), nullable=True)
    phone       = db.Column(db.String(20), nullable=True)
    address     = db.Column(db.Text, nullable=True)

    # Relationships
    supply_logs = db.relationship('SupplyLog', backref='supplier', lazy=True)

    def to_dict(self):
        return {
            "supplier_id": self.supplier_id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "address": self.address,
        }

# =========================
# 📋 SUPPLY LOG (Restocking)
# =========================
class SupplyLog(db.Model):
    __tablename__ = 'supply_logs'

    log_id        = db.Column(db.Integer, primary_key=True)
    book_id       = db.Column(db.Integer, db.ForeignKey('books.book_id'), nullable=False)
    supplier_id   = db.Column(db.Integer, db.ForeignKey('suppliers.supplier_id'), nullable=True)
    quantity      = db.Column(db.Integer, nullable=False)
    cost_per_unit = db.Column(db.Float, nullable=True)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "log_id": self.log_id,
            "book_title": self.book.title,
            "supplier": self.supplier.name if self.supplier else "Unknown",
            "quantity": self.quantity,
            "cost_per_unit": self.cost_per_unit,
            "total_cost": (self.quantity * self.cost_per_unit) if self.cost_per_unit else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
