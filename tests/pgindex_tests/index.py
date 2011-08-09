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


class ItemIndexSv(IndexBase):
    def get_lang(self):
        return 'sv'

    def get_data(self):
        return self.obj

    def get_vectors(self):
        return (
            Vector(self.obj.title, weight='A'),
            Vector(self.obj.content_sv, weight='B'),
        )


class ItemPublIndex(ItemIndex):
    def get_publish(self):
        return False

class ItemPublStartIndex(ItemIndex):
    def get_start_publish(self):
        return self.obj.start_publish

class ItemPublStopIndex(ItemIndex):
    def get_stop_publish(self):
        return self.obj.stop_publish

