import glob
import pathlib
from pathlib import Path

from SacPy import SACShell


def filter_(sac_folder: Path, frequency: tuple):
    for sac_file in sorted(glob.glob("{0}/*.SAC".format(sac_folder))):
        sac_file = pathlib.Path(sac_file)
        _sac = SACShell(sac_folder, show_log=True)
        _sac.r(sac_file.name)
        _sac.cmd("bp c {0} {1} n 2 p 2".format(*frequency))
        _sac.w_over()
        _sac.close()


def main():
    root_folder = pathlib.Path(__file__).resolve().parent
    data_folder = root_folder.parent.joinpath('data')

    sac_folder = data_folder.joinpath('SAC-N')
    f = (0.02, 0.2)

    filter_(sac_folder=sac_folder, frequency=f)


if __name__ == "__main__":
    main()
