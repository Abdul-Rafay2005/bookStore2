from flask import Blueprint, jsonify, request
from database import db
from models import Author

authors_bp = Blueprint('authors', __name__, url_prefix='/api')

@authors_bp.route('/authors', methods=['GET'])
def get_authors():
    authors = Author.query.all()
    return jsonify([a.to_dict() for a in authors])

@authors_bp.route('/authors/<int:author_id>', methods=['GET'])
def get_author(author_id):
    author = Author.query.get_or_404(author_id)
    return jsonify(author.to_dict())

@authors_bp.route('/authors', methods=['POST'])
def add_author():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data received'}), 400
        if not data.get('name'):
            return jsonify({'error': 'Name is required'}), 400

        # Check for duplicate
        existing = Author.query.filter_by(name=data['name'].strip()).first()
        if existing:
            return jsonify({'error': f'Author "{data["name"]}" already exists'}), 409

        author = Author(
            name=data['name'].strip(),
            bio=data.get('bio') or None,
            email=data.get('email') or None
        )
        db.session.add(author)
        db.session.commit()
        return jsonify(author.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@authors_bp.route('/authors/<int:author_id>', methods=['PUT'])
def update_author(author_id):
    try:
        author = Author.query.get_or_404(author_id)
        data = request.get_json()
        author.name  = data.get('name', author.name).strip()
        author.bio   = data.get('bio', author.bio)
        author.email = data.get('email', author.email)
        db.session.commit()
        return jsonify(author.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@authors_bp.route('/authors/<int:author_id>', methods=['DELETE'])
def delete_author(author_id):
    try:
        author = Author.query.get_or_404(author_id)
        db.session.delete(author)
        db.session.commit()
        return jsonify({'message': 'Author deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
