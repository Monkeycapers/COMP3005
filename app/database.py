from Types import ItemType, Author, Book, StoreItem, User, Address, Order
from main import Bcrypt, check_password_hash, generate_password_hash
from pprint import pprint
import Cart
import psycopg2
from psycopg2.extras import Json
import random, string

DEFAULT_FEATURED_ITEM_COUNT = 5
TRACKING_NUMBER_LENGTH = 64

def connect():
    conn = psycopg2.connect("dbname=BookExpress user=postgres password=root host=localhost")
    return conn

#because the db isnt ready yet
#returns a list of store items type=book 
def makeFakeBooks(count):
    items = []
    for i in range(count):
        storeItem = makeFakeBook(i, str("fakebook #" + str(i)))
        items.append(storeItem)
    return items

def makeFakeBook(_id, name):
    author = Author(0, None, "fake author")
    book = Book(_id, None, name, author, None, None, None, 500, "A fake description")
    bookType = ItemType.BOOK
    storeItem = StoreItem(_id, name, bookType, 3, book, 5, 500, 400, .5, 5)
    return storeItem

# Return <count> random store items from the Featured table
def getFeaturedItems(count=DEFAULT_FEATURED_ITEM_COUNT):
    return makeFakeBooks(count)

def getStoreItemById(_id):
    return makeFakeBook(_id, str("fakebook #" + str(_id)))

def getUserById(_id):
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT id, email, pw_hash FROM users WHERE id=%s", (_id,))

    res = cur.fetchone()

    cur.close()
    conn.close()

    if (res is not None):
        user = User(res[0], res[1], res[2])
        return user
    return None

def getUserByEmail(email, conn=None):
    conn = connect() if conn is None else conn
    cur = conn.cursor()
    cur.execute("SELECT id, email, pw_hash FROM users WHERE email=%s", (email,))

    res = cur.fetchone()

    pprint(res)
    #print("length of res: %d" % len(res))
    
    user = None
    if (res is not None and len(res) >= 3):
        user = User(res[0], res[1], res[2])

    cur.close()
    conn.close()

    return user

def addUser(email, password):
    
    password_hash = generate_password_hash(password).decode('utf-8')

    conn = connect()
    cur = conn.cursor()
    cur.execute("INSERT INTO users (email, pw_hash) VALUES (%s, %s)",
                (email, password_hash))

    cur.close()
    conn.commit()

    #todo kind of silly. but we need to know what the generated id is
    #todo replace with RETURNING id
    return getUserByEmail(email, conn)

# add an address; return address id 
def addAddress(country, city, province, street_name, cur):
    cur.execute("SELECT id FROM addr WHERE country=%s AND city=%s AND province=%s AND address=%s", (country, city, province, street_name))

    res = cur.fetchone()
    address_id = None
    if res is not None and len(res) >= 1:
        address_id = int(res[0])
    
    if address_id is None:
        #insert address, returning ID
        cur.execute("INSERT INTO addr (country, city, province, address) VALUES (%s, %s, %s, %s) RETURNING id", (country, city, province, street_name))

        #get our id
        res = cur.fetchone()
        if res is not None and len(res) >= 1:
            address_id = int(res[0])
    return address_id

def addOrder(cart, form):

    simple_cart = Cart.simplify(cart)
    tracking_number = makeTrackingNumber()

    conn = connect()
    cur = conn.cursor()

    b_address_id = addAddress(form['b-country'], form['b-city'], form['b-province'], form['b-address'], cur)
    s_address_id = addAddress(form['s-country'], form['s-city'], form['s-province'], form['s-address'], cur)

    # we do not store credit card information (typically you would interface with a payment provider for that)
    cur.execute("INSERT INTO orders (cart, first_name, last_name, tracking, b_address_id, s_address_id) VALUES (%s,%s,%s,%s,%s,%s) RETURNING id", 
                (Json(simple_cart), form['firstname'], form['lastname'], tracking_number, b_address_id, s_address_id))

    order_id = cur.fetchone()[0]
    conn.commit()

    billing_address = Address(b_address_id, form['b-country'], form['b-city'], form['b-province'], form['b-address'])
    shipping_address = Address(s_address_id, form['s-country'], form['s-city'], form['s-province'], form['s-address'])

    order = Order(order_id, tracking_number, form['firstname'], form['lastname'], billing_address, shipping_address)

    cur.close()
    conn.close()

    return order

# normally we would connect to an api once an order is 'shipped'
# for demonstration purposes just return a random string
def makeTrackingNumber():
    # source: https://stackoverflow.com/questions/2257441/random-string-generation-with-upper-case-letters-and-digits
    # pick TRACKING_NUMBER_LENGTH characters out of the list of uppercase characters and digits and join them together into a string
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=TRACKING_NUMBER_LENGTH))
