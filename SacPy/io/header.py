from datetime import datetime, timedelta


class SACHeader:
    def __init__(self, header_dict=None):
        if header_dict is None:
            self._header_dict = {}
        else:
            self._set_header_dict(header_dict)

    def __getattr__(self, item):
        if item not in self.__dict__:
            raise KeyError("{0} did not get!".format(item))

    def __str__(self):
        return self._header_dict.__str__()

    def __repr__(self):
        return self.__str__()

    def __getitem__(self, item):
        return self._header_dict[item]

    def __contains__(self, item):
        if item in self._header_dict:
            return True
        else:
            return False

    def __len__(self):
        return len(self._header_dict)

    @property
    def time(self):
        date = datetime(int(self.nzyear), 1, 1) + timedelta(int(self.nzjday) - 1)
        time = datetime(int(self.nzyear), date.month, date.day,
                        int(self.nzhour), int(self.nzmin), int(self.nzsec), int(self.nzmsec))
        return time

    @property
    def header_dict(self):
        return self._header_dict

    @header_dict.setter
    def header_dict(self, header_dict):
        self._set_header_dict(header_dict)

    def _set_header_dict(self, header_dict):
        self._header_dict = header_dict
        for key in header_dict.keys():
            setattr(self, key, header_dict.get(key))

    def get(self, *args):
        values = []
        for key in args:
            values.append(self._header_dict.get(key))
        if len(args) == 1:
            return values[0]
        else:
            return values

    @property
    def kt2t(self):
        t_list = ['t0', 't1', 't2', 't3', 't4', 't5', 't6', 't7', 't8', 't9']
        kt_list = ['kt0', 'kt1', 'kt2', 'kt3', 'kt4', 'kt5', 'kt6', 'kt7', 'kt8', 'kt9']
        values_dict = {}
        for t in t_list:
            if t in self._header_dict:
                tn = self._header_dict.get(t)
                kt = kt_list[t_list.index(t)]
                ktn = self._header_dict.get(kt)
                values_dict[ktn] = tn
        return values_dict
