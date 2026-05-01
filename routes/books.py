from flask import Blueprint, jsonify, request
from database import db
from models import Book, Author, Category

books_bp = Blueprint('books', __name__, url_prefix='/api')

# ⚠️ IMPORTANT: /books/low-stock must be defined BEFORE /books/<int:book_id>
# otherwise Flask matches "low-stock" as a book_id and returns 404
@books_bp.route('/books/low-stock', methods=['GET'])
def low_stock():
    books = Book.query.filter(Book.stock <= Book.low_stock_threshold).all()
    return jsonify([b.to_dict() for b in books])

@books_bp.route('/books', methods=['GET'])
def get_books():
    books = Book.query.all()
    return jsonify([b.to_dict() for b in books])

@books_bp.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    book = Book.query.get_or_404(book_id)
    return jsonify(book.to_dict())

@books_bp.route('/books', methods=['POST'])
def add_book():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data received'}), 400
        if not data.get('title'):
            return jsonify({'error': 'Title is required'}), 400
        if not data.get('price'):
            return jsonify({'error': 'Price is required'}), 400

        book = Book(
            title=data['title'],
            isbn=data.get('isbn') or None,
            price=float(data['price']),
            stock=int(data.get('stock', 0)),
            publisher=data.get('publisher') or None,
            published_year=data.get('published_year') or None,
            description=data.get('description') or None,
            cover_url=data.get('cover_url') or None
        )

        # Add authors (create if not exists)
        for author_name in data.get('authors', []):
            if not author_name.strip():
                continue
            author = Author.query.filter_by(name=author_name.strip()).first()
            if not author:
                author = Author(name=author_name.strip())
                db.session.add(author)
            book.authors.append(author)

        # Add categories (create if not exists)
        for cat_name in data.get('categories', []):
            if not cat_name.strip():
                continue
            cat = Category.query.filter_by(name=cat_name.strip()).first()
            if not cat:
                cat = Category(name=cat_name.strip())
                db.session.add(cat)
            book.categories.append(cat)

        db.session.add(book)
        db.session.commit()
        return jsonify(book.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@books_bp.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    try:
        book = Book.query.get_or_404(book_id)
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No JSON data received'}), 400
        if not data.get('title'):
            return jsonify({'error': 'Title is required'}), 400
        if not data.get('price'):
            return jsonify({'error': 'Price is required'}), 400

        # Explicitly assign every field so SQLAlchemy tracks changes
        book.title       = str(data['title']).strip()
        book.price       = float(data['price'])
        book.stock       = int(data.get('stock', 0))
        book.isbn        = data.get('isbn') or book.isbn
        book.publisher   = data.get('publisher') or book.publisher
        book.description = data.get('description') or book.description

        # Force SQLAlchemy to recognise the object as changed
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(book, 'title')
        flag_modified(book, 'price')
        flag_modified(book, 'stock')

        db.session.add(book)
        db.session.commit()
        db.session.refresh(book)   # re-read from DB to confirm
        return jsonify(book.to_dict())

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@books_bp.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    try:
        book = Book.query.get_or_404(book_id)
        db.session.delete(book)
        db.session.commit()
        return jsonify({'message': 'Book deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
