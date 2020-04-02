import os

import flask

from flask import Flask, render_template, session, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, current_user, login_required
from flask_bcrypt import Bcrypt, check_password_hash, generate_password_hash
from pprint import pprint

app = Flask(__name__)

app.secret_key = "dev" #todo real secret key

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

bcrypt = Bcrypt(app)

from Types import ItemType, StoreItem
from Cart import addItemToCart, removeItemFromCart, deleteItemFromCart, validate, updateCartItem
import database

def getFormattedCurrency(value):
    return "$" + format((value / 100), ',.2f')

#expose our enums to the template engine
@app.context_processor
def inject_enums():
    def is_book(item):
        return item.item_type == ItemType.BOOK
    return dict(is_book=is_book)

#login code
@login_manager.user_loader
def load_user(user_id):
    return database.getUserById(user_id)

@app.route('/')
@app.route('/home')
def main(name="Home"):
    featured = {
        "Featured: ": {"items": database.getFeaturedItems(), "url":"#"}
    }
    print("???")
    pprint(featured["Featured: "]["items"][0])
    return render_template("home.j2", name=name, featured=featured)

def handle_item_details(item_id):
    item = database.getStoreItemById(item_id)
    if (item.isBook()):
      return render_template("book.j2", item=item, book=item.item, author=item.item.author)
    return render_template("item.j2", item=item)

@app.route('/img/<int:item_id>:<string:size>')
def image(item_id, size):
    pass

@app.route('/item/<int:item_id>')
def item_details(item_id):
    return handle_item_details(item_id)

#silently discard slug
@app.route('/item/<int:item_id>/<string:slug>')
def item_details_with_slug(item, slug):
    return handle_item_details(item)

@app.route('/account')
@login_required
def account():
    return render_template("account.j2", user=current_user)

@app.route('/login', methods=['POST', 'GET'])
def login(name='login'):
    if request.method == 'GET':
        return render_template('login.j2')
    else:
        #todo server side validation
        email = str(request.form['email'])
        password = str(request.form['password'])
        next_page = str(request.form['next'])
        remember = 'remember' in request.form

        user = database.getUserByEmail(email)

        if user is not None and user.test_password(password):
            login_user(user, remember)
            #if not is_safe_url(next):
            #    return flask.abort(400)
            return redirect(next_page or url_for('/'))
        else:
            flash("Invalid email or password!")
            return redirect(url_for('login'))

        

@app.route('/register', methods=['POST', 'GET'])
def register(name='register'):
    if request.method == 'GET':
        return render_template('register.j2')
    else:
        #todo server side validation

        email = str(request.form['email'])
        password = str(request.form['password'])
        next_page = str(request.form['next'])
        remember = 'remember' in request.form

        if database.getUserByEmail(email) is not None: #user already exists
            print("User already exists!")
            flash("User already exists!")
            return redirect(url_for('register'))
        else:
            # add user
            user = database.addUser(email, password)
            pprint(user)
            # log the user in
            login_user(user, remember)
            return redirect(next_page or url_for('/'))

@app.route('/cart')
def cart(name="cart"):
    if "cart" in session:
        pprint(session["cart"])
        res = validate(session["cart"])
        cart = res['cart']
        total_price = res['totalPrice']
        total_discount = res['totalDiscount']
        return render_template("cart.j2", hasCart=True, cart=cart,
         total_price=total_price, formatted_total_price=getFormattedCurrency(total_price),
         total_discount=total_discount, formatted_total_discount=getFormattedCurrency(total_discount))
    return render_template("cart.j2", hasCart=False)

@app.route('/addcart', methods=['POST'])
def addcart():
    if not "cart" in session:
        session['cart'] = {}
    item_id = request.form['itemId']
    print("item_id: " + item_id)
    quantity = int(request.form['quantity'])
    store_item = database.getStoreItemById(item_id)
    if store_item is not None:
        session['cart'] = addItemToCart(session['cart'], store_item, quantity)
        return redirect(url_for('cart'))
    flash("Error: item_id " + item_id + " does not exist!")

@app.route('/updatecart', methods=['POST'])
def updatecart():
    if not "cart" in session:
        flash("No valid cart!")
        return
    item_id = request.form['itemId']
    print("item_id: " + item_id)
    quantity = int(request.form['quantity'])
    store_item = database.getStoreItemById(item_id)
    if store_item is not None:
        session['cart'] = updateCartItem(session['cart'], store_item, quantity)
        return redirect(url_for('cart'))
    flash("Error: item_id " + item_id + " does not exist!")
    
@app.route('/about')
def about(name="About"):
    return render_template("about.j2", name=name)