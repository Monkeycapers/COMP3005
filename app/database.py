from Types import ItemType, Author, Book, StoreItem
DEFAULT_FEATURED_ITEM_COUNT = 5

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