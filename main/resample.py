#!/usr/bin/env python3

import glob
import pathlib
import argparse
from pathlib import Path

from SacPy import SACShell, SACLst


def parse_parameters():
    parser = argparse.ArgumentParser()
    parser.add_argument("-S",
                        dest="sac_folder",
                        metavar="SAC folder",
                        type=str,
                        default="data/SAC-N",
                        help="""
                        "SAC"文件存储目录(相对)，默认值: {0}
                        """.format('%(default)s'))
    parser.add_argument("-P",
                        dest="period_resample",
                        metavar="period resample",
                        type=float,
                        default=None,
                        help="""
                        采样周期，默认值: 数据中出现次数最多的周期
                        """)
    return parser


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
                _sac.cmd("lp c {}".format(0.5/period_resample))
            _sac.cmd("interpolate delta {}".format(period_resample))
            _sac.w_over()
            _sac.close()


def main_shell():
    root_folder = pathlib.Path(__file__).resolve().parent
    parser = parse_parameters()
    args = parser.parse_args()

    sac_folder = args.sac_folder
    sac_folder = root_folder.joinpath(*sac_folder.split("/"))
    period_resample = args.period_resample

    resample(sac_folder=sac_folder, period_resample=period_resample)


def main_ide():
    root_folder = pathlib.Path(__file__).resolve().parent
    data_folder = root_folder.parent.joinpath('data')

    sac_folder = data_folder.joinpath('SAC-N')
    period_resample = None

    resample(sac_folder=sac_folder, period_resample=period_resample)


if __name__ == "__main__":
    main_ide()
