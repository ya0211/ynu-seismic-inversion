#!/usr/bin/env python3

import glob
import pathlib
import argparse
from pathlib import Path
from logging import ERROR

from SacPy import SAC
from SacPy.logging import get_logger

root_folder = pathlib.Path(__file__).resolve().parent
_logging = get_logger(name="transfer", log_file=root_folder.joinpath("project.log").as_posix())


def parse_parameters():
    parser = argparse.ArgumentParser()
    parser.add_argument("-S",
                        dest="sac_folder",
                        metavar="SAC folder",
                        type=str,
                        default="data/SAC",
                        help="""
                        "SAC"文件存储目录(相对)，默认值: {0}
                        """.format('%(default)s'))
    parser.add_argument("-P",
                        dest="sac_pzs_folder",
                        metavar="SAC_PZs folder",
                        type=str,
                        default="data/SAC_PZs",
                        help="""
                        "SAC_PZs"文件存储目录(相对)，默认值: {0}
                        """.format('%(default)s'))
    parser.add_argument("-TS",
                        dest="period_shortest",
                        metavar="period shortest",
                        type=float,
                        default=0.5,
                        help="""
                        最短周期，默认值: {0}
                        """.format('%(default)s'))
    parser.add_argument("-TL",
                        dest="period_longest",
                        metavar="period longest",
                        type=float,
                        default=100.,
                        help="""
                        最长周期，默认值: {0}
                        """.format('%(default)s'))
    parser.add_argument("-r",
                        "--remove-trend",
                        action='store_true',
                        help="""
                        去均值、去线性趋势和波形尖灭
                        """)
    return parser


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
            _sac = SAC(cwd_folder=sac_folder, show_log=True)
            _sac.r(sac_file.name)
            if remove_trend is True:
                _sac.cmd("rmean; rtr; taper")
            _sac.cmd("trans from pol s {0} to none freq {1} {2} {3} {4}".format(pz_file, *f))
            _sac.cmd("mul 1.0e9")
            _sac.w_over()
            _sac.close()


def main():
    parser = parse_parameters()
    args = parser.parse_args()

    sac_folder = args.sac_folder
    sac_folder = root_folder.joinpath(*sac_folder.split("/"))
    sac_pzs_folder = args.sac_pzs_folder
    sac_pzs_folder = root_folder.joinpath(*sac_pzs_folder.split("/"))

    f = [0.8/args.period_longest, 1/args.period_longest, 1/args.period_shortest, 1.2/args.period_shortest]
    remove_trend = args.remove_trend

    transfer(sac_folder=sac_folder,
             sac_pzs_folder=sac_pzs_folder,
             f=f,
             remove_trend=remove_trend)


if __name__ == "__main__":
    main()
