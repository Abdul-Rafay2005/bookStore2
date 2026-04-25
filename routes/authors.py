from flask import Blueprint, request, jsonify
from models import Author
from database import db

authors_bp = Blueprint('authors', __name__)

@authors_bp.route('/authors', methods=['POST'])
def add_author():
    data = request.json

    author = Author(name=data['name'])
    db.session.add(author)
    db.session.commit()

    return jsonify({"message": "Author added"})


@authors_bp.route('/authors', methods=['GET'])
def get_authors():
    authors = Author.query.all()
    return jsonify([a.to_dict() for a in authors])