import glob
from pathlib import Path

from draw_sacpy import get_draw3_file


def read_file(sac_folder: Path) -> list:
    keys = list()
    for sac_file in sorted(glob.glob("{0}/*.SAC".format(sac_folder))):
        key = '.'.join(Path(sac_file).name.split('.')[:3])
        key = "{}.*.M.SAC".format(key)
        if key not in keys:
            keys.append(key)
    return sorted(keys)


def main():
    root_folder = Path(__file__).resolve().parent
    data_folder = root_folder.parent.joinpath('data')
    out_folder = root_folder.joinpath('out')
    out_t_folder = root_folder.joinpath('out-T')

    sac_folder = data_folder.joinpath('SAC')
    sac_n_folder = data_folder.joinpath('SAC-N')
    sac_t_folder = data_folder.joinpath('SAC-T')

    key_list = read_file(sac_t_folder)

    get_draw3_file(*key_list, sac_folder=sac_t_folder, out_folder=out_folder, suffix='T', orientation='RTZ')


if __name__ == "__main__":
    main()

