import flask
# from flask_uploads import UploadSet, IMAGES, configure_uploads
from app import app, db, load_user
from app.models import User, AdminUser, Item, Order
from app.forms import SignUpForm, SignInForm, ItemForm, ProductForm, OrderForm
from flask import render_template, redirect, url_for, request, flash, send_from_directory
from flask_login import login_required, login_user, logout_user, current_user
from sqlalchemy.exc import IntegrityError
import bcrypt
import datetime


# pictures = UploadSet('pictures', IMAGES)
# app.config['UPLOADED_PICTURES_DEST']= 'C:\\Users\\nkouk\\project-1-windoors-dream-team'

# configure_uploads(app, pictures)

@app.route('/')
@app.route('/index')
@app.route('/index.html')
def index():
    return render_template('index.html')


# sign-in functionality from previous homework
@app.route('/users/signin', methods=['GET', 'POST'])
def users_signin():
    form = SignInForm()
    if form.validate_on_submit():
        user = db.session.query(User).filter_by(id=form.id.data).first()
        if user and bcrypt.checkpw(form.passwd.data.encode('utf-8'), user.passwd):
            login_user(user)

            # Check if the user has admin privileges
            if request.form.get("id") == "tmota" and request.form.get("passwd") == "1":
                return redirect(url_for('admin_all_orders'))
            else:
                return redirect(url_for('user_orders'))

        else:
            flash('Username and/or password not recognized. Please Try again')
            return render_template('users_signin.html', form=form)
    else:
        return render_template('users_signin.html', form=form)

# sign-up functionality from previous homework
@app.route('/users/signup', methods=['GET', 'POST'])
def users_signup():
    form = SignUpForm()
    if form.validate_on_submit():
        try:
            password = form.passwd.data
            confirm_password = form.passwd_confirm.data

            if password == confirm_password:
                hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                user = User(id=form.id.data, name=form.name.data, passwd=hashed)
                db.session.add(user)
                db.session.commit()
            else:
                flash('Passwords do not match. Please try again.')
                return render_template('users_signup.html', form=form)

            return render_template('index.html')  # redirect(url_for('index'))
        except IntegrityError:
            flash('Username already take. Please use a different ID')
            return render_template('users_signup.html', form=form)
    else:
        return render_template('users_signup.html', form=form)


# sign-out functionality from previous homework
@app.route('/users/signout', methods=['GET', 'POST'])
def users_signout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/user_orders')
@login_required
def user_orders():
    return render_template("user_orders.html", user=current_user, orders=current_user.orders)


@app.route('/products')
@login_required
def products():
    return render_template("products.html", user=current_user, products=db.session.query(Item))


# Original
# return render_template("products.html", user=current_user)

@app.route('/admin_products')
@login_required
def admin_products():
    # List of Temporary Products for baseline implementation
    return render_template("Admin_products.html", user=current_user, products=db.session.query(Item))


from flask import send_from_directory


# @app.route('/uploads/<filename>')
# def get_file(filename):
#     return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/products/create items', methods=['GET', 'POST'])
@login_required
def item_create():
    form = ItemForm()
    if form.validate_on_submit():
        # filename = pictures.save(form.product_image.data)
        # file_url = url_for('get_file', filename=filename)
        try:
            new_item = Item(sku=form.sku.data, product_name=form.product_name.data,
                            price=form.price.data, product_image=form.product_image.data,
                            stock=form.stock.data, specs=form.specs.data)
            db.session.add(new_item)
            db.session.commit()

            return redirect(url_for('admin_all_orders'))
        except IntegrityError:
            db.session.rollback()
            flash('Product Code already exists. Please use a differnt Product Code', 'danger')

    return render_template('create_items.html', form=form)


@app.route('/products/change_item', methods=['GET', 'POST'])
@login_required
def change_item():
    items = db.session.query(Item)
    form = ItemForm()
    if form.validate_on_submit():
        item = Item.query.get(form.sku.data)
        item.product_name = form.product_name.data
        item.stock = form.stock.data
        item.price = form.price.data
        item.product_image = form.product_image.data
        item.specs = form.specs.data
        db.session.commit()
        return redirect(url_for('admin_products'))
    return render_template("change_item.html", items=items, form=form)


@app.route('/admin/', methods=['POST', 'GET'])
@login_required
def admin_all_orders():
    return render_template("admin_all_orders.html", user=current_user, orders=db.session.query(Order))


