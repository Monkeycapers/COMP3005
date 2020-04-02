from Types import ItemType, Author, Book, StoreItem, User
from main import Bcrypt, check_password_hash, generate_password_hash
from pprint import pprint
import psycopg2

DEFAULT_FEATURED_ITEM_COUNT = 5

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
    return getUserByEmail(email, conn)
    
