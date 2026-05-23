class LegiTarsasag:
    def __init__(self, nev):
        self._nev = nev
        self._jaratok = []

    @property
    def nev(self):
        return self._nev

    @property
    def jaratok(self):
        return self._jaratok

    def jarat_hozzaadasa(self, jarat):
        self._jaratok.append(jarat)

    def jarat_keresese(self, jaratszam):
        for jarat in self._jaratok:
            if jarat.jaratszam == jaratszam:
                return jarat
        return None
