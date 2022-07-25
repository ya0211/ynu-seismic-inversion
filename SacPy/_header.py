class SACHeader:
    def __init__(self):
        # Self
        self._header_dict = {}

        # Time-series Values
        self.b, self.e, self.o, self.a, self.F, self.ko, self.ka, self.kf = [None] * 8
        self.npts, self.delta, self.depmin, self.depmax, self.depmen, self.scale, self.nvhdr = [None] * 7

        # Station and Event Values
        self.kstnm, self.stlo, self.stla, self.stel, self.stdp = [None] * 5
        self.kevnm, self.evlo, self.evla, self.evel, self.evdp = [None] * 5
        self.dist, self.az, self.baz, self.gcarc, self.khole = [None] * 5
        self.kcmpnm, self.knetwk, self.kdatrd, self.kinst, self.cmpaz, self.cmpinc = [None] * 6
        self.iftype, self.idep, self.iztype, self.iinst, self.istreg, self.ievreg = [None] * 6
        self.ievtyp, self.iqual, self.isynth = [None] * 3

        # Timing Values
        self.kzdate, self.kztime, self.odelta = [None] * 3
        self.nzyear, self.nzjday, self.nzmonth, self.nzday = [None] * 4
        self.nzhour, self.nzmin, self.nzsec, self.nzmsec = [None] * 4

        # Picks, Response, and User Values
        self.t0, self.t1, self.t2, self.t3, self.t4, self.t5, self.t6, self.t7, self.t8, self.t9 = [None] * 10
        self.kt0, self.kt1, self.kt2, self.kt3, self.kt4, self.kt5 = [None] * 6
        self.kt6, self.kt7, self.kt8, self.kt9 = [None] * 4
        self.resp0, self.resp1, self.resp2, self.resp3, self.resp4, self.resp5 = [None] * 6
        self.resp6, self.resp7, self.resp8, self.resp9 = [None] * 4
        self.user0, self.user1, self.user2, self.user3, self.user4, self.user5 = [None] * 6
        self.user6, self.user7, self.user8, self.user9 = [None] * 4
        self.kuser0, self.kuser1, self.kuser2 = [None] * 3

    def __str__(self):
        return str(self._header_dict.keys()).replace('dict', 'header')

    @property
    def header_dict(self):
        return self._header_dict

    @header_dict.setter
    def header_dict(self, header_dict):
        self._header_dict = header_dict
        for key in self._header_dict.keys():
            setattr(self, key, self._header_dict.get(key))
