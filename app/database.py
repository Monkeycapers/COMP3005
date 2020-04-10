from Types import ItemType, Author, Book, StoreItem, User, Address, Order, Publisher
from main import Bcrypt, check_password_hash, generate_password_hash
from flask import abort
from pprint import pprint
import Cart, Constants
import psycopg2
from psycopg2.extras import Json
import random, string
import math

DEFAULT_FEATURED_ITEM_COUNT = 7
TRACKING_NUMBER_LENGTH = 64

def connect():
    conn = psycopg2.connect("dbname=BookExpress user=postgres password=root host=localhost")
    return conn

def addBankingAccount(cur, balance):
    cur.execute("INSERT INTO bank_accounts (balance) VALUES (%s) RETURNING id",
                (balance,))
    res = cur.fetchone()
    return res[0]

def addPublisher(cur, name, address_id, banking_account_id):
    cur.execute("INSERT INTO publisher (name, address_id, banking_account_id) VALUES (%s, %s, %s) RETURNING id",
                (name, address_id, banking_account_id))
    res = cur.fetchone()
    return res[0]

def addBook(cur, name, source_key, author_id, publisher_id, isbn, page_count, description, genre):
    cur.execute("INSERT INTO book (source_key, name, author_id, publisher_id, isbn, page_count, description, genre) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id",
                (source_key, name, author_id, publisher_id, isbn, page_count, description, genre))
    res = cur.fetchone()
    return res[0]

def addStoreItem(cur, ref_id, item_type, name, quantity, price, discount_price, revenue_share_percent, auto_order_threshold, image_file_name):
    cur.execute("INSERT INTO store_items (ref_id, item_type, name, quantity, price, discount_price, revenue_share_percent, auto_order_threshold, img_file_name) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id",
    (ref_id, item_type, name, quantity, price, discount_price, revenue_share_percent, auto_order_threshold, image_file_name))
    res = cur.fetchone()
    return res[0]

def addAuthor(cur, source_key, name):
    cur.execute("INSERT INTO author (source_key, name) VALUES (%s, %s) RETURNING id", (source_key,name))
    res = cur.fetchone()
    return res[0]

def getPublisherById(cur, _id):
    cur.execute("SELECT * FROM publisher WHERE id=%s",
    (_id,))
    res = cur.fetchone()
    return Publisher(_id, res[1], res[2], res[3])

def getAuthorById(cur, _id):
    cur.execute("SELECT * FROM author WHERE id=%s",
    (_id,))
    res = cur.fetchone()
    return Author(_id, res[1], res[2])

# Return <count> random store items from the Featured table
def getFeaturedItems(count=DEFAULT_FEATURED_ITEM_COUNT):
    conn = connect()
    cur = conn.cursor()
    #see https://www.postgresql.org/docs/current/tsm-system-rows.html
    cur.execute("SELECT * FROM featured_items NATURAL RIGHT JOIN store_items TABLESAMPLE SYSTEM_ROWS(%s)" % (count,))
    allres = cur.fetchall()
    items = []
    for res in allres:
        pointer_obj = resolveRef(res[1], res[2], cur)
        store_item = StoreItem(res[1], res[3], ItemType(res[2]), pointer_obj, res[4], res[5], res[6], res[7], res[8], res[9])
        items.append(store_item)
    cur.close()
    conn.close()
    return items

def resolveRef(_id, item_type, cur):
    print("resolve Ref for _id %d type %d" % (_id, item_type))
    if item_type == ItemType.BOOK.value:
        print("book")
        cur.execute("SELECT * FROM book WHERE id=%s",
                    (_id,))
        res = cur.fetchone()
        print("Res:")
        pprint(res)
        if res is not None:
            book = Book(_id, res[1], res[2], getAuthorById(cur,res[3]), getPublisherById(cur,res[4]), res[5], res[8], res[6], res[7])
            pprint(book)
            return book
    return None

def getStoreItemById(_id):
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM store_items WHERE id=%s",
    (_id,))
    res = cur.fetchone()
    store_item = None
    if res is not None:
        pointer_obj = resolveRef(res[1], res[2], cur)
        store_item = StoreItem(_id, res[3], ItemType(res[2]), pointer_obj, res[4], res[5], res[6], res[7], res[8], res[9])

    cur.close()
    conn.close()
    return store_item
    #return makeFakeBook(_id, str("fakebook #" + str(_id)))

def getStoreItemIDByISBN(isbn):
    #get book's id
    conn = connect()
    cur = conn.cursor()

    cur.execute("SELECT id FROM book WHERE isbn=%s",
                (isbn,))
    
    res = cur.fetchone()
    book_id = -1
    if res is not None:
        book_id = res[0]
    store_id = None
    if book_id != -1:
        cur.execute("SELECT id FROM store_items WHERE ref_id=%s",
                    (book_id,))
        res = cur.fetchone()
        if res is not None:
            store_id = res[0]

    cur.close()
    conn.close()

    return store_id

