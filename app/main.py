import os
import database
from Types import ItemType
from flask import Flask, render_template

app = Flask(__name__)

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

@app.route('/about')
def about(name="About"):
    return render_template("about.j2", name=name)