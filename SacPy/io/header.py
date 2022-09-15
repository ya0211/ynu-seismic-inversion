from datetime import datetime, timedelta
from SacPy.object import dict_


class SACHeader(dict_):
    def __init__(self, header_dict=None):
        super().__init__(header_dict)

    @property
    def time(self):
        date = datetime(int(self.nzyear), 1, 1) + timedelta(int(self.nzjday) - 1)
        time = datetime(int(self.nzyear), date.month, date.day,
                        int(self.nzhour), int(self.nzmin), int(self.nzsec), int(self.nzmsec))
        return time

    @property
    def kt(self):
        t_list = ['t0', 't1', 't2', 't3', 't4', 't5', 't6', 't7', 't8', 't9']
        kt_list = ['kt0', 'kt1', 'kt2', 'kt3', 'kt4', 'kt5', 'kt6', 'kt7', 'kt8', 'kt9']
        values_dict = {}
        for t in t_list:
            if t in self.__dict__:
                tn = self.__dict__[t]
                kt = kt_list[t_list.index(t)]
                ktn = self.__dict__[kt]
                values_dict[ktn] = tn
        return values_dict
