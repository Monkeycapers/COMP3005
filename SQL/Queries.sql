--- A sampling of queriers used in the application. Please see database.py and Admin.py for actual queries

--- add banking account
INSERT INTO bank_accounts (balance) VALUES (%s) RETURNING id

-- add publisher, returning its id
INSERT INTO publisher (name, address_id, banking_account_id) VALUES (%s, %s, %s) RETURNING id

--add book, returning its id
INSERT INTO book (source_key, name, author_id, publisher_id, isbn, page_count, description, genre) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id

-- add store_item, returing its id
INSERT INTO store_items (ref_id, item_type, name, quantity, price, discount_price, revenue_share_percent, auto_order_threshold, img_file_name) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id

-- add author, returning its id
INSERT INTO author (source_key, name) VALUES (%s, %s) RETURNING id

-- get publisher
SELECT * FROM publisher WHERE id=%s

-- get author
SELECT * FROM author WHERE id=%s

-- Select %s rows from featured_items
SELECT * FROM featured_items NATURAL RIGHT JOIN store_items TABLESAMPLE SYSTEM_ROWS(%s)

--get book by isbn
SELECT id FROM book WHERE isbn=%s

--get book's store_item
SELECT id FROM store_items WHERE ref_id=%s

--PAGED QUERIES: These are genereated smartly, so there is no one query. Instead, here are the fragments that are combined to make the full query:

--Add fields in the WHERE part
-- flags are to determine what table to join (ie join author to search by its name)
KWARG_TO_SQL = {
    "author_id": {"flag": None, "query":"book.author_id=%s"},
    "publisher_id": {"flag": None, "query":"book.publisher_id=%s"},
    "author_name": {"flag": "author", "query":"author.name ~ %s"},
    "publisher_name": {"flag": "publisher", "query":"publisher.name ~ %s"},
    "book_name":{"flag": None, "query":"book.name ~ %s"},
    "genre":{"flag": None, "query":"book.genre ~ %s"},
    "isbn": {"flag": None, "query":"book.isbn=%s"}
}

--Determine what to ORDER by
SORT_TO_SQL = {
    "price_low": "ORDER BY store_items.discount_price ASC",
    "price_high": "ORDER BY store_items.discount_price DESC",
    "name_A-Z": "ORDER BY store_items.name ASC",
    "name_Z-A": "ORDER BY store_items.name DESC"
}

--beggining of query string, grab store_item + book
SELECT * FROM store_items FULL OUTER JOIN book ON book.id=store_items.ref_id

--if author flag:
FULL OUTER JOIN author ON book.author_id=author.id

--if publisher flag:
FULL OUTER JOIN publisher ON book.publisher_id=publisher.id

--for pagination, limit to page_size and offset by page_size * (page - 1)
LIMIT %d OFFSET %d

--end paged queries

--Get user
SELECT id, email, pw_hash, super_user FROM users WHERE id=%s

--Get user by email
SELECT id, email, pw_hash, super_user FROM users WHERE email=%s

--Add user, by default non super user
INSERT INTO users (email, pw_hash, super_user) VALUES (%s, %s, 'False')

--add address
INSERT INTO addr (country, city, province, address) VALUES (%s, %s, %s, %s) RETURNING id

-- add store item to be featured
INSERT INTO featured_items (id) VALUES(%s)

--Update a store_item
UPDATE store_items SET name=%s, item_type=%s, quantity=%s, price=%s, discount_price=%s, revenue_share_percent=%s, auto_order_threshold=%s, img_file_name=%s WHERE id=%s

--Get users orders
SELECT * FROM orders WHERE user_id=%s

--Get order by id
SELECT * FROM orders where id=%s

--add order, returning id and order_date (should be current time)
INSERT INTO orders (cart, total_price, total_discount_price, first_name, last_name, tracking, b_address_id, s_address_id, user_id, order_date) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,'now') RETURNING id, order_date

--add store item history
INSERT INTO store_item_history VALUES (%s, %s, %s, %s, %s)