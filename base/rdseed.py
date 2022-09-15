import glob
import os
import pathlib
import shutil
import subprocess
from pathlib import Path


def seed2sac(seed_folder: Path, output_folder: Path,
             sac_output: str, sac_pzs_output: str) -> None:
    sac_folder = output_folder.joinpath(sac_output)
    if not os.path.exists(sac_folder):
        os.makedirs(sac_folder)

    sac_pzs_folder = output_folder.joinpath(sac_pzs_output)
    if not os.path.exists(sac_pzs_folder):
        os.makedirs(sac_pzs_folder)

    for seed_file in sorted(glob.glob("{0}/*.seed".format(seed_folder))):
        seed_file = pathlib.Path(seed_file)
        # print
        print_header(seed_file.name)
        rdseed = subprocess.Popen(["rdseed", "-pdf", seed_file.name],
                                  stdout=subprocess.PIPE,
                                  stdin=subprocess.PIPE,
                                  cwd=seed_folder.as_posix())
        rdseed.stdout.read()
        rdseed.stdout.close()

        for sac_file in sorted(glob.glob("{0}/*.SAC".format(seed_folder))):
            sac_file = pathlib.Path(sac_file)
            new_sac_file = sac_folder.joinpath(sac_file.name)
            shutil.move(sac_file, new_sac_file)

        for sac_pzs_file in sorted(glob.glob("{0}/SAC_PZs_*".format(seed_folder))):
            sac_pzs_file = pathlib.Path(sac_pzs_file)
            new_sac_pzs_file = sac_pzs_folder.joinpath(sac_pzs_file.name)
            shutil.move(sac_pzs_file, new_sac_pzs_file)

        if not os.path.exists(output_folder.joinpath('log')):
            os.mkdir(output_folder.joinpath('log'))
        shutil.move(seed_folder.joinpath("rdseed.err_log"),
                    output_folder.joinpath("log", "rdseed-{0}-err.log".format(seed_file.name.split('.')[2])))


def print_header(string):
    print("\033[01;36m")
    for x in range(0, len(string) + 6):
        print("=", end="")
    print("\n== %s ==" % string)
    for x in range(0, len(string) + 6):
        print("=", end="")
    print("\n\033[0m")


def main():
    root_folder = pathlib.Path(__file__).resolve().parent
    data_folder = root_folder.parent.joinpath('data')

    seed_folder = data_folder
    output_folder = data_folder

    sac_output = 'SAC'
    sac_pzs_output = 'SAC_PZs'

    seed2sac(seed_folder=seed_folder,
             output_folder=output_folder,
             sac_output=sac_output,
             sac_pzs_output=sac_pzs_output)


if __name__ == "__main__":
    main()
