import glob
import os
import pathlib
from pathlib import Path

from SacPy import SACShell


def merge(key_merge: list, sac_folder: Path) -> None:
    for key in key_merge:
        _sac = SACShell(sac_folder, show_log=True)
        _sac.r("*.{0}".format(key))
        _sac.cmd("merge")
        _sac.w(key)
        _sac.close()


def read_file(sac_folder: Path) -> list:
    key = ['.'.join(sac_file.split('.')[6:]) for sac_file in sorted(glob.glob(
        "{0}/*.SAC".format(sac_folder)))]
    key_merge = list()
    for item in key:
        if key.count(item) > 1:
            if item not in key_merge and item != '':
                key_merge.append(item)
    return sorted(key_merge)


def rename(sac_folder: Path) -> None:
    for sac_file in sorted(glob.glob("{0}/*.SAC".format(sac_folder))):
        sac_file = pathlib.Path(sac_file)
        new_sac_file = '.'.join(sac_file.name.split('.')[6:])
        if new_sac_file != '':
            new_sac_file = sac_folder.joinpath(new_sac_file)
            os.rename(sac_file, new_sac_file)


def main():
    root_folder = pathlib.Path(__file__).resolve().parent
    data_folder = root_folder.parent.joinpath('data')

    sac_folder = data_folder.joinpath('SAC')

    key_merge = read_file(sac_folder=sac_folder)
    if key_merge != list():
        merge(key_merge=key_merge, sac_folder=sac_folder)

    rename(sac_folder=sac_folder)


if __name__ == "__main__":
    main()
