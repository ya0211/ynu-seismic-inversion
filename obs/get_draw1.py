from pathlib import Path

from draw_sacpy import draw1


def main():
    root_folder = Path(__file__).resolve().parent
    data_folder = root_folder.parent.joinpath('data')
    sac_t_folder = data_folder.joinpath('SAC-T')
    out_t_folder = root_folder.joinpath('out-T')

    d = draw1(sac_t_folder,
              phases='sP', channel='BHZ',
              gcarc=(60, 65), az=(0, 90))
    d.get_file(out_folder=out_t_folder)


if __name__ == "__main__":
    main()
