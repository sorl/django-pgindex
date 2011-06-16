import datetime
from pgindex import IndexBase, Vector


class ItemIndex(IndexBase):
    def get_description(self):
        return self.obj.content

    def get_data(self):
        return self.obj

    def get_vectors(self):
        return (
            Vector(self.obj.title, weight='A'),
            Vector(self.obj.content, weight='B'),
        )

class ItemPublIndex(ItemIndex):
    def get_published(self):
        return False

class ItemExpiresIndex(ItemIndex):
    def get_expires(self):
        return self.obj.expires