# Start Paged Items
# for now paging only supported for books (WHERE item_type=ItemType.BOOK.value)

# define mapping from kwarg => sql query (WHERE id=..., etc)
KWARG_TO_SQL = {
    "author_id": {"flag": None, "query":"book.author_id=%s"},
    "publisher_id": {"flag": None, "query":"book.publisher_id=%s"},
    "author_name": {"flag": "author", "query":"author.name ~ %s"},
    "publisher_name": {"flag": "publisher", "query":"publisher.name ~ %s"},
    "book_name":{"flag": None, "query":"book.name ~ %s"},
    "genre":{"flag": None, "query":"book.genre ~ %s"},
    "isbn": {"flag": None, "query":"book.isbn=%s"}
}

SORT_TO_SQL = {
    "price_low": "ORDER BY store_items.discount_price ASC",
    "price_high": "ORDER BY store_items.discount_price DESC",
    "name_A-Z": "ORDER BY store_items.name ASC",
    "name_Z-A": "ORDER BY store_items.name DESC"
}

def doPagedQuery(cur, page, sort, amount=Constants.PAGE_AMOUNT, **kwargs):
    #determine what tables to join with
    flags = {
        "author":False, #grab details from author
        "publisher": False
    }
    #initial query string
    queryStr = "SELECT * FROM store_items FULL OUTER JOIN book ON book.id=store_items.ref_id "

    endStr = "WHERE "
    didFirst = False

    valList = []

    sortStr = ''

    for key, value in kwargs.items():
        if key not in KWARG_TO_SQL:
            continue
        sql_map = KWARG_TO_SQL[key]
        if sql_map["flag"] is not None and sql_map["flag"] in flags:
            flags[sql_map["flag"]] = True
        if didFirst:
            endStr += " AND "
        else:
            didFirst = True
        endStr += sql_map["query"]
        valList.append(value)

    pprint(flags)

    #todo flags
    if flags["author"]:
        print("select author")
        queryStr += " FULL OUTER JOIN author ON book.author_id=author.id "
    if flags["publisher"]:
        print("select publisher")
        queryStr += " FULL OUTER JOIN publisher ON book.publisher_id=publisher.id "
    queryStr += endStr

    sortStr = SORT_TO_SQL[sort] if sort in SORT_TO_SQL else ''

    queryStr += " " + sortStr 

    queryStr += (" LIMIT %d OFFSET %d" % (Constants.PAGE_AMOUNT, Constants.PAGE_AMOUNT * (page - 1)))

    print(queryStr) 

    pprint(valList)

    cur.execute(queryStr, tuple(valList))

    allres = cur.fetchall()
    pprint(allres)

    items = []
    for res in allres:
        author = kwargs['author_obj'] if 'author_obj' in kwargs else getAuthorById(cur, res[13])
        book = Book(res[1], res[11], res[12], author, res[14], res[15], res[18], res[16], res[17])
        store_item = StoreItem(res[0], res[3], ItemType(res[2]), book, res[4], res[5], res[6], res[7], res[8], res[9])
        items.append(store_item)
    return items
    #for res in allres:    

def search(search, query, page, sort):
    conn = connect()
    cur = conn.cursor()

    items = None
    if search == "author_name":
        items = doPagedQuery(cur, page, sort, author_name=query)
    elif search == "book_name":
        items = doPagedQuery(cur, page, sort, book_name=query)
    elif search == "genre":
        items = doPagedQuery(cur, page, sort, genre=query)
    elif search == "publisher_name":
        items = doPagedQuery(cur, page, sort, publisher_name=query)
    else:
        pass

    is_next_page = len(items) == Constants.PAGE_AMOUNT

    cur.close()
    conn.close()
    
    return items, is_next_page

def getBooksByAuthor(author_id, sort, page):
    conn = connect()
    cur = conn.cursor()

    author = getAuthorById(cur, author_id)
    if author is None:
        cur.close()
        conn.close()
        abort(404)

    items = doPagedQuery(cur, page, sort, author_id=author_id, author_obj=author)

    is_next_page = len(items) == Constants.PAGE_AMOUNT

    cur.close()
    conn.close()
    return author, items, is_next_page

def getBooksByPublisher(publisher_id, sort, page):
    conn = connect()
    cur = conn.cursor()

    publisher = getPublisherById(cur, publisher_id)
    if publisher is None:
        cur.close()
        conn.close()
        abort(404)

    items = doPagedQuery(cur, page, sort, publisher_id=publisher_id, publisher_obj=publisher)

    is_next_page = len(items) == Constants.PAGE_AMOUNT

    cur.close()
    conn.close()
    return publisher, items, is_next_page
    
# End Paged Items

def getUserById(_id):
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT id, email, pw_hash, super_user FROM users WHERE id=%s", (_id,))

    res = cur.fetchone()

    cur.close()
    conn.close()

    if res is not None:
        user = User(res[0], res[1], res[2], res[3])
        return user
    return None

