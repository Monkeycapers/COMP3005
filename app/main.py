import os, copy

import flask

from flask import Flask, render_template, session, redirect, url_for, request, flash, abort
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
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

# login code

@login_manager.user_loader
def load_user(user_id):
    return database.getUserById(user_id)

@app.template_filter('format_currency')
def format_currency(i):
    return getFormattedCurrency(int(i))

# Home Page

@app.route('/')
@app.route('/home')
def main(name="Home"):
    featured = {
        "Featured: ": {"items": database.getFeaturedItems(), "url":"#"}
    }
    print("???")
    pprint(featured["Featured: "]["items"][0])
    return render_template("home.j2", name=name, featured=featured)

# Order Details
@app.route('/orderdetails/<int:order_id>')
@login_required
def orderdetails(order_id):
    order_item = database.getOrderById(order_id)
    cart = order_item.cart_json
    if current_user.super_user or order_item.user_id == current_user.id:
        return render_template("orderdetails.j2", order=order_item, cart = cart)
    else:
        return flask.abort(401)

# Item Details

def handle_item_details(item_id):
    item = database.getStoreItemById(item_id)
    if (item.isBook()):
      #author_items = database.getSomeBooksByAuthor(author_id=item.item.author.id)
      return render_template("book.j2", item=item, book=item.item, author=item.item.author) #, auhtor_items=author_items)
    return render_template("item.j2", item=item)

@app.route('/item/<int:item_id>')
def item_details(item_id):
    return handle_item_details(item_id)

#silently discard slug
@app.route('/item/<int:item_id>/<string:slug>')
def item_details_with_slug(item, slug):
    return handle_item_details(item)

# Author Details / Items

def handle_author(author_id):
    page = request.args.get(key="page", default=1, type=int)
    sort = request.args.get(key="sort", default=None, type=str)
    author, author_items, is_next_page = database.getBooksByAuthor(author_id, sort, page)
    if author is None:
        return abort(404)
    return render_template("author.j2", author=author, items=author_items, page=page, sort=sort, page_name='author', is_next_page=is_next_page)
    
@app.route('/author/<int:last_bit>')
def author(last_bit):
    return handle_author(last_bit)

# Publisher Items

def handle_publisher(publisher_id):
    page = request.args.get(key="page", default=1, type=int)
    sort = request.args.get(key="sort", default=None, type=str)
    publisher, publisher_items, is_next_page = database.getBooksByPublisher(publisher_id, sort, page)
    if publisher is None:
        return abort(404)
    return render_template("publisher.j2", publisher=publisher, items=publisher_items, page=page, sort=sort, page_name='publisher', is_next_page=is_next_page)
    
@app.route('/publisher/<int:last_bit>')
def publisher(last_bit):
    return handle_publisher(last_bit)

# Browse/Search

@app.route('/browse')
def browse():

    search = request.args.get(key='search', default=None, type=str)
    query = request.args.get(key='query', default=None, type=str)
    page = request.args.get(key="page", default=1, type=int)
    sort = request.args.get(key="sort", default=None, type=str)

    if search is None:
        return render_template("browse.j2", has_result=False)
    if search == 'isbn':
        item_id = database.getStoreItemIDByISBN(query)
        if item_id is None:
            return render_template("browse.j2", has_error=True, error="Whoops! We do not have any books with the isbn: %s" % (query))
        else:
            return redirect(url_for('item_details', item_id=item_id))
    else:
        #this search can be handled by paged_query
        items, is_next_page = database.search(search, query, page, sort)
        if len(items) == 1:
            return redirect(url_for('item_details', item_id=items[0].id))
        elif len(items) == 0:
            return render_template("browse.j2", has_error=True, error="Whoops! No books found for the query %s" % (query))
        else:
            return render_template("browse.j2", has_result=True, items=items, page=page, sort=sort, is_next_page=is_next_page, query=query, search=search)
    return render_template("browse.j2", has_result=False)


# Account

@app.route('/account')
@login_required
def account():
    pprint(current_user)
    order_items = database.getUserOrders(current_user)
    return render_template("account.j2", user=current_user, order_items=order_items)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main'))

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

        if user is not None and check_password_hash(user.password_hash, password):
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

# Cart

@app.route('/cart')
def cart(name="cart"):
    if "cart" in session:
        print("Cart: ")
        pprint(session["cart"])
        #c = session["cart"]
        res = validate(copy.deepcopy(session["cart"]))
        cart = res['cart']
        #session["cart"] = c
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
        return flask.abort(400)
    item_id = request.form['itemId']
    print("item_id: " + item_id)
    quantity = int(request.form['quantity'])
    store_item = database.getStoreItemById(item_id)
    if store_item is not None:
        session['cart'] = updateCartItem(session['cart'], store_item, quantity)
        return redirect(url_for('cart'))
    flash("Error: item_id " + item_id + " does not exist!")

# Checkout

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    if not "cart" in session:
        flash("No valid cart!")
        return flask.abort(400)

    #todo: FAIL if anything in the cart changed
    res = validate(session["cart"])
    cart = res['cart']
    total_price = res['totalPrice']
    total_discount = res['totalDiscount']
    if request.method == 'GET':
        return render_template("checkout.j2", cart=cart, user=current_user,
                total_price=total_price, formatted_total_price=getFormattedCurrency(total_price),
                total_discount=total_discount, formatted_total_discount=getFormattedCurrency(total_discount))
    else:
        order = database.addOrder(cart, total_price, total_discount, request.form, current_user)
        if order is not None:
            #success, so we can dump the cart
            del session["cart"]
            return render_template("orderconfirm.j2", order=order)
        return flask.abort(400)

# Misc
        
@app.route('/about')
def about(name="About"):
    return render_template("about.j2", name=name)

@app.route('/admin')
@login_required
def admin(name="Admin"):
    if current_user.super_user:
        return render_template("admin.j2")
    flash("User is not a super_user!")
    return flask.abort(401)
