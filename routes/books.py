from flask import Blueprint, request, jsonify
from models import Book, Author
from database import db

books_bp = Blueprint('books', __name__)
# GET
@books_bp.route('/books', methods=['GET'])
def get_books():
    books = Book.query.all()
    return jsonify([b.to_dict() for b in books])

# POST
@books_bp.route('/books', methods=['POST'])
def add_book():
    data = request.json

    new_book = Book(
        title=data['title'],
        price=data['price'],
        stock=data['stock']
    )

    author_ids = data.get('author_ids', [])

    for author_id in author_ids:
        author = Author.query.get(author_id)
        if author:
            new_book.authors.append(author)

    db.session.add(new_book)
    db.session.commit()

    return jsonify({"message": "Book with authors added"})