import numpy as np
import matplotlib.pyplot as plt
from obspy import read, Stream, Trace
from pathlib import Path
from matplotlib.axes import Axes
from typing import Optional


class _Draw:
    def __init__(self, st: Optional[Stream] = None, phases_travel=True, figsize: Optional[tuple] = (18, 13)):
        self._st = st
        self._phases_travel = phases_travel
        plt.subplots_adjust(hspace=0)
        self.fig, (self.ax0, self.ax1, self.ax2) = plt.subplots(3, 1, figsize=figsize, dpi=100)
        self.fig.subplots_adjust(hspace=0)
        self.tr0, self.tr1, self.tr2 = self._st

    def __call__(self, *args):
        self.__init__(*args)

    def draw(self, out_file: Optional[Path] = None):
        self.ax0 = self._draw_ax(ax=self.ax0, tr=self.tr0)
        titlesrc = '\n'.join((
            '{0} - {1}'.format(self.tr0.stats.starttime, self.tr0.stats.endtime),
        ))
        self.ax0.set_title(titlesrc, fontsize=18)
        self.ax0.set_xticks([])

        self.ax1 = self._draw_ax(ax=self.ax1, tr=self.tr1)
        self.ax1.set_xticks([])

        self.ax2 = self._draw_ax(ax=self.ax2, tr=self.tr2)

        if out_file is None:
            plt.show()
        else:
            plt.savefig(fname=out_file.as_posix())
            plt.close()

    @staticmethod
    def _add_phases_travel(ax: Axes, tr: Trace):
        t_list = ['t0', 't1', 't2', 't3', 't4', 't5', 't6', 't7', 't8', 't9']
        kt_list = ['kt0', 'kt1', 'kt2', 'kt3', 'kt4', 'kt5', 'kt6', 'kt7', 'kt8', 'kt9']
        for t in t_list:
            if t in tr.stats.sac:
                tn = tr.stats.sac.get(t)
                kt = kt_list[t_list.index(t)]
                ax.axvline(tn, color='red', ymin=0.02, ymax=0.98)
                ax.text(*(tn + 5, tr.data.min()), tr.stats.sac.get(kt), fontsize=14, color='red')
        return ax

    def _draw_ax(self, ax: Axes, tr: Trace):
        b, e = tr.stats.sac.b, tr.stats.sac.e
        ax.set_xlim(b, e)

        props = dict(boxstyle='round', facecolor='white', alpha=0.5)
        ax.text(0.02, 0.9, tr.id, transform=ax.transAxes, fontsize=14,
                verticalalignment='top', bbox=props)

        if self._phases_travel:
            ax = self._add_phases_travel(ax=ax, tr=tr)

        ax.plot(np.linspace(b, e, tr.data.size), tr.data, color='black')
        return ax


draw = _Draw


def draw_component(*args,
                   orientation: Optional[str] = 'ENZ',
                   sac_folder: Path,
                   out_folder: Path,
                   suffix: Optional[str] = None):

    key_list = [i for i in args]
    for key in key_list:
        print(key)
        file_list = [key] * 3
        for i in range(0, 3):
            file_list[i] = file_list[i].replace('*', 'BH'+orientation[i])
        st: Stream = read(sac_folder.joinpath(file_list[0]))
        for file in file_list[1:]:
            st += read(sac_folder.joinpath(file))
        if suffix is None:
            out_file = "{0}.pdf".format(key.replace('.*.M.SAC', '').replace('.', '_'))
        else:
            out_file = "{0}_{1}.pdf".format(key.replace('.*.M.SAC', '').replace('.', '_'), suffix)
        d = draw(st=st, phases_travel=True)
        d.draw(out_file=out_folder.joinpath(out_file))
