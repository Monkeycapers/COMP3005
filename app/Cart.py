from database import getStoreItemById
import json

def makeOrderItem(store_item, quantity):
    return {
        "id":store_item.id, "name": store_item.name, "quantity": quantity, "image_file_name":store_item.image_file_name
    }

def addItemToCart(items, store_item, quantity=1):
    if store_item.id in items:
        # update
        order_item = items[store_item.id]
        order_item['quantity'] += min(store_item.quantity, quantity)
    else:
        # add new item
        order_item = makeOrderItem(store_item, min(store_item.quantity, quantity))
        # todo handle order_item['quantity'] == 0
        items[store_item.id] = order_item
    return items

def updateCartItem(items, store_item, quantity):
    if store_item.id in items:
        order_item = items[store_item.id]
        order_item['quantity'] = max(0, min(store_item.quantity, quantity))
        if order_item['quantity'] <= 0 or quantity == -1:
            del items[store_item.id]
    return items

def deleteItemFromCart(items, store_item):
    return removeItemFromCart(items, store_item, -1)

def removeItemFromCart(items, store_item, quantity=-1):
    if store_item.id in items:
        # remove <quantity> from order_item, if it is empty remove from cart
        order_item = items[store_item.id]
        if quantity > 0:
            order_item['quantity'] -= quantity
        if order_item['quantity'] <= 0 or quantity == -1:
            del items[store_item.id]
    else:
        #todo handle invalid remove
        pass
    return items

#get real store_item objects for order_items
#auto adjust quantity based on actual quantity from DB
# after adjustment sum up total price
# todo if we do adjust quantity, add a modified flag to the order_item.
def validate(items):
    newItems = {}
    totalPrice = 0
    totalDiscount = 0
    for item_id in items:
        store_item = getStoreItemById(item_id)
        if store_item is not None:
            order_item = items[item_id]
            # todo check if we adjusted quantity
            order_item['quantity'] = min(order_item['quantity'], store_item.quantity)
            if order_item['quantity'] > 0:
                # item is valid, add to newItems
                order_item['store_item'] = store_item
                order_item['total_price'] = store_item.discount_price * order_item['quantity']
                totalPrice += order_item['total_price']
                totalDiscount += (store_item.price - store_item.discount_price) * order_item['quantity']
                newItems[item_id] = order_item
    return {
        "cart":newItems,
        "totalPrice":totalPrice,
        "totalDiscount":totalDiscount
    }

#remove all class objects from items and return as a list of id => quantity
#items must have been run through validate
def simplify(items):
    newItems = {}
    for item_id in items:
        newItems[item_id] = {"id": item_id, "name":items[item_id]['name'], "quantity": items[item_id]['quantity'],
                            "total_price": items[item_id]['total_price'], "image_file_name" : items[item_id]['image_file_name'] }
    return newItems