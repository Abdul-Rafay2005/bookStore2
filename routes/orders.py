from flask import Blueprint, request, jsonify
from models import db, Order, OrderItem, Book

orders_bp = Blueprint('orders', __name__)

# 🧾 CREATE ORDER
@orders_bp.route('/orders', methods=['POST'])
def create_order():
    data = request.json
    items = data.get("items", [])

    new_order = Order()
    total = 0

    db.session.add(new_order)
    db.session.flush()

    for item in items:
        book = Book.query.get(item["book_id"])
        quantity = item["quantity"]

        if not book or book.stock < quantity:
            return jsonify({"error": "Book not available"}), 400

        book.stock -= quantity
        total += book.price * quantity

        order_item = OrderItem(
            order_id=new_order.id,
              book_id=book.book_id, 
            quantity=quantity
        )

        db.session.add(order_item)

    new_order.total_price = total
    db.session.commit()

    return jsonify({
        "message": "Order created",
        "total": total
    })


# 📖 GET ALL ORDERS (ADD THIS)
@orders_bp.route('/orders', methods=['GET'])
def get_orders():
    orders = Order.query.all()
    return jsonify([order.to_dict() for order in orders])