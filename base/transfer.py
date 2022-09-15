import glob
import pathlib
from logging import ERROR
from pathlib import Path

from SacPy import SACShell
from SacPy.util.logging import get_logger

root_folder = pathlib.Path(__file__).resolve().parent
_logging = get_logger(name="transfer", log_file=root_folder.joinpath("project.log").as_posix())


def transfer(sac_folder: Path, sac_pzs_folder: Path,
             f: list, remove_trend: bool) -> None:
    for sac_file in sorted(glob.glob("{0}/*.SAC".format(sac_folder))):
        sac_file = pathlib.Path(sac_file)
        net, sta, loc, chn = sac_file.name.split('.')[0:4]
        pzs_file = [pathlib.Path(pz_file).name for pz_file in sorted(glob.glob(
            "{0}/SAC_PZs_{1}_{2}_{3}_{4}_*_*".format(sac_pzs_folder, net, sta, chn, loc)))]
        if len(pzs_file) > 1:
            _logging.log(level=ERROR, msg="PZ file error for {0}".format(sac_file.name))
        else:
            pz_file = sac_pzs_folder.joinpath(pzs_file[0])
            _sac = SACShell(sac_folder, show_log=True)
            _sac.r(sac_file.name)
            if remove_trend is True:
                _sac.cmd("rmean; rtr; taper")
            _sac.cmd("trans from pol s {0} to none freq {1} {2} {3} {4}".format(pz_file, *f))
            _sac.cmd("mul 1.0e9")
            _sac.w_over()
            _sac.close()


def main():
    data_folder = root_folder.parent.joinpath('data')

    sac_folder = data_folder.joinpath('SAC')
    sac_pzs_folder = data_folder.joinpath('SAC_PZs')

    period_longest = 100.
    period_shortest = 0.5

    f = [0.8/period_longest, 1/period_longest, 1/period_shortest, 1.2/period_shortest]

    transfer(sac_folder=sac_folder,
             sac_pzs_folder=sac_pzs_folder,
             f=f,
             remove_trend=True)


if __name__ == "__main__":
    main()
