from flask import Blueprint, jsonify, request
from database import db
from models import Order, OrderItem, Book, Customer

orders_bp = Blueprint('orders', __name__, url_prefix='/api')

@orders_bp.route('/orders', methods=['GET'])
def get_orders():
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return jsonify([o.to_dict() for o in orders])

@orders_bp.route('/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    order = Order.query.get_or_404(order_id)
    return jsonify(order.to_dict())

@orders_bp.route('/orders', methods=['POST'])
def create_order():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data received'}), 400

        items = data.get('items', [])
        if not items:
            return jsonify({'error': 'At least one item is required'}), 400

        order = Order(
            customer_id=data.get('customer_id') or None,
            payment_method=data.get('payment_method', 'cash'),
            notes=data.get('notes') or None,
            status='pending'
        )
        db.session.add(order)
        db.session.flush()  # get order_id before commit

        total = 0
        for item in items:
            book_id  = item.get('book_id')
            quantity = int(item.get('quantity', 1))

            if not book_id:
                return jsonify({'error': 'book_id is required for each item'}), 400

            book = Book.query.get(book_id)
            if not book:
                return jsonify({'error': f'Book with id {book_id} not found'}), 404
            if book.stock < quantity:
                return jsonify({'error': f'Not enough stock for "{book.title}". Available: {book.stock}'}), 400

            order_item = OrderItem(
                order_id=order.order_id,
                book_id=book.book_id,
                quantity=quantity,
                unit_price=book.price
            )
            book.stock -= quantity   # deduct stock automatically
            total += order_item.subtotal
            db.session.add(order_item)

        order.total_price = total
        db.session.commit()
        return jsonify(order.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@orders_bp.route('/orders/<int:order_id>/status', methods=['PUT'])
def update_status(order_id):
    try:
        order = Order.query.get_or_404(order_id)
        data = request.get_json()
        valid = ['pending', 'confirmed', 'shipped', 'delivered', 'cancelled']
        status = data.get('status')
        if status not in valid:
            return jsonify({'error': f'Status must be one of: {valid}'}), 400
        order.status = status
        db.session.commit()
        return jsonify(order.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
