from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, unset_jwt_cookies
from models import db, User, Product, CartItem, Order

api = Blueprint('api', __name__)

@api.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    if not data or not all(k in data for k in ("fio", "email", "password")):
        return jsonify({"message": "Validation error"}), 422
    existing_user = User.query.filter_by(email=data['email']).first()
    if existing_user:
        return jsonify({"message": "Email already exists"}), 422
    user = User(fio=data['fio'], email=data['email'], password=data['password'], role='client')
    db.session.add(user)
    db.session.commit()
    token = create_access_token(identity=user.id)
    return jsonify({"user_token": token}), 201

@api.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not all(k in data for k in ("email", "password")):
        return jsonify({"message": "Validation error"}), 422
    user = User.query.filter_by(email=data['email'], password=data['password']).first()
    if user:
        token = create_access_token(identity=user.id)
        return jsonify({"user_token": token}), 200
    return jsonify({"message": "Auth failed"}), 401

@api.route('/logout', methods=['GET'])
@jwt_required()
def logout():
    response = jsonify({"message": "logout"})
    unset_jwt_cookies(response)
    return response, 200

@api.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify([{"id": p.id, "name": p.name, "description": p.description, "price": p.price} for p in products]), 200

@api.route('/cart/<int:product_id>', methods=['POST'])
@jwt_required()
def add_to_cart(product_id):
    user_id = get_jwt_identity()
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"message": "Product not found"}), 404
    cart_item = CartItem.query.filter_by(user_id=user_id, product_id=product_id).first()
    if cart_item:
        cart_item.quantity += 1
    else:
        cart_item = CartItem(user_id=user_id, product_id=product_id, quantity=1)
        db.session.add(cart_item)
    db.session.commit()
    return jsonify({"message": "Product added to cart"}), 201

@api.route('/cart', methods=['GET'])
@jwt_required()
def view_cart():
    user_id = get_jwt_identity()
    cart_items = CartItem.query.filter_by(user_id=user_id).all()
    return jsonify([{
        "id": item.id,
        "product_id": item.product_id,
        "name": item.product.name,
        "description": item.product.description,
        "price": item.product.price,
        "quantity": item.quantity
    } for item in cart_items]), 200

@api.route('/cart/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_from_cart(id):
    user_id = get_jwt_identity()
    cart_item = CartItem.query.get(id)
    if not cart_item:
        return jsonify({"message": "Item not found"}), 404
    if cart_item.user_id != user_id:
        return jsonify({"message": "Forbidden for you"}), 403
    db.session.delete(cart_item)
    db.session.commit()
    return jsonify({"message": "Item removed from cart"}), 200

@api.route('/order', methods=['POST'])
@jwt_required()
def place_order():
    user_id = get_jwt_identity()
    cart_items = CartItem.query.filter_by(user_id=user_id).all()
    if not cart_items:
        return jsonify({"error": {"code": 422, "message": "Cart is empty"}}), 422
    order_price = sum(item.product.price * item.quantity for item in cart_items)
    order = Order(user_id=user_id, order_price=order_price)
    db.session.add(order)
    for item in cart_items:
        order.products.append(item.product)
        db.session.delete(item)
    db.session.commit()
    return jsonify({"order_id": order.id, "message": "Order is processed"}), 201

@api.route('/order', methods=['GET'])
@jwt_required()
def view_orders():
    user_id = get_jwt_identity()
    orders = Order.query.filter_by(user_id=user_id).all()
    return jsonify([{
        "id": order.id,
        "products": [product.id for product in order.products],
        "order_price": order.order_price
    } for order in orders]), 200

@api.route('/product', methods=['POST'])
@jwt_required()
def add_product():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if user.role != 'admin':
        return jsonify({"message": "Forbidden"}), 403
    data = request.get_json()
    if not data or not all(k in data for k in ("name", "description", "price")):
        return jsonify({"message": "Validation error"}), 422
    product = Product(name=data['name'], description=data['description'], price=data['price'])
    db.session.add(product)
    db.session.commit()
    return jsonify({"id": product.id, "message": "Product added"}), 201

@api.route('/product/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_product(id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if user.role != 'admin':
        return jsonify({"message": "Forbidden"}), 403
    product = Product.query.get(id)
    if not product:
        return jsonify({"message": "Product not found"}), 404
    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": "Product removed"}), 200

@api.route('/product/<int:id>', methods=['PATCH'])
@jwt_required()
def edit_product(id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if user.role != 'admin':
        return jsonify({"message": "Forbidden"}), 403
    product = Product.query.get(id)
    if not product:
        return jsonify({"message": "Product not found"}), 404
    data = request.get_json()
    if 'name' in data:
        product.name = data['name']
    if 'description' in data:
        product.description = data['description']
    if 'price' in data:
        product.price = data['price']
    db.session.commit()
    return jsonify({
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "price": product.price
    }), 200