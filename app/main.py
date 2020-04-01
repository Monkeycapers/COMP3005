import os
import database
from Types import ItemType, StoreItem
from Cart import addItemToCart, removeItemFromCart, deleteItemFromCart, validate, updateCartItem
from flask import Flask, render_template, session, redirect, url_for, request, flash
from pprint import pprint

app = Flask(__name__)

app.secret_key = "dev" #todo real secret key

def getFormattedCurrency(value):
    return "$" + format((value / 100), ',.2f')

#expose our enums to the template engine
@app.context_processor
def inject_enums():
    def is_book(item):
        return item.item_type == ItemType.BOOK
    return dict(is_book=is_book)

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