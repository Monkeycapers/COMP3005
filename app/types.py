from enum import Enum
#from main import Bcrypt, check_password_hash, generate_password_hash
#import main
import os
import Constants

class ItemType(Enum):
    BOOK = 1

class Author:
    def __init__(self, _id, source_key, name):
        self.id = _id
        self.source_key = source_key
        self.name = name

class Publisher:
    def __init__(self, _id, name, address_id, banking_id):
        self.id = _id
        self.name = name
        self.address_id = address_id
        self.banking_id = banking_id

class Book:
    def __init__(self, _id, source_key, name, author, publisher, isbn, genre, page_count, description):
        self.id = _id
        self.source_key = source_key
        self.name = name
        self.author = author
        self.publisher = publisher
        self.isbn = isbn
        self.genre = genre
        self.page_count = page_count
        self.description = description
        
class StoreItem:

    def __init__ (self, _id, name, item_type, item, quantity, price, discount_price, revenue_share_percent, auto_order_threshold, image_file_name):
        self.id = _id
        self.name = name
        self.image_file_name = image_file_name
        self.item_type = item_type
        self.item = item
        self.quantity = quantity
        self.price = price
        self.discount_price = discount_price
        self.revenue_share_percent = revenue_share_percent
        self.auto_order_threshold = auto_order_threshold

    def isBook(self):
        return self.item_type == ItemType.BOOK

    def isSale(self):
        return self.price != self.discount_price

    def inStock(self):
        return self.quantity > 0

    def getFormattedCurrency(self, value):
        return "$" + format((value / 100), ',.2f')

    def getFormattedPrice(self):
        return self.getFormattedCurrency(self.price)

    def getFormattedDiscountPrice(self):
        return self.getFormattedCurrency(self.discount_price)

    def getFormattedSaving(self):
        return self.getFormattedCurrency(self.price - self.discount_price)

    def getFullImageFileName(self):
        return os.path.join(Constants.IMAGES_DIRECTORY, self.image_file_name)
    
    def __str__(self):
        return ""
        #return "Name: " + self.name + " Item type: " + str(self.item_type) + " Item: " + self.item.__str__() + "; quantity: " + self.quantity + " price: " + self.price + " discount: " + self.discount_price

    def __repr__(self):
        return self.__str__()

#class OrderItem:
#    
#    def __init__(self, store_item, order_quantity):
#        self.store_item = store_item
#       self.order_quantity = order_quantity

class Address:

    def __init__(self, _id, country, province, city, address):
        self.id = _id
        self.country = country
        self.province = province
        self.city = city
        self.address = address

class Order:
    
    def __init__(self, _id, total_price, total_discount_price, cart_json, first_name, last_name, tracking, b_address, s_address, date, user_id):
        self.id = _id
        self.total_price = int(total_price)
        self.total_discount_price = int(total_discount_price)
        self.cart_json = cart_json
        self.tracking = tracking
        self.first_name = first_name
        self.last_name = last_name
        self.b_address = b_address
        self.s_address = s_address
        self.date = date
        self.user_id = user_id

class User:

    def __init__(self, _id, email, password_hash, super_user):
        self.id = _id
        self.email = email
        self.password_hash = password_hash
        self.super_user = super_user
    
    def get_id(self):
        return str(self.id)

    #return True if hash(password) == password_hash
    #def test_password(self, password):
    #    return main.check_password_hash(self.password_hash, password)

    #flask_login properties
    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    

            