def getUserByEmail(email, conn=None):
    conn = connect() if conn is None else conn
    cur = conn.cursor()
    cur.execute("SELECT id, email, pw_hash, super_user FROM users WHERE email=%s", (email,))

    res = cur.fetchone()

    pprint(res)
    #print("length of res: %d" % len(res))
    
    user = None
    if res is not None and len(res) >= 4:
        user = User(res[0], res[1], res[2], res[3])

    cur.close()
    conn.close()

    return user

def addUser(email, password):
    
    password_hash = generate_password_hash(password).decode('utf-8')

    conn = connect()
    cur = conn.cursor()
    cur.execute("INSERT INTO users (email, pw_hash, super_user) VALUES (%s, %s, 'False')",
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

#feature the store item id
def addFeature(cur, id):
    cur.execute("INSERT INTO featured_items (id) VALUES(%s)", (id,))

def pay(payee_id, money, cur):
    cur.execute("UPDATE bank_accounts SET balance=balance + %s WHERE id=%s", (money, payee_id))

#save changes to item
def updateItem(store_item, cur):
    cur.execute("UPDATE store_items SET name=%s, item_type=%s, quantity=%s, price=%s, discount_price=%s, revenue_share_percent=%s, auto_order_threshold=%s, img_file_name=%s WHERE id=%s",
    (store_item.name, store_item.item_type.value, store_item.quantity, store_item.price, store_item.discount_price, store_item.revenue_share_percent, store_item.auto_order_threshold, store_item.image_file_name, store_item.id))

def getUserOrders(user):
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM orders WHERE user_id=%s",
                (user.id,))
    allres = cur.fetchall()
    orders = []
    for res in allres:
        order = Order(res[0], res[1], res[2], res[3], res[4], res[5], res[6], res[7], res[8], res[9], res[10])
        orders.append(order)
    return orders

def getOrderById(order_id):
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM orders where id=%s",
                (order_id,))
    res = cur.fetchone()
    return Order(res[0], res[1], res[2], res[3], res[4], res[5], res[6], res[7], res[8], res[9], res[10])


def addOrder(cart, total_price, total_discount, form, user):

    simple_cart = Cart.simplify(cart)
    tracking_number = makeTrackingNumber()

    conn = connect()
    cur = conn.cursor()

    b_address_id = addAddress(form['b-country'], form['b-city'], form['b-province'], form['b-address'], cur)
    s_address_id = addAddress(form['s-country'], form['s-city'], form['s-province'], form['s-address'], cur)

    # we do not store credit card information (typically you would interface with a payment provider now for that)
    cur.execute("INSERT INTO orders (cart, total_price, total_discount_price, first_name, last_name, tracking, b_address_id, s_address_id, user_id, order_date) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,'now') RETURNING id, order_date", 
                (Json(simple_cart), str(total_price), str(total_discount), str(form['firstname']), str(form['lastname']), str(tracking_number), str(b_address_id), str(s_address_id), str(user.id)))

    res = cur.fetchone()
    order_id = res[0]
    order_date = res[1]
    #order_id = cur.fetchone()[0]

    # now we need to update each items quantity, and pay people accordingly
    for item_id in cart:
        order_item = cart[item_id]
        store_item = order_item['store_item']
        owner_share = int(math.floor(order_item['quantity'] * store_item.discount_price * (1 - store_item.revenue_share_percent)))
        publisher_share = int(math.ceil(order_item['quantity'] * store_item.discount_price * store_item.revenue_share_percent)) #todo pay publisher
        pay(Constants.OWNER_BANKING_ID, owner_share, cur)
        if store_item.item_type == ItemType.BOOK:
            pay(store_item.item.publisher.id, publisher_share, cur)
        store_item.quantity -= order_item['quantity'] #todo I could detect that we need to order more books here
        updateItem(store_item, cur)
        addOrderItemHistory(cur, item_id, order_id, order_item['quantity'], owner_share, publisher_share)
        #pay(publisher_id, cur)

    #order complete, commit
    conn.commit()

    billing_address = Address(b_address_id, form['b-country'], form['b-city'], form['b-province'], form['b-address'])
    shipping_address = Address(s_address_id, form['s-country'], form['s-city'], form['s-province'], form['s-address'])

    order = Order(order_id, total_price, total_discount, simple_cart, form['firstname'], form['lastname'], tracking_number, billing_address, shipping_address, order_date, user.id)

    cur.close()
    conn.close()

    return order

def addOrderItemHistory(cur, store_item_id, order_id, amount, owner_share, publisher_share):
    cur.execute("INSERT INTO store_item_history VALUES (%s, %s, %s, %s, %s)",
                (store_item_id, order_id, amount, owner_share, publisher_share))

# normally we would connect to an api once an order is 'shipped'
# for demonstration purposes just return a random string
def makeTrackingNumber():
    # source: https://stackoverflow.com/questions/2257441/random-string-generation-with-upper-case-letters-and-digits
    # pick TRACKING_NUMBER_LENGTH characters out of the list of uppercase characters and digits and join them together into a string
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=TRACKING_NUMBER_LENGTH))
