class JegyFoglalas:
    _kovetkezo_azonosito = 1

    def __init__(self, vezeteknev, keresztnev, jarat, datum, azonosito=None):
        if azonosito is None:
            self._azonosito = JegyFoglalas._kovetkezo_azonosito
            JegyFoglalas._kovetkezo_azonosito += 1
        else:
            self._azonosito = azonosito
            if azonosito >= JegyFoglalas._kovetkezo_azonosito:
                JegyFoglalas._kovetkezo_azonosito = azonosito + 1

        self._vezeteknev = vezeteknev
        self._keresztnev = keresztnev
        self._jarat = jarat
        self._datum = datum

    @property
    def azonosito(self):
        return self._azonosito

    @property
    def vezeteknev(self):
        return self._vezeteknev

    @vezeteknev.setter
    def vezeteknev(self, uj_vezeteknev):
        self._vezeteknev = uj_vezeteknev

    @property
    def keresztnev(self):
        return self._keresztnev

    @keresztnev.setter
    def keresztnev(self, uj_keresztnev):
        self._keresztnev = uj_keresztnev

    @property
    def teljes_nev(self):
        return f"{self._vezeteknev} {self._keresztnev}"

    @property
    def jarat(self):
        return self._jarat

    @jarat.setter
    def jarat(self, uj_jarat):
        self._jarat = uj_jarat

    @property
    def datum(self):
        return self._datum

    @datum.setter
    def datum(self, uj_datum):
        self._datum = uj_datum

    def __str__(self):
        return (
            f"Foglalás azonosító: {self._azonosito} | "
            f"Utas: {self.teljes_nev} | "
            f"Járat: {self._jarat.jaratszam} | "
            f"Cél: {self._jarat.celallomas} | "
            f"Dátum: {self._datum} | "
            f"Ár: {self._jarat.jegyar} Ft"
        )