@app.route('/orders/<int:order_id>/', methods=['POST', 'GET', 'DELETE'])
@login_required
def delete_order(order_id):
    order = Order.query.get(order_id)
    for item in order.items:
        item.stock = item.stock + order.items.quantity_in_order
        db.session.add(item)
    db.session.delete(order)
    db.session.commit()
    return render_template('products.html', item=item)

@app.route('/change_status/<int:order_id>', methods=['GET', 'POST'])
@login_required
def change_status(order_id):
    order = Order.query.get(order_id)
    return render_template('change_status.html', order=order)

@app.route('/update_status/<int:order_id>', methods=['GET', 'POST'])
@login_required
def update_status(order_id):
    order = Order.query.get(order_id)
    new_status = request.form['change_status']
    order.status = new_status
    db.session.commit()
    return redirect(url_for('admin_all_orders'))

@app.route('/orders/create order', methods=['POST', 'GET'])
@login_required
def create_order():
    if request.method == 'POST':
        output = request.form.to_dict()
        print(output)
        items = []
        quantities = []

        for key in output:
            if output[key] != "" and output[key] is not None and key != "id":
                if Item.query.get(key).stock < int(output[key]):
                    flash("We don't have enough of an item you requested!")
                    return render_template("create_order.html", user=current_user, products=db.session.query(Item))
                items.append(key)
                quantities.append(output[key])

        # for key in output:
        #     if output[key] != "" and output[key] is not None and key != "id":
        #         if Item.query.get(key).stock < int(output[key]):
        #             flash("We don't have enough of an item you requested!")
        #             return render_template("create_order.html", user=current_user, products=db.session.query(Item))
        #         items.append(key)
        #         quantities.append(output[key])
        #         Item.query.get(key).stock -= int(output[key])
        #         db.session.commit()

        if output is None or len(items) == 0:
            flash("You must enter an item!")
            return render_template("create_order.html", user=current_user, products=db.session.query(Item))
        elif  output["id"] is None:
            flash("Invalid ID!")
            return render_template("create_order.html", user=current_user, products=db.session.query(Item))
        elif output["id"] == "":
            flash("Invalid ID!")
            return render_template("create_order.html", user=current_user, products=db.session.query(Item))
        else:
            existing_ids = []
            for order in db.session.query(Order):
                existing_ids.append(order.id)
            if output["id"] in existing_ids:
                flash("That ID is already in use!")
                return render_template("create_order.html", user=current_user, products=db.session.query(Item))
            for key in output:
                #if output[key] != "" and output[key] is not None and key != "id":
                 #   if Item.query.get(key).stock < int(output[key]):
                 #       flash("We don't have enough of an item you requested!")
                 #       return render_template("create_order.html", user=current_user, products=db.session.query(Item))
                   # items.append(key)
                   # quantities.append(output[key])
                if output[key] != "" and output[key] is not None and key != "id":
                    Item.query.get(key).stock -= int(output[key])
                    db.session.commit()

            new_order = Order(id=output["id"], order_date=datetime.date.today().strftime("%m/%d/%Y"),
                              user_id=current_user.id, status="Ordered", items=items, quantities=quantities)
            db.session.add(new_order)
            db.session.commit()
            if current_user.id == "tmota":
                return redirect(url_for('admin_all_orders'))
            return redirect(url_for('user_orders'))
    else:
        return render_template("create_order.html", user=current_user, products=db.session.query(Item))

@app.route('/orders/view_order', methods=['GET', 'POST'])
@login_required
def view_order():
    try:
        request.args.get("order_id")
        order_id = request.args.get("order_id")
    except:
        flash("Invalid input!")
        if current_user.id == "tmota":
            return redirect(url_for('admin_all_orders'))
        return redirect(url_for('user_orders'))
    order = Order.query.get(order_id)
    items = []
    total = []
    idx = 0
    for item in order.items:
        items.append(Item.query.get(item))
        total.append(Item.query.get(item).price * float(order.quantities[idx]))
        idx += 1
    return render_template("view_order.html", items=items, quantities=order.quantities, total=total, order=order, user_id=current_user.id)

@app.route('/order_return')
@login_required
def order_return():
    if current_user.id == "tmota":
        return redirect(url_for('admin_all_orders'))
    return redirect(url_for('user_orders'))
