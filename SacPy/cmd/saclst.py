import pathlib
import subprocess
from typing import Union
from pathlib import Path

from SacPy.io.header import SACHeader


class SACLst:
    def __init__(self, sac_file: Union[str, Path]):
        self._sac_header = SACHeader()
        if type(sac_file) is str:
            sac_file = pathlib.Path(sac_file)

        if sac_file.exists():
            self._sac_file = sac_file
        else:
            raise FileNotFoundError(sac_file.as_posix())

    def get_header(self, *args: str):
        _header_dict = {}
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
            if value == -12345.0:
                value = None
            _header_dict[key] = value
        self._sac_header.header_dict = _header_dict
        values_list = [v for v in _header_dict.values()]
        if len(_header_dict.keys()) <= 1:
            return values_list[0]
        else:
            return values_list

    def get_headers(self) -> SACHeader:
        _header_dict = {}
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
                _header_dict[key] = value
        self._sac_header.header_dict = _header_dict
        return self._sac_header
