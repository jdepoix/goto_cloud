class DbItemHandler():
    """
    used to keep an handle on created db items, to be able to delete all of them, in case something goes wrong, later on
    in a process and you want to delete all created items
    """
    def __init__(self):
        self.db_items = []

    def add_db_item(self, item):
        """
        Adds an item, which is handled, by this handler. You can also add other DbItemHandlers
        
        :param item: the item to handle
        :type item: DbItemHandler or django.db.models.Model
        :return: the item is returned for chaining
        :rtype: Any
        """
        self.db_items.append(item)
        return item

    def delete(self):
        """
        Deletes all handled items. In case there also are other DbItemHandlers watched. Their items are also deleted
        recursively 
        """
        [db_item.delete() for db_item in self.db_items]
        self.db_items = []
