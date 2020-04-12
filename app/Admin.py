import psycopg2, argparse, random
import Types
import main
#provides various admin tasks

DDL_FILE="../SQL/DDL.sql"

database = main.database

# def addBankingAccount(cur, balance):
#     cur.execute("INSERT INTO bank_accounts VALUES (%s) RETURNING id",
#                 (balance,))
#     res = cur.fetchone()
#     return res[0]

# def addPublisher(cur, name, address_id, banking_account_id):
#     cur.execute("INSERT INTO publisher VALUES (%s, %s, %s) RETURNING id",
#                 (name, address_id, banking_account_id))
#     res = cur.fetchone()
#     return res[0]

# def addBook(cur, name, source_key, author_id, publisher_id, isbn, page_count, description):
#     cur.execute("INSERT INTO book VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id",
#                 (source_key, name, author_id, publisher_id, isbn, page_count, description))
#     res = cur.fetchone()
#     return res[0]

# def addStoreItem(cur, ref_id, item_type, name, quantity, price, discount_price, revenue_share_percent, auto_order_threshold, image_file_name):
#     cur.execute("INSERT INTO store_items VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id",
#     (ref_id, item_type, name, quantity, price, discount_price, revenue_share_percent, auto_order_threshold, image_file_name))
#     res = cur.fetchone()
#     return res[0]

# def addAuthor(cur, source_key, name):
#     cur.execute("INSERT INTO author VALUES (%s, %s) RETURNING id", (source_key,name))
#     res = cur.fetchone()
#     return res[0]

def connect():
    conn = psycopg2.connect("dbname=BookExpress user=postgres password=root host=localhost")
    return conn

def toggle_super(id, cur):
    cur.execute("UPDATE users SET super_user = NOT super_user WHERE id=%s", (id,))

#def drop_tables(cur):
    #cur.execute("")

def create_tables(cur):
    cur.execute(open(DDL_FILE, "r").read())

def insert_fake_author(cur):
    return database.addAuthor(cur, "source_key", "Fake Author")

def insert_fake_address(cur):
    return database.addAddress("Canada", "Ottawa", "Ontario", "10 Parliment Street", cur)

def insert_fake_bankaccount(cur):
    return database.addBankingAccount(cur, 0)

def insert_fake_publisher(cur, address_id, bank_id):
    return database.addPublisher(cur, "Fake Publisher", address_id, bank_id)

# def addAddress(country, city, province, street_name, cur):
#     cur.execute("SELECT id FROM addr WHERE country=%s AND city=%s AND province=%s AND address=%s", (country, city, province, street_name))

#     res = cur.fetchone()
#     address_id = None
#     if res is not None and len(res) >= 1:
#         address_id = int(res[0])
    
#     if address_id is None:
#         #insert address, returning ID
#         cur.execute("INSERT INTO addr (country, city, province, address) VALUES (%s, %s, %s, %s) RETURNING id", (country, city, province, street_name))

#         #get our id
#         res = cur.fetchone()
#         if res is not None and len(res) >= 1:
#             address_id = int(res[0])
#     return address_id

def insert_fake_books(count, cur):
    items = []
    address_id = insert_fake_address(cur)
    banking_id = insert_fake_bankaccount(cur)
    author_id = insert_fake_author(cur)
    publisher_id = insert_fake_publisher(cur, address_id, banking_id)
    for i in range(count):
        #storeItem = makeFakeBook(i,str("fakebook #" + str(i)))
        book_name = "Fake book #" + str((i + 1))
        book_id = database.addBook(cur, book_name, "source_key", author_id, publisher_id, "1111", 250, "some text", "SomeGenre")
        price = random.randrange(1, 10000)
        discount_price = price
        if price > 1:
            discount_price = random.randrange(1, price)
        store_item_id = database.addStoreItem(cur, book_id, Types.ItemType.BOOK.value, book_name, 5, price, discount_price, 0.55, 5, 'default.jpg')
        addFeature(cur, store_item_id)
        items.append(store_item_id) 

#feature the store item id
def addFeature(cur, id):
    cur.execute("INSERT INTO featured_items VALUES(%s)", (id,))

# def makeFakeBooks(count):
#     items = []
#     for i in range(count):
#         storeItem = makeFakeBook(i, str("fakebook #" + str(i)))
#         items.append(storeItem)
#     return items

