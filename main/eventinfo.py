#!/usr/bin/env python3

import glob
import json
import pathlib
import argparse
from pathlib import Path
from datetime import datetime

from SacPy import SAC


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
    parser.add_argument("-i",
                        dest="info_file",
                        metavar="info file",
                        type=str,
                        default="data/CMTSOLUTION.json",
                        help="""
                        事件信息，要求JSON格式，默认值: {0}
                        """.format('%(default)s'))
    return parser


def add_event_info(sac_folder: Path, info: dict) -> None:
    time: datetime = info["time"]
    jday = time.strftime("%j")
    msec = int(time.microsecond / 1000)

    evla = info["latitude"]
    evlo = info["longitude"]
    evdp = info["depth"]

    # limit: a group of 50 *.SAC
    for sac_file in split(sac_folder, 50):
        _sac = SAC(cwd_folder=sac_folder, show_log=True)
        _sac.r(*sac_file)
        _sac.cmd("synchronize")
        _sac.cmd("ch o gmt {0} {1} {2} {3} {4} {5}".format(
            time.year, jday, time.hour, time.minute, time.second, msec))
        _sac.cmd("ch allt (0 - &1,o&) iztype IO")
        _sac.cmd("ch evlo {0} evla {1} evdp {2}".format(evlo, evla, evdp))
        _sac.wh()
        _sac.close()


def read_info(info_file: Path) -> dict:
    info = json.load(open(info_file, encoding="utf-8"))
    ymd, hms = info["time"].split(' ')
    year, month, day = ymd.split('-')
    hour, minute, second = hms.split(':')
    second, millisecond = second.split('.')
    microsecond = int(millisecond) * 1000

    info["time"] = datetime(int(year), int(month), int(day),
                            int(hour), int(minute), int(second), microsecond)
    return info


def split(sac_folder: Path, n: int) -> list[list]:
    sac_file = [pathlib.Path(sac_file).name for sac_file in sorted(glob.glob("{0}/*.SAC".format(sac_folder)))]
    sac_file_split = list()
    for i in range(0, len(sac_file), n):
        if i+n in range(0, len(sac_file)):
            sac_file_split.append(sac_file[i:i+n])
        else:
            sac_file_split.append(sac_file[i:])
    return sac_file_split


def main():
    root_folder = pathlib.Path(__file__).resolve().parent
    parser = parse_parameters()
    args = parser.parse_args()

    sac_folder = args.sac_folder
    sac_folder = root_folder.joinpath(*sac_folder.split("/"))

    info_file = args.info_file
    info_file = root_folder.joinpath(*info_file.split("/"))
    info = read_info(info_file=info_file)

    add_event_info(sac_folder=sac_folder,
                   info=info)


if __name__ == "__main__":
    main()
