import uuid

from models.shared import db


class Item(db.Model):
    __name__ = 'item'
    name = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=False)
    type = db.Column(db.Text, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.REAL, nullable=False)
    id = db.Column(db.VARCHAR, primary_key=True, nullable=False)
    user_id = db.Column(db.VARCHAR, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return '<Item %r>' % self.name

    @staticmethod
    def json_data(name, description, type, quantity, price, id, user_id):
        return {
            "name": name,
            "description": description,
            "type": type,
            "quantity": quantity,
            "price": price,
            "id": id,
            "user_id": user_id
        }

    @staticmethod
    def create(name, description, type, price, user_id, quantity=1, id=None):
        if id is None:
            id = uuid.uuid4().hex
        else:
            id = id
        item = Item(name=name, description=description, type=type, price=price, user_id=user_id,
                    quantity=quantity, id=id)
        db.session.add(item)
        db.session.commit()

    @staticmethod
    def view():
        item_list = []
        items = Item.query.all()
        for item in items:
            item_list.append(Item.json_data(item.name, item.description, item.type, item.quantity,
                                                   item.price, item.id, item.user_id))
        return item_list

    @staticmethod
    def find_one(id):
        try:
            item = Item.query.filter_by(id=id).first()
            return Item.json_data(item.name, item.description, item.type, item.quantity, item.price, item.id, item.user_id)
        except:
            return None

    @staticmethod
    def update(id, data):
        item = Item.query.filter_by(id=id).first()
        if "name" in data:
            item.name = data['name']
        if 'description' in data:
            item.description = data['description']
        if 'type' in data:
            item.type = data['type']
        if 'quantity' in data:
            item.quantity = data['quantity']
        if 'price' in data:
            item.price = data['price']

        db.session.commit()

    @staticmethod
    def delete(id):
        item = Item.query.filter_by(id=id).first()
        db.session.delete(item)
        db.session.commit()

    @staticmethod
    def buy(id, quantity):
        item = Item.find_one(id)
        new_quantity = item["quantity"] - quantity
        Item.update(id, {"quantity": new_quantity})
        db.session.commit()