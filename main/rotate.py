#!/usr/bin/env python3

import os
import glob
import shutil
import pathlib
import argparse
from pathlib import Path
from logging import ERROR

from SacPy import SAC, SACLst
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
    parser.add_argument("-N",
                        dest="new_sac_output",
                        metavar="new SAC output",
                        type=str,
                        default="SAC-N",
                        help="""
                        新"SAC"文件存储目录(相对)，默认值: {0}
                        """.format('%(default)s'))
    parser.add_argument("-b",
                        dest="begin_of_record",
                        metavar="begin",
                        type=float,
                        default=None,
                        help="""
                        数据窗的起始时间，默认值: "三分量的最大的起始时间"
                        """)
    parser.add_argument("-e",
                        dest="end_of_record",
                        metavar="end",
                        type=float,
                        default=None,
                        help="""
                        数据窗的结束时间，默认值: "三分量的最小的结束时间"
                        """)
    return parser


def rotate(sac_folder: Path, new_sac_folder: Path,
           keys: list, begin_of_record, end_of_record) -> None:
    if not os.path.exists(new_sac_folder):
        os.makedirs(new_sac_folder)

    for key in keys:
        bhz = key + ".BHZ.M.SAC"
        bhz = sac_folder.joinpath(bhz)

        bhn = key + ".BHN.M.SAC"
        bhn = sac_folder.joinpath(bhn)

        bhe = key + ".BHE.M.SAC"
        bhe = sac_folder.joinpath(bhe)

        if not os.path.exists(bhz):
            _logging.log(level=ERROR, msg="{0}: Vertical component missing".format(key))
            continue

        if not os.path.exists(bhe) or not os.path.exists(bhn):
            _logging.log(level=ERROR, msg="{0}: Horizontal component missing".format(key))
            continue

        lst = SACLst(sac_file=bhz)
        lst.args('b', 'e', 'delta')
        z_begin, z_end, z_delta = lst.header_dict.values()

        lst = SACLst(sac_file=bhe)
        lst.args('b', 'e', 'delta')
        e_begin, e_end, e_delta = lst.header_dict.values()

        lst = SACLst(sac_file=bhn)
        lst.args('b', 'e', 'delta')
        n_begin, n_end, n_delta = lst.header_dict.values()

        if not (float(z_delta) == float(e_delta) and float(z_delta) == float(n_delta)):
            print("{0}: delta not equal!".format(key))
            continue

        if begin_of_record is None:
            begin = max(float(z_begin), float(e_begin), float(n_begin))
        else:
            begin = begin_of_record

        if end_of_record is None:
            end = min(float(z_end), float(e_end), float(n_end))
        else:
            end = end_of_record

        _sac = SAC(cwd_folder=sac_folder, show_log=True)
        _sac.cmd("cut {0} {1}".format(begin, end))
        _sac.r(bhn.name, bhe.name)
        _sac.cmd("rotate to gcp")

        bhn, bhe = bhn.name + '.dis', bhe.name + '.dis'
        _sac.w(bhn, bhe)

        _sac.r(bhz.name)
        bhz = bhz.name + '.dis'
        _sac.w(bhz)

        _sac.close()

    for sac_file in sorted(glob.glob("{0}/*.dis".format(sac_folder))):
        sac_file = pathlib.Path(sac_file)
        new_sac_file = new_sac_folder.joinpath(sac_file.name.replace('.dis', ''))
        shutil.move(sac_file, new_sac_file)


def read_file(sac_folder: Path) -> list:
    keys = list()
    for sac_file in sorted(glob.glob("{0}/*.SAC".format(sac_folder))):
        key = '.'.join(pathlib.Path(sac_file).name.split('.')[:3])
        if key not in keys:
            keys.append(key)
    return sorted(keys)


def main_shell():
    parser = parse_parameters()
    args = parser.parse_args()

    sac_folder = args.sac_folder
    sac_folder = root_folder.joinpath(*sac_folder.split("/"))
    new_sac_output = args.new_sac_output
    new_sac_folder = sac_folder.parent.joinpath(new_sac_output)

    begin_of_record = args.begin_of_record
    end_of_record = args.end_of_record

    keys = read_file(sac_folder=sac_folder)

    rotate(sac_folder=sac_folder,
           new_sac_folder=new_sac_folder,
           keys=keys,
           begin_of_record=begin_of_record,
           end_of_record=end_of_record)


def main_ide():
    data_folder = root_folder.parent.joinpath('data')

    sac_folder = data_folder.joinpath('SAC')
    new_sac_folder = data_folder.joinpath('SAC-N')

    begin_of_record = None
    end_of_record = None

    keys = read_file(sac_folder=sac_folder)
    rotate(sac_folder=sac_folder,
           new_sac_folder=new_sac_folder,
           keys=keys,
           begin_of_record=begin_of_record,
           end_of_record=end_of_record)


if __name__ == "__main__":
    main_ide()
