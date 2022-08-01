from numpy import ndarray, linspace
from typing import Optional


class SACData:
    def __init__(self, index: Optional[ndarray], element: Optional[ndarray]):
        self._data_index = index
        self._data_element = element

    @property
    def b(self):
        return self._data_index[0]

    @property
    def e(self):
        return self._data_index[-1]

    @property
    def size(self):
        return self._data_element.size

    def get(self, start, stop):
        start_element, stop_element = None, None
        start_index, stop_index = None, None
        for i in range(0, self._data_index.size - 1):
            if start_element is None or stop_element is None:
                b = self._data_index[i]
                e = self._data_index[i + 1]
                if b <= start < e:
                    start_index = e
                    start_element = i
                if b <= stop < e:
                    stop_index = e
                    stop_element = i
            else:
                break

        if start_element is None:
            start_index = self.b
            start_element = 0
        if stop_element is None:
            stop_index = self.e
            stop_element = self.size

        self._data_element = self._data_element[start_element:stop_element]
        self._data_index = linspace(start_index, stop_index, self.size)
        return self._data_index, self._data_element
