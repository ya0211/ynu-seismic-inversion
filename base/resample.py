import glob
import pathlib
from pathlib import Path

from SacPy import SACShell, SACLst


def period_default(sac_folder: Path) -> float:
    _period = {}
    for sac_file in sorted(glob.glob("{0}/*.SAC".format(sac_folder))):
        sac_file = pathlib.Path(sac_file)
        lst = SACLst(sac_file=sac_file)
        delta = lst.get_header('delta')
        if delta not in _period:
            _period[delta] = 1
        else:
            _period[delta] += 1
    delta = float(max(_period, key=_period.get))
    return delta


def resample(sac_folder: Path, period_resample):
    if period_resample is None:
        period_resample = period_default(sac_folder)
    for sac_file in sorted(glob.glob("{0}/*.SAC".format(sac_folder))):
        sac_file = pathlib.Path(sac_file)
        lst = SACLst(sac_file=sac_file)
        delta = lst.get_header('delta')
        if delta != period_resample:
            _sac = SACShell(sac_folder, show_log=True)
            _sac.r(sac_file.name)
            if delta < period_resample:
                _sac.cmd("lp c {0}".format(0.5 / period_resample))
            _sac.cmd("interpolate delta {0}".format(period_resample))
            _sac.w_over()
            _sac.close()


def main():
    root_folder = pathlib.Path(__file__).resolve().parent
    data_folder = root_folder.parent.joinpath('data')

    sac_folder = data_folder.joinpath('SAC-N')
    period_resample = None

    resample(sac_folder=sac_folder, period_resample=period_resample)


if __name__ == "__main__":
    main()
