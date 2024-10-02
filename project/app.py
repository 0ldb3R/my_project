from flask import Flask
from flask_jwt_extended import JWTManager
from models import db, User, Product
from routes import api

app = Flask(__name__)
app.config.from_object('config.Config')

db.init_app(app)
jwt = JWTManager(app)

with app.app_context():
    db.create_all()

    admin = User.query.filter_by(email='admin@shop.ru').first()
    if not admin:
        admin = User(fio='Администратор', email='admin@shop.ru', password='QWEasd123', role='admin')
        db.session.add(admin)

    client = User.query.filter_by(email='user@shop.ru').first()
    if not client:
        client = User(fio='Клиент', email='user@shop.ru', password='password', role='client')
        db.session.add(client)

    if not Product.query.first():
        products = [
            Product(name='Product name 1', description='Product description 1', price=100),
            Product(name='Product name 2', description='Product description 2', price=200),
        ]
        db.session.bulk_save_objects(products)

    db.session.commit()

app.register_blueprint(api, url_prefix='/api')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)