from flask import Flask, request
import json
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import raw_data


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False    #настройка позволяет не грузить ПК
db = SQLAlchemy(app)

#получаем словарь
def get_response(data) -> json:
    return json.dumps(data), 200, {'Content-Type': 'application/json; charset=utf-8'}


#создаем модель User
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    age = db.Column(db.Integer)
    email = db.Column(db.String(100))
    role = db.Column(db.String(10))
    phone = db.Column(db.String(100))

    #в словарь
    def to_dict(self):
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}



#создаем модель Order
class Order(db.Model):
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String())
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    address = db.Column(db.String(100))
    price = db.Column(db.Integer)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    executor_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    #в словарь
    def to_dict(self):
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}



#создаем модель Offer (промежуточная таблица)
class Offer(db.Model):
    __tablename__ = 'offer'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    executor_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    #в словарь
    def to_dict(self):
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}


with app.app_context():
    db.create_all()

#распаковка **usr_data (users)
    for usr_data in raw_data.users:
        db.session.add(User(**usr_data))
        db.session.commit()

        #users = [User(**usr_data) for usr_data in raw_data.users]
        #db.session.add_all(users)
        #также можно один commit в конце

        #перевод в формат datetime, так как в orders есть формат '05/20/2005'
        #from datetime import datetime
        #d = '02/08/2013'
        #date_obj = datetime.strptime(d, '%m/%d/%Y').date()
        #datetime.date(2013, 2, 8)

        # распаковка **ord_data (orders)
    for ord_data in raw_data.orders:
        ord_data['start_date'] = datetime.strptime(ord_data['start_date'], '%m/%d/%Y').date()
        ord_data['end_date'] = datetime.strptime(ord_data['end_date'], '%m/%d/%Y').date()
        db.session.add(Order(**ord_data))
        db.session.commit()


        # распаковка **ofr_data (offers)
    for ofr_data in raw_data.offers:
        db.session.add(Offer(**ofr_data))
        db.session.commit()



#User - users
#получение (GET) списка пользователей и добавление нового пользователя (POST) в Postman
@app.route('/users', methods=['GET', 'POST'])
def users():
    if request.method == 'GET':
        users = User.query.all()
        res = [usr.to_dict() for usr in users]
        return get_response(res)
    elif request.method == 'POST':
        user_data = json.loads(request.data)
        db.session.add(User(**user_data))
        db.session.commit()
        return '', 201


#получение пользователя по id, обновление и удаление через Postman
@app.route('/users/<int:uid>', methods=['GET', 'PUT', 'DELETE'])
def user(uid: int):
    user = User.query.get(uid)
    if request.method == 'GET':
        return get_response(user.to_dict())
    if request.method == 'DELETE':
        db.session.delete(user)
        db.session.commit()
        return '', 204
    if request.method == 'PUT':
        user_data = json.loads(request.data)
        user.first_name = user_data['first_name']
        user.last_name = user_data['last_name']
        user.age = user_data['age']
        user.email = user_data['email']
        user.role = user_data['role']
        user.phone = user_data['phone']
        db.session.add(user)
        db.session.commit()
        return '', 204



#Order - orders
#получение (GET) списка пользователей и добавление нового пользователя (POST) в Postman
@app.route('/orders', methods=['GET', 'POST'])
def orders():
    if request.method == 'GET':
        orders = Order.query.all()
        res = []
        for order in orders:
            ord_dict = order.to_dict()
            ord_dict['start_date'] = str(ord_dict['start_date'])
            ord_dict['end_date'] = str(ord_dict['end_date'])
            res.append(ord_dict)
        return get_response(res)
    elif request.method == 'POST':
        order_data = json.loads(request.data)
        db.session.add(Order(**order_data))
        db.session.commit()
        return '', 201


#получение пользователя по id, обновление и удаление через Postman
@app.route('/orders/<int:oid>', methods=['GET', 'PUT', 'DELETE'])
def order(oid: int):
    order = Order.query.get(oid)
    if request.method == 'GET':
        ord_dict = order.to_dict()
        ord_dict['start_date'] = str(ord_dict['start_date'])
        ord_dict['end_date'] = str(ord_dict['end_date'])
        return get_response(ord_dict)
    if request.method == 'DELETE':
        db.session.delete(order)
        db.session.commit()
        return '', 204
    if request.method == 'PUT':
        order_data = json.loads(request.data)
        order_data['start_date'] = datetime.strptime(order_data['start_date'], '%Y-%m-%d').date()
        order_data['end_date'] = datetime.strptime(order_data['end_date'], '%Y-%m-%d').date()

        order.name = order_data['name']
        order.description = order_data['description']
        order.start_date = order_data['start_date']
        order.end_date = order_data['end_date']
        order.price = order_data['price']
        order.customer_id = order_data['customer_id']
        order.executor_id = order_data['executor_id']
        db.session.add(order)
        db.session.commit()
        return '', 204



#Order - offers
#получение (GET) списка пользователей и добавление нового пользователя (POST) в Postman
@app.route('/offers', methods=['GET', 'POST'])
def offers():
    if request.method == 'GET':
        offers = Offer.query.all()
        res = [offer.to_dict() for offer in offers]
        return get_response(res)
    elif request.method == 'POST':
        offer_data = json.loads(request.data)
        db.session.add(Offer(**offer_data))
        db.session.commit()
        return '', 201


#получение пользователя по id, обновление и удаление через Postman
@app.route('/offers/<int:oid>', methods=['GET', 'PUT', 'DELETE'])
def offer(oid: int):
    offer = Offer.query.get(oid)
    if request.method == 'GET':
        return get_response(offer.to_dict())
    if request.method == 'DELETE':
        db.session.delete(offer)
        db.session.commit()
        return '', 204
    if request.method == 'PUT':
        offer_data = json.loads(request.data)
        offer.order_id = offer_data['order_id']
        offer.executor_id = offer_data['executor_id']
        db.session.add(offer)
        db.session.commit()
        return '', 204




if __name__ == '__main__':
    app.run(debug=True)
