from pathlib import Path
from typing import Optional
from numpy import fromfile

from .trace import SACTrace


class SacFileError(Exception):
    pass


def get_sac_header(f, int_type, float_type):
    header_dict = {}
    f.seek(0, 0)
    header_list = ['delta', 'depmin', 'depmax', 'scale', 'odelta', 'b', 'e', 'o', 'a',
                   'fmt', 't', 'f', 'resp', 'stla', 'stlo', 'stel', 'stdp', 'evla',
                   'evlo', 'evel', 'evdp', 'mag', 'user', 'dist', 'az', 'baz', 'gcarc',
                   'internal2', 'internal3', 'depmen', 'cmpaz', 'cmpinc', 'xminimum',
                   'xmaximum', 'yminimum', 'ymaximum', ]
    for header in header_list:
        if header in ['t', 'resp', 'user']:
            value = fromfile(f, float_type, 10)
            for i in range(0, 10):
                h = "{0}{1}".format(header, i)
                v = value[i]
                if v != -12345.0:
                    header_dict[h] = v
        else:
            value = fromfile(f, float_type, 1)[0]
            if value != -12345.0 and not header.startswith('internal'):
                header_dict[header] = value

    f.seek(28, 1)
    header_list = ['nzyear', 'nzjday', 'nzhour', 'nzmin', 'nzsec',
                   'nzmsec', 'nvhdr', 'norid', 'nevid', 'npts', 'internal4',
                   'nwfid', 'nxsize', 'nysize']
    for header in header_list:
        value = fromfile(f, int_type, 1)[0]
        if value != -12345.0 and not header.startswith('internal'):
            header_dict[header] = value

    f.seek(4, 1)
    header_list = ['iftype', 'idep', 'iztype']
    for header in header_list:
        value = fromfile(f, int_type, 1)[0]
        if value != -12345.0:
            header_dict[header] = value

    f.seek(4, 1)
    header_list = ['iinst', 'istreg', 'ievreg', 'ievtyp', 'iqual',
                   'isynth', 'imagtyp', 'imagsrc']
    for header in header_list:
        value = fromfile(f, int_type, 1)[0]
        if value != -12345.0:
            header_dict[header] = value

    f.seek(32, 1)
    header_list = ['leven', 'lpspol', 'lovrok', 'lcalda']
    for header in header_list:
        value = fromfile(f, int_type, 1)[0]
        if value != -12345.0:
            header_dict[header] = value

    f.seek(4, 1)
    header_list = ['kstnm', 'kevnm', 'khole', 'ko', 'ka', 'kt',
                   'kf', 'kuser', 'kcmpnm', 'knetwk', 'kdatrd', 'kinst']
    for header in header_list:
        if header == 'kevnm':
            value = unpack(fromfile(f, 'c', 16), False)
            if value != '-12345':
                header_dict['kevnm'] = value
        elif header == 'kt':
            for i in range(0, 10):
                header = "kt{0}".format(i)
                value = unpack(fromfile(f, 'c', 8))
                if value != '-12345':
                    header_dict[header] = value
        elif header == 'kuser':
            for i in range(0, 3):
                header = "kuser{0}".format(i)
                value = unpack(fromfile(f, 'c', 8))
                if value != '-12345':
                    header_dict[header] = value
        else:
            value = unpack(fromfile(f, 'c', 8))
            if value != '-12345':
                header_dict[header] = value

    return header_dict


def unpack(chararray, strip=True):
    _str = ''
    for c in chararray:
        _str += c.decode('utf-8')
    if strip:
        _str = _str.strip()
    return _str.strip()


def get_sac_waveform(f, float_type):
    f.seek(632, 0)
    data = fromfile(f, float_type)
    return data


def read(file: Optional[Path]) -> SACTrace:
    f = open(file, 'rb')

    f.seek(316, 0)
    npts = fromfile(f, '<i4', 1)[0]
    f.seek(0, 2)
    f_size = f.tell()
    if f_size == 632 + 4 * npts:
        float_type = '<f4'
        int_type = '<i4'
    elif f_size == 632 + 4 * npts.byteswap():
        float_type = '>f4'
        int_type = '>i4'
    else:
        raise SacFileError("Number of points in header and length of trace inconsistent !")

    header = get_sac_header(f, int_type, float_type)
    data = get_sac_waveform(f, float_type)
    trace = SACTrace(header, data)

    f.close()

    return trace
