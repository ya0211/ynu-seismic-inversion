from numpy import ndarray, array
from typing import Optional
from datetime import timedelta

from .header import SACHeader


class SACTrace:
    def __init__(self, header: Optional[dict], data: Optional[ndarray] = array([])):
        self.header = SACHeader(header)
        self._data = data
        self.stats = Stats(self.header)

    @property
    def data(self):
        return self._data

    @property
    def id(self):
        return "{0}.{1}.{2}.{3}".format(
            self.header.knetwk,
            self.header.kstnm,
            self.header.khole,
            self.header.kcmpnm)


class Stats:
    def __init__(self, header: SACHeader):
        self.network = header['knetwk']
        self.station = header['kstnm']
        self.location = header['khole']
        self.channel = header['kcmpnm']
        self.delta = header['delta']

        time = header.time
        self.starttime = time + timedelta(seconds=int(header['b']))
        self.endtime = time + timedelta(seconds=int(header['e']))

    def __str__(self):
        _str = "network: ".rjust(16, ' ') + "{}\n".format(self.network)
        _str += "station: ".rjust(16, ' ') + "{}\n".format(self.station)
        _str += "location: ".rjust(16, ' ') + "{}\n".format(self.location)
        _str += "channel: ".rjust(16, ' ') + "{}\n".format(self.channel)
        _str += "starttime: ".rjust(16, ' ') + "{}\n".format(self.starttime)
        _str += "endtime: ".rjust(16, ' ') + "{}\n".format(self.endtime)
        _str += "delta: ".rjust(16, ' ') + "{:08f}\n".format(self.delta)
        return _str
