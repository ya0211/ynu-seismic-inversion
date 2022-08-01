from pathlib import Path

from draw import draw1


def main():
    root_folder = Path(__file__).resolve().parent
    data_folder = root_folder.parent.joinpath('data')
    sac_t_folder = data_folder.joinpath('SAC-T')
    out_t_folder = root_folder.joinpath('out-T')

    d = draw1(sac_folder=sac_t_folder,
              time=(1025, 1125), channel='BHZ',
              dist=(6500, 7000), az=(0, 90),
              figsize=(10, 13))
    d.get_file(out_file=out_t_folder.joinpath('BHZ-6500_7000-0_90.pdf'))


if __name__ == "__main__":
    main()
