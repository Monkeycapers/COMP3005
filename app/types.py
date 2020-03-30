from enum import Enum

class ItemType(Enum):
    BOOK: 1

class Author:
    def __init__(self, _id, source_key, name):
        self.id = _id
        self.source_key = source_key
        self.name = name

class Book:
    def __init__(self, _id, source_key, name, author, publisher, isbn, genre, page_count):
        self.id = _id
        self.source_key = source_key
        self.name = name
        self.author = author
        self.publisher = publisher
        self.isbn = isbn
        self.genre = genre
        self.page_count = page_count
        
class StoreItem:
    def __init__ (self, _id, item_type, item, quantity, price, discount_price, revenue_share_percent, auto_order_threshold):
        self.id = _id
        self.item_type = item_type
        self.item = item
        self.quantity = quantity
        self.price = price
        self.discount_price = discount_price
        self.revenue_share_percent = revenue_share_percent
        self.auto_order_threshold = auto_order_threshold
    
    def __str__(self):
        return "Item type: " + self.item_type + " Item: " + self.item.__str__() + "; quantity: " + self.quantity + " price: " + self.price + " discount: " + self.discount_price

    def __repr__(self):
        return self.__str__()