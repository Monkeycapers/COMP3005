DO $$ DECLARE
    r RECORD;
BEGIN
    -- if the schema you operate on is not "current", you will want to
    -- replace current_schema() in query with 'schematodeletetablesfrom'
    -- *and* update the generate 'DROP...' accordingly.
    FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = current_schema()) LOOP
        EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
    END LOOP;
END $$;

CREATE TABLE users (
    id integer generated by default as identity primary key,
    email varchar(255),
    pw_hash varchar(255),
    super_user boolean DEFAULT False
);

CREATE TABLE addr (
    id integer generated by default as identity primary key,
    country varchar(127),
    province varchar(63),
    city varchar(255),
    address text
);

CREATE TABLE orders (
    id integer generated by default as identity primary key,
    total_price integer,
    total_discount_price integer,
    cart jsonb,
    first_name text,
    last_name text,
    tracking varchar(64),
    b_address_id integer,
    s_address_id integer,
    order_date timestamp,
    user_id integer
);

CREATE TABLE bank_accounts (
    id integer generated by default as identity primary key,
    balance integer default 0
);

CREATE TABLE author (
    id integer generated by default as identity primary key,
    source_key text,
    name text
);

CREATE TABLE publisher (
    id integer generated by default as identity primary key,
    name text,
    address_id integer,
    banking_account_id integer
);

CREATE TABLE book (
    id integer generated by default as identity primary key,
    source_key text,
    name text,
    author_id integer,
    publisher_id integer,
    isbn text,
    page_count integer,
    description text
);

CREATE TABLE store_items (
    id integer generated by default as identity primary key,
    ref_id integer,
    item_type smallint,
    name text,
    quantity int,
    price int,
    discount_price int,
    revenue_share_percent numeric(3, 2),
    auto_order_threshold int,
    img_file_name text default 'default.jpg'
);

CREATE TABLE store_item_history (
    store_item_id integer,
    order_id integer,
    amount integer,
    price integer
);

CREATE TABLE featured_items (
    id integer primary key
);