import numpy as np
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from obspy import read, Stream, Trace
from pathlib import Path
from typing import Optional
from glob import glob

from data import SACData


class _ASTA:
    def __init__(self,
                 st: Optional[Stream] = None,
                 phases_travel=True,
                 figsize: Optional[tuple] = (18, 13)):

        self._st = st
        self._phases_travel = phases_travel

        plt.subplots_adjust(hspace=0)
        self.fig, (self.ax0, self.ax1, self.ax2) = plt.subplots(3, 1, figsize=figsize, dpi=100)
        self.fig.subplots_adjust(hspace=0)

        self._tr0, self._tr1, self._tr2 = self._st

    def __call__(self, *args):
        self.__init__(*args)

    def get_ax(self):
        self.ax0 = self._get_ax(ax=self.ax0, tr=self._tr0)
        title = '\n'.join((
            '{0} - {1}'.format(self._tr0.stats.starttime, self._tr0.stats.endtime),
        ))
        self.ax0.set_title(title, fontsize=18)
        self.ax0.set_xticks([])

        self.ax1 = self._get_ax(ax=self.ax1, tr=self._tr1)
        self.ax1.set_xticks([])

        self.ax2 = self._get_ax(ax=self.ax2, tr=self._tr2)
        return self.ax0, self.ax1, self.ax2

    def _get_ax(self, ax: Axes, tr: Trace):
        b, e = tr.stats.sac.b, tr.stats.sac.e
        ax.set_xlim(b, e)

        props = dict(boxstyle='round', facecolor='white', alpha=0.5)
        ax.text(0.02, 0.9, tr.id, transform=ax.transAxes, fontsize=14,
                verticalalignment='top', bbox=props)

        if self._phases_travel:
            ax = self._get_phases_travel(ax=ax, tr=tr)

        ax.plot(np.linspace(b, e, tr.data.size), tr.data, color='black')
        return ax

    def get_file(self, out_file: Optional[Path]):
        self.get_ax()
        plt.savefig(fname=out_file.as_posix())
        plt.close()

    def show(self):
        self.get_ax()
        plt.show()

    @staticmethod
    def _get_phases_travel(ax: Axes, tr: Trace):
        t_list = ['t0', 't1', 't2', 't3', 't4', 't5', 't6', 't7', 't8', 't9']
        kt_list = ['kt0', 'kt1', 'kt2', 'kt3', 'kt4', 'kt5', 'kt6', 'kt7', 'kt8', 'kt9']
        for t in t_list:
            if t in tr.stats.sac:
                tn = tr.stats.sac.get(t)
                kt = kt_list[t_list.index(t)]
                ax.axvline(tn, color='red', ymin=0.02, ymax=0.98)
                ax.text(*(tn + 5, tr.data.min()), tr.stats.sac.get(kt), fontsize=14, color='red')
        return ax


class _ASOfSTA:
    def __init__(self,
                 sac_folder: Optional[Path],
                 time: Optional[tuple],
                 channel: Optional[str] = 'BHZ',
                 dist: Optional[tuple] = (35, 45),
                 az: Optional[tuple] = (0, 30),
                 figsize: Optional[tuple] = (10, 13)):

        if sac_folder.exists():
            self._sac_folder = sac_folder
        else:
            raise NotADirectoryError(sac_folder.as_posix())

        self._time = time
        self._channel = channel
        self._dist_b, self._dist_e = dist
        self._az_b, self._az_e = az

        class InfoList:
            def __init__(self):
                self.file_list = []
                self.data_list = []
                self.dist_list = []
                self.az_list = []
                self.sac_list = []

            def update(self, _file, _data, _dist, _az, _other):
                self.file_list.append(_file)
                self.data_list.append(_data)
                self.dist_list.append(_dist)
                self.az_list.append(_az)
                self.sac_list.append(_other)

            def get(self, i):
                return [self.file_list[i],
                        self.data_list[i],
                        self.dist_list[i],
                        self.az_list[i],
                        self.sac_list[i]]

        self._info_list = InfoList()

        self.fig = plt.figure(figsize=figsize, dpi=100)
        self.fig.subplots_adjust(wspace=0)
        gs = self.fig.add_gridspec(20, 20)
        self.ax = self.fig.add_subplot(gs[0:20, 0:18])
        self.ax_f = self.fig.add_subplot(gs[0:20, 18:20])

    def __call__(self, *args):
        self.__init__(*args)

    def _get_info_list(self):
        for sac_file in sorted(glob("{0}/*.{1}.M.SAC".format(self._sac_folder, self._channel))):
            sac_file = Path(sac_file)

            st: Stream = read(sac_file)
            tr = st[0]
            sac = tr.stats.sac
            dist = sac.get('dist')
            az = sac.get('az')
            b = sac.get('b')
            e = sac.get('e')

            if self._dist_b <= dist <= self._dist_e and self._az_b <= az <= self._az_e:
                self._info_list.update(tr.id, tr.data, dist, az, [b, e])

    @property
    def get_info_list(self):
        if len(self._info_list.file_list) == 0:
            self._get_info_list()
        return self._info_list

    def get_ax(self):
        self._get_info_list()
        for i in range(0, len(self._info_list.data_list)):
            file, data, dist, az, [b, e] = self._info_list.get(i)

            data = data / 100 + dist
            if (data.max() - data.min()) < 200:
                sd = SACData(np.linspace(b, e, data.size), data)
                self.ax.plot(*sd.get(*self._time), color='black')
                self.ax_f.text(1, dist, file, fontsize=10)

        self.ax.set_xlim(*self._time)
        title = r" ".join((
            "$",
            "{},".format(self._channel),
            "dist = {0} \sim {1}km, ".format(self._dist_b, self._dist_e),
            "az = {0} \sim {1}^o".format(self._az_b, self._az_e),
            "$"
        ))
        self.ax.set_title(title, fontsize=18)
        self.ax.set_xlabel(r'$ Time(s) $', fontsize=18)
        self.ax.set_ylabel(r'$ Distance(km) $', fontsize=18)

        self.ax_f.set_ylim(*self.ax.get_ylim())
        self.ax_f.set_xlim(0, 10)
        self.ax_f.axis(False)

        return self.ax

    def get_file(self, out_file: Optional[Path]):
        self.get_ax()
        plt.savefig(fname=out_file.as_posix())
        plt.close()

    def show(self):
        self.get_ax()
        plt.show()


draw3 = _ASTA
draw1 = _ASOfSTA


def get_draw3_file(*args,
                   orientation: Optional[str] = 'ENZ',
                   sac_folder: Path,
                   out_folder: Path,
                   suffix: Optional[str] = None):
    key_list = [i for i in args]
    for key in key_list:
        print(key)
        file_list = [key] * 3
        for i in range(0, 3):
            file_list[i] = file_list[i].replace('*', 'BH' + orientation[i])
        st: Stream = read(sac_folder.joinpath(file_list[0]))
        for file in file_list[1:]:
            st += read(sac_folder.joinpath(file))
        if suffix is None:
            out_file = "{0}.pdf".format(key.replace('.*.M.SAC', '').replace('.', '_'))
        else:
            out_file = "{0}_{1}.pdf".format(key.replace('.*.M.SAC', '').replace('.', '_'), suffix)
        d = draw3(st=st, phases_travel=True)
        d.get_file(out_file=out_folder.joinpath(out_file))