# def makeFakeBook(_id, name):
#     author = Author(0, None, "fake author")
#     book = Book(_id, None, name, author, None, None, None, 500, "A fake description")
#     bookType = ItemType.BOOK
#     storeItem = StoreItem(_id, name, bookType, 3, book, 5, 500, 400, .5, 5)
#     return storeItem

def mainLoop(cur):
    flag = True
    last_publisher_id = 0
    last_author_id = 0
    while flag:
        print('usage: For ids, use "last" to pick the last used one \n 0: Exit Loop \n 1: Add Book \n 2: Add Author: \n 3: Add Publisher \n 4: Delete Book \n 5: Delete Author \n 6: Delete Publisher')
        s = int(input('\nSelection: '))
        
        if s == 0:
            flag = False
        elif s == 1:
            name = input('\nname: ').strip()
            author_id = input('\nauthor id: ').strip()
            if author_id.startswith('last'): 
                author_id = last_author_id
            publisher_id = input('\npublisher id: ').strip()
            if publisher_id.startswith('last'):
                publisher_id = last_publisher_id
            isbn = input('\nisbn: ').strip()
            page_count = input('\npage count: ').strip()
            description = input('\ndescription: ').strip()
            genre = input('\ngenre: ').strip()
            book_id = database.addBook(cur, name, 'N\/A', author_id, publisher_id, isbn, page_count, description, genre)
            # make a store item for the book
            quantity = input('\nquantity: ').strip()
            price = input ('\n(original) price: ').strip()
            discount_price = input ('\n(discount) price: ').strip()
            revenue_share_percent = input('\nrevenue_share_percent (float): ').strip()
            auto_order_threshold = input('\nauto_order_threshold: ').strip()
            image_file_name = input('\nimage filename (in static/imgs): ').strip()
            featured = input('featured: (y/n)').strip()
            fFlag = featured == 'y'
            store_item_id = database.addStoreItem(cur, book_id, Types.ItemType.BOOK.value, name, quantity, price, discount_price, revenue_share_percent, auto_order_threshold, image_file_name)
            if fFlag:
                addFeature(cur, store_item_id)
            print("\nStore Item ID: %s " % (store_item_id))
        elif s == 2:
            name = input('\nname: ').strip()
            author_id = database.addAuthor(cur, 'N\/A', name)
            last_author_id = author_id
            print("\nAuthor ID: %s" % (author_id))
        elif s == 3:
            name = input('\nname: ').strip()
            country = input('\ncountry: ').strip()
            city = input('\ncity: ').strip()
            province = input('\nprovince: ').strip()
            street_name = input('\nstreet name: ').strip()
            address_id = database.addAddress(country, city, province, street_name, cur)
            print("Address ID: %s" % (address_id))
            banking_account_id = database.addBankingAccount(cur, 0)
            print("Banking Account #: %s" % (banking_account_id))
            publisher_id = database.addPublisher(cur, name, address_id, banking_account_id)
            last_publisher_id = publisher_id
            print("Publisher ID: %s" % (publisher_id))
        elif s == 4:
            book_id = input('\nbook id: ')
            cur.execute("DELETE FROM book WHERE id=%s",
                        (book_id,))
            cur.execute("DELETE FROM store_items WHERE ref_id=%s",
                        (book_id,))
        elif s == 5:
            author_id = input('\nauthor id: ')
            cur.execute("DELETE FROM author WHERE id=%s",
                        (author_id,))
            #do cascade here...
        elif s == 6:
            publisher_id = input('\npublisher id: ')
            cur.execute("DELETE FROM publisher WHERE id=%s",
                        (publisher_id,))
            #again do cascade
        else:
            print("Invalid input!")


def main2():
    parser = argparse.ArgumentParser(description="Provides admin tasks for the DB")
    parser.add_argument('-super', type=int, help="Toggle a users super_user status")
    parser.add_argument('-hardreset', action='store_true', help="drop all tables and add them again")
    parser.add_argument('-addfake', type=int, help="Add n fake items")

    conn = connect()
    cur = conn.cursor()

    args = parser.parse_args()
    if args.hardreset:
        #drop_tables(cur)
        #conn.commit()
        print("hard reset")
        create_tables(cur)
        owners_banking_id = database.addBankingAccount(cur, 0)
        print("Owners banking id: %s" % (owners_banking_id))
    elif args.super is not None:
        print("super")
        toggle_super(args.super, cur)
    elif args.addfake is not None:
        print("add books")
        insert_fake_books(args.addfake, cur)
    else: #begin the add / delete loop
        mainLoop(cur)

    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    main2()

