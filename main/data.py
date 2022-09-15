from numpy import linspace
from pandas import Series
from scipy.signal import correlate

from SacPy.object import dict_


def get_t_real_extremum(data: dict_, p: str):
    t_p = data.phases.get(p)
    b = t_p
    e = t_p + 10
    data = Series(index=linspace(data.b, data.e, data.data.size), data=data.data)[b:e]
    data_max = data.max()
    data_min = data.min()
    if abs(data_max) > abs(data_min):
        data_target = data_max
    else:
        data_target = data_min

    return data[data.values == data_target].index.min()


def get_t_real_corr(
        data_refer: dict_, data_target: dict_,
        p: str, b=4, e=10):
    b_r = data_refer.phases.get(p) - b
    e_r = data_refer.phases.get(p) + e
    b_t = data_target.phases.get(p) - b
    e_t = data_target.phases.get(p) + e
    time_r = linspace(data_refer.b, data_refer.e, data_refer.data.size)
    time_t = linspace(data_target.b, data_target.e, data_target.data.size)

    data_refer = Series(index=time_r, data=data_refer.data)[b_r:e_r]
    data_target = Series(index=time_t, data=data_target.data)[b_t:e_t]

    if data_refer.size != 0 and data_target.size != 0:
        corr = correlate(data_refer.values, data_target.values, mode="same")
        time = linspace(b_t, e_t, corr.size)

        return time[corr.argmax()]
    else:
        return None


def filter_data_extremum(data_target: dict_, p: str, sill: float):
    b_p = data_target.b
    e_p = data_target.phases.P

    b_r = data_target.phases.get(p)
    e_r = data_target.phases.get(p) + 10

    time_t = linspace(data_target.b, data_target.e, data_target.data.size)
    data_p = Series(index=time_t, data=data_target.data)[b_p:e_p]
    data_r = Series(index=time_t, data=data_target.data)[b_r:e_r]

    s_p = data_p.max() - data_p.min()
    s_r = data_r.max() - data_r.min()

    if (s_r / s_p) >= sill:
        return True
    else:
        return False
