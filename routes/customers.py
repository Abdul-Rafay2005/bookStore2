from flask import Blueprint, jsonify, request
from database import db
from models import Customer

customers_bp = Blueprint('customers', __name__, url_prefix='/api')

@customers_bp.route('/customers', methods=['GET'])
def get_customers():
    customers = Customer.query.all()
    return jsonify([c.to_dict() for c in customers])

@customers_bp.route('/customers/<int:customer_id>', methods=['GET'])
def get_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    return jsonify(customer.to_dict())

@customers_bp.route('/customers', methods=['POST'])
def add_customer():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data received'}), 400
        if not data.get('name'):
            return jsonify({'error': 'Name is required'}), 400
        if not data.get('email'):
            return jsonify({'error': 'Email is required'}), 400

        # Check duplicate email
        existing = Customer.query.filter_by(email=data['email'].strip()).first()
        if existing:
            return jsonify({'error': f'Customer with email "{data["email"]}" already exists'}), 409

        customer = Customer(
            name=data['name'].strip(),
            email=data['email'].strip(),
            phone=data.get('phone') or None,
            address=data.get('address') or None
        )
        db.session.add(customer)
        db.session.commit()
        return jsonify(customer.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@customers_bp.route('/customers/<int:customer_id>', methods=['PUT'])
def update_customer(customer_id):
    try:
        customer = Customer.query.get_or_404(customer_id)
        data = request.get_json()
        customer.name    = data.get('name', customer.name).strip()
        customer.email   = data.get('email', customer.email).strip()
        customer.phone   = data.get('phone', customer.phone)
        customer.address = data.get('address', customer.address)
        db.session.commit()
        return jsonify(customer.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@customers_bp.route('/customers/<int:customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    try:
        customer = Customer.query.get_or_404(customer_id)
        db.session.delete(customer)
        db.session.commit()
        return jsonify({'message': 'Customer deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
