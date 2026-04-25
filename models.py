from database import db

# =========================
# 🔗 Book ↔ Author (Many-to-Many)
# =========================

book_author = db.Table(
    'book_author',
    db.Column('book_id', db.Integer, db.ForeignKey('books.book_id'), primary_key=True),
    db.Column('author_id', db.Integer, db.ForeignKey('authors.author_id'), primary_key=True)
)

# =========================
# 📚 BOOK
# =========================

class Book(db.Model):
    __tablename__ = 'books'

    book_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)

    authors = db.relationship('Author', secondary=book_author, backref='books')

    order_items = db.relationship('OrderItem', backref='book', lazy=True)

    def to_dict(self):
        return {
            "book_id": self.book_id,
            "title": self.title,
            "price": self.price,
            "stock": self.stock,
            "authors": [a.name for a in self.authors]
        }


# =========================
# 👤 AUTHOR
# =========================

class Author(db.Model):
    __tablename__ = 'authors'

    author_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    def to_dict(self):
        return {
            "author_id": self.author_id,
            "name": self.name
        }


# =========================
# 🧾 ORDER
# =========================

class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    total_price = db.Column(db.Float, default=0)

    items = db.relationship('OrderItem', backref='order', lazy=True)

    def to_dict(self):
        return {
            "order_id": self.id,
            "total_price": self.total_price,
            "items": [
                {
                    "book_title": item.book.title,
                    "quantity": item.quantity,
                    "price": item.book.price
                }
                for item in self.items
            ]
        }


# =========================
# 📦 ORDER ITEM
# =========================

class OrderItem(db.Model):
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True)

    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id'), nullable=False)

    quantity = db.Column(db.Integer, nullable=False)