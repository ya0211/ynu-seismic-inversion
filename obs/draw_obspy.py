import numpy as np
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from obspy import read, Stream, Trace
from pathlib import Path
from typing import Optional, Union
from glob import glob

from data import InfoList, SACData


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
                 sac_folder: Optional[Path], *,
                 phases: Optional[str] = 'P',
                 channel: Optional[str] = 'BHZ',
                 gcarc: Optional[tuple] = (90, 180),
                 az: Optional[tuple] = (0, 30),
                 figsize: Optional[tuple] = (10, 13)):

        if sac_folder.exists():
            self._sac_folder = sac_folder
        else:
            raise NotADirectoryError(sac_folder.as_posix())

        self._phases = phases
        self._channel = channel
        self._gcarc_b, self._gcarc_e = gcarc
        self._az_b, self._az_e = az

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
            gcarc, az, b, e = self._get_sac(sac, 'gcarc', 'az', 'b', 'e')
            phases = self._get_phases_travel(sac)

            if self._gcarc_b <= gcarc <= self._gcarc_e and self._az_b <= az <= self._az_e:
                self._info_list.update(tr.id, tr.data, gcarc, az, [b, e, phases])
        self._info_list.sort()

    @staticmethod
    def _get_sac(sac, *args):
        result = []
        for arg in args:
            result.append(sac.get(arg))
        return result

    @staticmethod
    def _get_phases_travel(sac):
        t_list = ['t0', 't1', 't2', 't3', 't4', 't5', 't6', 't7', 't8', 't9']
        kt_list = ['kt0', 'kt1', 'kt2', 'kt3', 'kt4', 'kt5', 'kt6', 'kt7', 'kt8', 'kt9']
        result = {}
        for t in t_list:
            if t in sac:
                tn = sac.get(t)
                kt = kt_list[t_list.index(t)]
                ktn = sac.get(kt)
                result[ktn] = tn
        return result

    @property
    def get_info_list(self):
        if self._info_list.size == 0:
            self._get_info_list()
        return self._info_list

    def get_ax(self):
        self._get_info_list()
        b, e, phases = self._info_list.sac[0]
        time = phases.get(self._phases)

        self.ax.axvline(time + 0.5, color='red', ymin=0.02, ymax=0.98)

        sd = SACData(phases_standard={'phases': self._phases, 'time': time})
        for item in self._info_list.reshape:
            file, data, gcarc, az, [b, e, phases] = item
            sd.phases_travel = phases

            data = data / 1000 + gcarc * 10
            sd.update(np.linspace(b, e, data.size), data)
            sd.set_align()

            if (data.max() - data.min()) < 20:
                self.ax.plot(sd.time, sd.data, color='black')
                self.ax_f.text(1, gcarc * 10, file, fontsize=10)

        self.ax.set_xlim(time - 40, time + 40)
        yticks_label = [i / 10 for i in self.ax.get_yticks()]
        self.ax.set_yticks(self.ax.get_yticks(), yticks_label)

        xticks_label = [int(i - time) for i in self.ax.get_xticks()]
        self.ax.set_xticks(self.ax.get_xticks(), xticks_label)

        self.ax.tick_params(labelsize=12)

        title = r'$ {0},\ gcarc = {0} \sim {1}^o,\ az = {2} \sim {3}^o $'.format(
            self._channel,
            self._gcarc_b, self._gcarc_e,
            self._az_b, self._az_e
        )
        self.ax.set_title(title, fontsize=16)
        self.ax.set_xlabel('Time(s) [aligned on {0}]'.format(self._phases), fontsize=14)
        self.ax.set_ylabel('Distance(deg)', fontsize=14)

        self.ax_f.set_ylim(*self.ax.get_ylim())
        self.ax_f.set_xlim(0, 10)
        self.ax_f.axis(False)

        return self.ax

    def get_file(self, out_file: Union[str, Path] = None, *, out_folder: Optional[Path] = None):
        self.get_ax()
        if out_file is None:
            out_file = "{0}-gcarc_{1}_{2}-az_{3}_{4}-{5}.pdf".format(
                self._channel,
                self._gcarc_b, self._gcarc_e,
                self._az_b, self._az_e,
                self._phases
            )
        if out_folder is not None:
            out_file = out_folder.joinpath(out_file)

        plt.savefig(fname=out_file.as_posix())
        plt.close()

    def show(self):
        self.get_ax()
        plt.show()


draw3 = _ASTA
draw1 = _ASOfSTA


def get_draw3_file(*args,
                   orientation: Optional[str] = 'RTZ',
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
