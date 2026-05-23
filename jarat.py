from abc import ABC, abstractmethod
from datetime import date


class Indulas:
    def __init__(self, datum, ferohely):
        self._datum = datum
        self._ferohely = ferohely

    @property
    def datum(self):
        return self._datum

    @property
    def ferohely(self):
        return self._ferohely

    def ferohely_csokkentese(self):
        if self._ferohely <= 0:
            raise ValueError("Nincs szabad férőhely ezen az induláson.")
        self._ferohely -= 1

    def ferohely_novelese(self):
        self._ferohely += 1


class Jarat(ABC):
    def __init__(self, jaratszam, celallomas, jegyar, indulasok):
        self._jaratszam = jaratszam
        self._celallomas = celallomas
        self._jegyar = jegyar
        self._indulasok = indulasok

    @property
    def jaratszam(self):
        return self._jaratszam

    @property
    def celallomas(self):
        return self._celallomas

    @property
    def jegyar(self):
        return self._jegyar

    @property
    def indulasok(self):
        return self._indulasok

    @abstractmethod
    def jarat_tipus(self):
        pass

    def indulas_keresese(self, datum):
        for indulas in self._indulasok:
            if indulas.datum == datum:
                return indulas
        return None

    def __str__(self):
        return f"{self.jarat_tipus()} | {self._jaratszam} | {self._celallomas} | {self._jegyar} Ft"


class BelfoldiJarat(Jarat):
    def jarat_tipus(self):
        return "Belföldi járat"


class NemzetkoziJarat(Jarat):
    def jarat_tipus(self):
        return "Nemzetközi járat"
