
class _Dict(dict):
    def __init__(self, seq=None, **kwargs):
        if seq is None:
            seq = kwargs
        else:
            seq.update(kwargs)

        super().__init__(seq)

        for key in self.keys():
            self.__setattr__(key, self.get(key))

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __getattr__(self, item):
        if item not in self.__dict__:
            return None
        else:
            return self.__dict__[item]

    def __setitem__(self, key, value):
        dict.__setitem__(self, key, value)
        self.__dict__[key] = value

    @property
    def dict(self):
        return self.copy()

    def get(self, *args):
        values = []
        for key in args:
            values.append(self.dict[key])
        if len(args) == 1:
            return values[0]
        else:
            return values


dict_ = _Dict
