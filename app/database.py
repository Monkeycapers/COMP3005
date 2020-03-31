from Types import ItemType, Author, Book, StoreItem
DEFAULT_FEATURED_ITEM_COUNT = 5

#because the db isnt ready yet
#returns a list of store items type=book 
def makeFakeBooks(count):
    items = []
    author = Author(0, None, "fake author")
    for i in range(count):
        book = Book(i, None, "fakebook #" + str(i), author, None, None, None, 500, "A fake description")
        bookType = ItemType.BOOK
        storeItem = StoreItem(i, bookType, 3, book, 5, 500, 400, .5, 5)
        items.append(storeItem)
    return items

# Return <count> random store items from the Featured table
def getFeaturedItems(count=DEFAULT_FEATURED_ITEM_COUNT):
    return makeFakeBooks(count)

def getStoreItemById(id):
    return makeFakeBooks(1)[0]