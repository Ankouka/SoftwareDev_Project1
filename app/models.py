from app import db
from flask_login import UserMixin
from sqlalchemy_utils import ScalarListType


class User(db.Model, UserMixin):  # general user class
    __tablename__ = 'users'
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String)
    # image_file=db.Column(db.String(20), nullable=False, default='default.png')
    email = db.Column(db.String)
    passwd = db.Column(db.LargeBinary)
    orders = db.relationship("Order")


class AdminUser(User):  # subclass of user with access to everything plus new methods
    __tablename__ = 'admin_user'
    admin_privilages = True

    # TODO: create specific type of user class that has access to all orders and can manipulate catalog items

    def add_item(self, sku, name, quantity, details):
        ...
        # TODO: sku = ID for item in database, quantity = # in stock (to be changed by users purchasing items),
        #  deails = description of what the door / window is
        new_item = Item(sku=sku, name=name, quantity=quantity, details=details)
        db.session.add(new_item)
        db.session.commit()
        # RETURN true or false depending on if the command was successful.
        try:
            return True
        except Exception as e:
            print(f"An Error Occured: {e}")
        return False

    def change_item(self, sku, name, quantity, details):
        # TODO: find item based on 'sku' and change name, quantity, and/or details
        try:
            item = Item.query.get(sku)
            if name:
                item.name = name
            if quantity:
                item.quantity = quantity
            if details:
                item.details = details
            db.session.commit()
            # RETURN true or false depending on if the command was successful.
            return True
        except Exception as e:
            print(f"An Error Occured: {e}")
        return False

    def remove_item(self, sku):
        # TODO: find item in catalog by sku and delete it
        try:
            item = Item.query.get(sku)
            db.session.delete(item)
            db.session.commit()
            # RETURN true or false depending on if the command was successful.
            return True
        except Exception as e:
            print(f"An Error Occured: {e}")
        return False
        ...


class Item(db.Model):  # items are doors and windows our company sells
    __tablename__ = 'catalog'  # TODO: tentative, can be named "items" instead but catalog fits our UML model
    sku = db.Column(db.String, primary_key=True)
    product_name = db.Column(db.String)
    price = db.Column(db.Float)
    order_number = db.Column(db.String)
    product_image = db.Column(db.String)
    product_code = db.Column(db.String)
    stock = db.Column(db.Integer)
    quantity_in_order = db.Column(db.Integer)
    specs = db.Column(db.String)


order_items_association = db.Table('order_items',
                                   db.Column('order_number', db.String, db.ForeignKey('orders.number')),
                                   db.Column('item_sku', db.String, db.ForeignKey('catalog.sku'))
                                   )


class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.String, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey("users.id"))
    number = db.Column(db.String, unique=True)
    title = db.Column(db.String)
    phone_number = db.Column(db.String)
    order_date = db.Column(db.String)
    status = db.Column(db.String)
    items = db.Column(ScalarListType())
    quantities = db.Column(ScalarListType())
