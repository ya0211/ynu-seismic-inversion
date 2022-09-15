import os
import glob
import shutil
import pathlib
from pathlib import Path
from logging import ERROR

from SacPy import SACShell, SACLst
from SacPy.util.logging import get_logger

root_folder = pathlib.Path(__file__).resolve().parent
_logging = get_logger(name="rotate", log_file=root_folder.joinpath("project.log").as_posix())


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

        lst = SACLst(sac_file=bhe)
        e_cmpaz = lst.get_header('cmpaz')

        lst = SACLst(sac_file=bhn)
        n_cmpaz = lst.get_header('cmpaz')

        cmpaz_delta = abs(e_cmpaz - n_cmpaz)
        if not (abs(cmpaz_delta - 90) <= 0.01 or abs(cmpaz_delta - 270) <= 0.01):
            _logging.log(level=ERROR,
                         msg="{0}: cmpaz1={1}, cmpaz2={2} are not orthogonal!".format(key, e_cmpaz, n_cmpaz))
            continue

        lst = SACLst(sac_file=bhz)
        z_begin, z_end, z_delta = lst.get_header('b', 'e', 'delta')

        lst = SACLst(sac_file=bhe)
        e_begin, e_end, e_delta = lst.get_header('b', 'e', 'delta')

        lst = SACLst(sac_file=bhn)
        n_begin, n_end, n_delta = lst.get_header('b', 'e', 'delta')

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

        _sac = SACShell(sac_folder, show_log=True)
        _sac.cmd("cut {0} {1}".format(begin, end))
        _sac.r(bhn.name, bhe.name)
        _sac.cmd("rotate to gcp")
        _sac.cmd("ch file 1 KCMPNM BHR")
        _sac.cmd("ch file 2 KCMPNM BHT")

        r, t = bhn.name.replace('BHN', 'BHR') + '.dis', bhe.name.replace('BHE', 'BHT') + '.dis'
        _sac.w(r, t)

        _sac.r(bhz.name)
        z = bhz.name + '.dis'
        _sac.w(z)

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


def main():
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
    main()
