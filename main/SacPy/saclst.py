import pathlib
import subprocess
from typing import Union
from pathlib import Path


class _SACLst:
    def __init__(self, sac_file: Union[str, Path]):
        if type(sac_file) is str:
            self._sac_file = pathlib.Path(sac_file)
        else:
            self._sac_file = sac_file

        self.header_values = {}

    def args(self, *args: str) -> dict:
        if 'all' in args:
            raise ValueError("command `all` is not supported")
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
            self.header_values[key] = value
        return self.header_values

    def b(self) -> float:
        if 'b' not in self.header_values.keys():
            self.args('b')
        return self.header_values['b']

    def e(self) -> float:
        if 'e' not in self.header_values.keys():
            self.args('e')
        return self.header_values['e']

    def delta(self) -> float:
        if 'delta' not in self.header_values.keys():
            self.args('delta')
        return self.header_values['delta']
