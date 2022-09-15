import numpy as np
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from pathlib import Path
from typing import Optional, Union
from glob import glob

from SacPy import read, SACTrace
from SacPy.object import dict_, list_
from data import get_t_real_corr, get_t_real_extremum, filter_data_extremum


class _ASTA:
    def __init__(self,
                 tr_list: Optional[list] = None,
                 phases_travel=True,
                 figsize: Optional[tuple] = (18, 13)):

        self._phases_travel = phases_travel

        plt.subplots_adjust(hspace=0)
        self.fig, (self.ax0, self.ax1, self.ax2) = plt.subplots(3, 1, figsize=figsize, dpi=100)
        self.fig.subplots_adjust(hspace=0)

        self._tr0, self._tr1, self._tr2 = tr_list

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

    def _get_ax(self, ax: Axes, tr: SACTrace):
        b, e = tr.header.get('b', 'e')
        ax.set_xlim(b, 750)

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
    def _get_phases_travel(ax: Axes, tr: SACTrace):
        header = tr.header
        for kt in header.kt.keys():
            tn = header.kt.get(kt)
            ax.axvline(tn, color='red', ymin=0.02, ymax=0.98)
            ax.text(*(tn + 5, tr.data.min()), kt, fontsize=14, color='red')

        return ax


class _ASOfSTA:
    def __init__(self,
                 sac_folder: Optional[Path], *,
                 phase: Optional[str] = 'sP',
                 channel: Optional[str] = 'BHZ',
                 refer: Optional[str] = 'AK.SCM..BHZ.M.SAC',
                 gcarc: Optional[tuple] = (90, 180),
                 az: Optional[tuple] = (0, 30),
                 figsize: Optional[tuple] = (10, 13),
                 real: Optional[bool] = True):

        if sac_folder.exists():
            self._sac_folder = sac_folder
        else:
            raise NotADirectoryError(sac_folder.as_posix())

        self._phase = phase
        self._channel = channel
        self._gcarc_b, self._gcarc_e = gcarc
        self._az_b, self._az_e = az
        self._is_real = real
        self._refer = refer

        self._data = list_()

        self.fig = plt.figure(figsize=figsize, dpi=100)
        self.fig.subplots_adjust(wspace=0)
        gs = self.fig.add_gridspec(20, 20)
        self.ax = self.fig.add_subplot(gs[0:20, 0:18])
        self.ax_f = self.fig.add_subplot(gs[0:20, 18:20])

    def read_data(self, sac_file):
        if type(sac_file) is str:
            sac_file = self._sac_folder.joinpath(sac_file)
        tr = read(sac_file)
        header = tr.header

        if self._gcarc_b <= header.gcarc <= self._gcarc_e and self._az_b <= header.az <= self._az_e:
            return dict_(
                {"id": tr.id,
                 "data": tr.data,
                 "gcarc": header.gcarc,
                 "az": header.az,
                 "b": header.b,
                 "e": header.e,
                 "phases": header.kt})
        else:
            return None

    def _get_data(self):
        for sac_file in sorted(glob("{0}/*.{1}.*.SAC".format(self._sac_folder, self._channel))):
            sac_file = Path(sac_file)

            data = self.read_data(sac_file)
            if data is not None:
                self._data.append(data)

        self._data.sort(key=lambda r: r.gcarc)

    def get_data(self):
        if self._data.size == 0:
            self._get_data()
        return self._data

    def _get_ax_theory(self):
        self.get_data()
        phases = self._data.first.phases
        t_refer = phases.get(self._phase)
        self.ax.axvline(t_refer, color='red', ymin=0.02, ymax=0.98)

        for item in self._data:
            b, e, t = item.b, item.e, item.phases.get(self._phase)
            data = item.data / 1000 + item.gcarc * 10
            time = np.linspace(b, e, data.size) - (t - t_refer)

            if (data.max() - data.min()) < 20:
                self.ax.plot(time, data, color='black')
                self.ax_f.text(1, item.gcarc * 10, item.id, fontsize=10)

        self._get_legend(t_refer)

    def _get_ax_real(self):
        self.get_data()
        data_refer = self.read_data(self._refer)
        t_refer = get_t_real_extremum(data_refer, self._phase)
        self.ax.axvline(t_refer, color='red', ymin=0.02, ymax=0.98)

        for item in self._data:
            b, e = item.b, item.e
            t = get_t_real_corr(data_refer, item, self._phase)

            data = item.data / 1000 + item.gcarc * 10
            time = np.linspace(b, e, data.size) - (t - t_refer)

            if filter_data_extremum(item, self._phase, 5):
                self.ax.plot(time, data, color='black')
                self.ax_f.text(1, item.gcarc * 10, item.id, fontsize=10)

        self._get_legend(t_refer)

    def _get_legend(self, time):
        self.ax.set_xlim(time - 100, time + 50)
        yticks_label = [i / 10 for i in self.ax.get_yticks()]
        self.ax.set_yticks(self.ax.get_yticks(), yticks_label)

        xticks_label = [int(i - time) for i in self.ax.get_xticks()]
        self.ax.set_xticks(self.ax.get_xticks(), xticks_label)

        self.ax.tick_params(labelsize=12)

        title = r'$ {0},\ gcarc = {1} \sim {2}^o,\ az = {3} \sim {4}^o $'.format(
            self._channel,
            self._gcarc_b, self._gcarc_e,
            self._az_b, self._az_e
        )
        self.ax.set_title(title, fontsize=16)
        self.ax.set_xlabel('Time(s) [aligned on {0}]'.format(self._phase), fontsize=14)
        self.ax.set_ylabel('Distance(deg)', fontsize=14)

        self.ax_f.set_ylim(*self.ax.get_ylim())
        self.ax_f.set_xlim(0, 10)
        self.ax_f.axis(False)

    def get_ax(self):
        if self._is_real:
            self._get_ax_real()
        else:
            self._get_ax_theory()
        return self.ax

    def get_file(self, out_file: Union[str, Path] = None, *, out_folder: Optional[Path] = None):
        self.get_ax()
        if out_file is None:
            out_file = "{0}-gcarc_{1}_{2}-az_{3}_{4}-{5}.pdf".format(
                self._channel,
                self._gcarc_b, self._gcarc_e,
                self._az_b, self._az_e,
                self._phase
            )
        if out_folder is not None:
            out_file = out_folder.joinpath(out_file)

        plt.savefig(fname=out_file.as_posix())
        plt.close()

    def show(self):
        self.get_ax()
        plt.show()

    @staticmethod
    def close():
        plt.close()


draw3 = _ASTA
draw1 = _ASOfSTA


def get_draw3_file(key_list: list,
                   sac_folder: Path,
                   out_folder: Path,
                   target: Optional[str] = None,
                   channel: Optional[str] = 'RTZ'):
    for key in key_list:
        print(key)
        file_list = [key] * 3
        for i in range(0, 3):
            file_list[i] = file_list[i].replace('*', 'BH' + channel[i])

        tr_list = []
        for file in file_list:
            tr = read(sac_folder.joinpath(file))
            tr_list.append(tr)

        if target is None:
            out_file = "{0}.pdf".format(key.replace('.*.M.SAC', '').replace('.', '_'))
        else:
            out_file = "{0}_{1}.pdf".format(key.replace('.*.M.SAC', '').replace('.', '_'), target)

        d = draw3(tr_list=tr_list, phases_travel=True)
        d.get_file(out_file=out_folder.joinpath(out_file))
