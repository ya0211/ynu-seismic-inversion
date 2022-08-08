import pathlib
import subprocess
from typing import Union
from pathlib import Path
from logging import INFO

from SacPy.util.logging import get_logger


class SACShell:
    def __init__(self, cwd_folder: Union[str, Path] = None, *, show_log=False):
        self.args = (cwd_folder, show_log)
        self._show_log = show_log
        self._log_dir = pathlib.Path(__name__).resolve().parent
        if cwd_folder is None:
            self.cwd_folder = self._log_dir
        else:
            if type(cwd_folder) is str:
                self.cwd_folder = pathlib.Path(cwd_folder)
            else:
                self.cwd_folder = cwd_folder
        self._sac = subprocess.Popen(["sac"],
                                     stdout=subprocess.PIPE,
                                     stdin=subprocess.PIPE,
                                     stderr=subprocess.PIPE,
                                     cwd=self.cwd_folder.as_posix())
        self.sac_object = self._sac

    def __del__(self):
        if not self._sac.stdin.closed:
            self._sac.stdin.close()
        if not self._sac.stdout.closed:
            self._sac.stdout.close()

    def _logging(self, name: str, level, msg: str):
        if self._show_log:
            _logging = get_logger(name=name, log_file="{0}/sac.log".format(self._log_dir.as_posix()))
            _logging.log(level=level, msg=msg)

    def cmd(self, cmd: str) -> None:
        self._logging(name="SACShell.cmd", level=INFO, msg=cmd)
        self._sac.stdin.write(bytes("{0} \n".format(cmd).encode()))

    def r(self, *args: str) -> None:
        _file = " {}"*len(args)
        _file = _file.format(*args)
        self.cmd("r{0}".format(_file))

    def w(self, *args: str) -> None:
        _file = " {}"*len(args)
        _file = _file.format(*args)
        self.cmd("w{0}".format(_file))

    def w_over(self) -> None:
        self.cmd("w over")

    def wh(self) -> None:
        self.cmd("wh")

    def q(self) -> None:
        self.cmd("q")

    def close(self) -> None:
        self._sac.stdin.close()
        self._sac.stdout.read()
        self._sac.stdout.close()
