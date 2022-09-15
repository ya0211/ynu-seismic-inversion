class _List(list):
    def __init__(self, seq=None):
        super().__init__()
        if seq is not None:
            self.extend(seq)

        self.__list__ = self.copy()

    @property
    def size(self):
        return self.__len__()

    @property
    def first(self):
        if self.size == 0:
            return None
        else:
            return self.__getitem__(0)

    @property
    def last(self):
        if self.size == 0:
            return None
        else:
            return self.__getitem__(-1)

    @property
    def min(self):
        return min(self.__list__)

    @property
    def max(self):
        return max(self.__list__)


list_ = _List
