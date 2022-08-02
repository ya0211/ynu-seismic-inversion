from numpy import ndarray, linspace
from typing import Optional


class _List(list):
    def __init__(self, _list: Optional[list] = None):
        list.__init__([])
        if _list is None:
            self.extend([])
        else:
            self.extend(_list)

    @property
    def max(self):
        if len(self) == 0:
            return None
        else:
            return max(self)

    @property
    def min(self):
        if len(self) == 0:
            return None
        else:
            return min(self)


class InfoList:
    def __init__(self):
        self.id = []
        self.data = []
        self.gcarc = _List()
        self.az = _List()
        self.sac = []

        self._list = []

    @property
    def size(self):
        return len(self.id)

    def update(self, _id, _data, _dist, _az, _sac):
        self.id.append(_id)
        self.data.append(_data)
        self.gcarc.append(_dist)
        self.az.append(_az)
        self.sac.append(_sac)

    def get(self, index):
        return [self.id[index],
                self.data[index],
                self.gcarc[index],
                self.az[index],
                self.sac[index]]

    @property
    def reshape(self):
        if len(self._list) == 0:
            for index in range(0, self.size):
                self._list.append(self.get(index))
        return self._list

    def sort(self):
        result = sorted(self.reshape, key=lambda r: r[2])
        self.__init__()
        for item in result:
            self.update(*item)
        return result


class SACData:
    def __init__(self, phases_standard: Optional[dict],
                 index: Optional[ndarray] = None,
                 element: Optional[ndarray] = None, ):
        self._data_index = index
        self._data_element = element

        self._phases_standard = phases_standard
        self._phases = None

    @property
    def time(self):
        return self._data_index

    @property
    def data(self):
        return self._data_element

    @property
    def phases_travel(self):
        return self._phases

    @phases_travel.setter
    def phases_travel(self, phases: Optional[dict]):
        self._phases = phases

    @property
    def b(self):
        return self._data_index[0]

    @property
    def e(self):
        return self._data_index[-1]

    @property
    def size(self):
        return self._data_element.size

    def update(self, _index, _element):
        self._data_index = _index
        self._data_element = _element

    def set_align(self):
        if self._phases is None:
            raise ValueError("phases_travel is None")

        phases = self._phases_standard.get('phases')
        time = self._phases_standard.get('time')
        t = self._phases.get(phases)

        self._data_index -= t - time
