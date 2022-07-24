import pathlib
import subprocess
from typing import Union
from pathlib import Path

from ._header import SACHeader


class SACLst:
    def __init__(self, sac_file: Union[str, Path]):
        self.header = SACHeader()
        if type(sac_file) is str:
            self._sac_file = pathlib.Path(sac_file)
        else:
            self._sac_file = sac_file
        self.header_dict = {}

    def args(self, *args: str) -> SACHeader:
        keys = args
        _args = " {}"*len(args)
        _args = _args.format(*args)
        cmd = "saclst{0} f {1}".format(_args, self._sac_file).split()
        values = subprocess.check_output(cmd).decode().split()[1:]
        for key in keys:
            _index = keys.index(key)
            value = values[_index]
            try:
                value = float(value)
            except ValueError:
                value = value
            self.header_dict[key] = value
        self.header.parse(self.header_dict)
        return self.header

    def all(self) -> SACHeader:
        cmd = "saclst all f {0}".format(self._sac_file).split()
        values = subprocess.check_output(cmd).decode().strip().split('\n')[1:]
        for item in values:
            _item = item.strip().split('  ')
            key = _item[1]
            value = _item[-1].strip()
            try:
                value = float(value)
            except ValueError:
                value = value
            if value != -12345.0:
                self.header_dict[key] = value
        self.header.parse(self.header_dict)
        return self.header