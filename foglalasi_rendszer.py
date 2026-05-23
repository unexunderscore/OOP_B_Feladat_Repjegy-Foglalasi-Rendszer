from datetime import datetime, date
import json
import os
import time

from jarat import BelfoldiJarat, NemzetkoziJarat, Indulas
from legitarsasag import LegiTarsasag
from jegyfoglalas import JegyFoglalas


class FoglalasiRendszer:
    def __init__(self):
        self._fajl_nev = "foglalasok.json"
        self._legitarsasag = LegiTarsasag("SkyTravel Airlines")
        self._foglalasok = []
        self._jaratok_betoltese()
        self._maverick_mod = False

        if not self._foglalasok_betoltese():
            self._alap_foglalasok_betoltese()
            self._foglalasok_mentese()

    def kepernyo_torles(self):
        os.system("cls" if os.name == "nt" else "clear")

    def idozitett_varakozas(self, masodperc=2, uzenet=True):
        if uzenet:
            print("\nVisszalépés folyamatban...")

        time.sleep(masodperc)

    def visszalepes_e(self, ertek):
        return ertek.strip().lower() in ["0", "back", "vissza"]

    def _jaratok_betoltese(self):
        self._legitarsasag.jarat_hozzaadasa(
            BelfoldiJarat("B101", "Budapest", 18000, [
                Indulas(date(2026, 6, 12), 10),
                Indulas(date(2026, 7, 5), 10),
                Indulas(date(2026, 8, 15), 10)
            ])
        )
        self._legitarsasag.jarat_hozzaadasa(
            BelfoldiJarat("B202", "Debrecen", 15000, [
                Indulas(date(2026, 6, 15), 10),
                Indulas(date(2026, 8, 10), 10),
                Indulas(date(2026, 9, 12), 10)
            ])
        )
        self._legitarsasag.jarat_hozzaadasa(
            NemzetkoziJarat("N303", "London", 65000, [
                Indulas(date(2026, 7, 1), 10),
                Indulas(date(2026, 9, 20), 10),
                Indulas(date(2026, 12, 5), 10)
            ])
        )
        # self._legitarsasag.jarat_hozzaadasa(
        #  NemzetkoziJarat("TG1986", "Danger Zone", 99000, [
        #      Indulas(date(2026, 6, 27), 2)
        #  ])
        # )

    def _foglalas_hozzaadasa(self, vezeteknev, keresztnev, jarat, datum, azonosito=None):
        indulas = jarat.indulas_keresese(datum)
        if indulas is None:
            raise ValueError("Erre a dátumra nincs ilyen járat.")
        indulas.ferohely_csokkentese()
        foglalas = JegyFoglalas(vezeteknev, keresztnev, jarat, datum, azonosito)
        self._foglalasok.append(foglalas)
        return foglalas

    def _alap_foglalasok_betoltese(self):
        adatok = [
            ("Kiss", "Anna", "B101", date(2026, 6, 12)),
            ("Nagy", "Béla", "B202", date(2026, 6, 15)),
            ("Tóth", "Eszter", "N303", date(2026, 7, 1)),
            ("Szabó", "Péter", "B101", date(2026, 7, 5)),
            ("Varga", "Lilla", "B202", date(2026, 8, 10)),
            ("Horváth", "Máté", "N303", date(2026, 9, 20)),
        ]
        for vezeteknev, keresztnev, jaratszam, datum in adatok:
            jarat = self._legitarsasag.jarat_keresese(jaratszam)
            self._foglalas_hozzaadasa(vezeteknev, keresztnev, jarat, datum)

    def _foglalasok_mentese(self):
        adatok = []
        for foglalas in self._foglalasok:
            adatok.append({
                "azonosito": foglalas.azonosito,
                "vezeteknev": foglalas.vezeteknev,
                "keresztnev": foglalas.keresztnev,
                "jaratszam": foglalas.jarat.jaratszam,
                "datum": str(foglalas.datum)
            })
        with open(self._fajl_nev, "w", encoding="utf-8") as fajl:
            json.dump(adatok, fajl, ensure_ascii=False, indent=4)

    def _foglalasok_betoltese(self):
        if not os.path.exists(self._fajl_nev):
            return False

        try:
            with open(self._fajl_nev, "r", encoding="utf-8") as fajl:
                adatok = json.load(fajl)

            if not isinstance(adatok, list):
                print("A JSON fájl szerkezete hibás. Alapadatok kerülnek betöltésre.")
                self.idozitett_varakozas()
                return False

            serult_adat_talalhato = False
            torolt_foglalasok_szama = 0
            hasznalt_azonositok = set()

            for elem in adatok:
                if not isinstance(elem, dict):
                    serult_adat_talalhato = True
                    torolt_foglalasok_szama += 1
                    continue

                azonosito = elem.get("azonosito")
                vezeteknev = elem.get("vezeteknev")
                keresztnev = elem.get("keresztnev")
                jaratszam = elem.get("jaratszam")
                datum_szoveg = elem.get("datum")

                if not vezeteknev or not keresztnev or not jaratszam or not datum_szoveg:
                    serult_adat_talalhato = True
                    torolt_foglalasok_szama += 1
                    continue

                try:
                    vezeteknev = self.ellenoriz_nev_resz(vezeteknev)
                    keresztnev = self.ellenoriz_nev_resz(keresztnev)
                    jarat = self._legitarsasag.jarat_keresese(jaratszam)
                    datum = datetime.strptime(datum_szoveg, "%Y-%m-%d").date()
                except ValueError:
                    serult_adat_talalhato = True
                    torolt_foglalasok_szama += 1
                    continue

                if jarat is None or jarat.indulas_keresese(datum) is None:
                    serult_adat_talalhato = True
                    torolt_foglalasok_szama += 1
                    continue

                if not isinstance(azonosito, int) or azonosito <= 0 or azonosito in hasznalt_azonositok:
                    serult_adat_talalhato = True
                    azonosito = None

                try:
                    foglalas = self._foglalas_hozzaadasa(vezeteknev, keresztnev, jarat, datum, azonosito)
                    hasznalt_azonositok.add(foglalas.azonosito)
                except ValueError:
                    serult_adat_talalhato = True
                    torolt_foglalasok_szama += 1

            if serult_adat_talalhato:
                self._foglalasok_mentese()
                print("\nFigyelem! A foglalasok.json fájl sérült adatokat tartalmazott.")
                print(f"Az értelmezhetetlen foglalások törlésre kerültek. Törölt foglalások száma: {torolt_foglalasok_szama}")
                print("A hibás vagy duplikált azonosítók automatikusan új azonosítót kaptak.")
                self.idozitett_varakozas()

            return True

        except json.JSONDecodeError:
            print("\nA foglalasok.json fájl nem értelmezhető JSON formátumú.")
            print("Alapadatok kerülnek betöltésre.")
            self.idozitett_varakozas()
            return False

    def ellenoriz_nev_resz(self, nev):
        nev = nev.strip()
        if len(nev) < 2:
            raise ValueError("A név túl rövid.")
        if not all(c.isalpha() or c in ["-", " "] for c in nev):
            raise ValueError("A név csak betűket, kötőjelet és szóközt tartalmazhat.")
        return " ".join(szo.capitalize() for szo in nev.split())

    def nev_resz_bekeres(self, tipus):
        while True:
            nev = input(f"Add meg az utas {tipus}: ").strip()
            if self.visszalepes_e(nev):
                return None
            try:
                return self.ellenoriz_nev_resz(nev)
            except ValueError as hiba:
                print(f"Hiba: {hiba}")

    def igen_nem_bekeres(self, kerdes):
        while True:
            valasz = input(kerdes).strip().lower()
            if valasz in ["i", "igen"]:
                return True
            if valasz in ["n", "nem"]:
                return False
            print("Hibás válasz. Kérlek, add meg így: i/igen vagy n/nem.")

    def jaratok_listazasa(self):
        print("\nElérhető járatok és indulások:")
        print("-" * 105)
        print(f"{'Járatszám':<12} {'Típus':<20} {'Célállomás':<15} {'Dátum':<12} {'Ár':<10} {'Szabad hely':<12}")
        print("-" * 105)
        for jarat in self._legitarsasag.jaratok:
            for indulas in jarat.indulasok:
                print(
                    f"{jarat.jaratszam:<12} {jarat.jarat_tipus():<20} {jarat.celallomas:<15} "
                    f"{str(indulas.datum):<12} {jarat.jegyar:<10} {indulas.ferohely:<12}"
                )
        if self._maverick_mod:
            print(
                f"{'F-14D':<12} "
                f"{'Vadászgép':<20} "
                f"{'Danger Zone':<15} "
                f"{'2026-06-27':<12} "
                f"{'TITKOS':<10} "
                f"{'-':<12}"
            )
        print("-" * 105)

    def foglalasok_tablazatban_kiirasa(self, foglalasok):
        if not foglalasok:
            print("Nincs megjeleníthető foglalás.")
            return
        print("-" * 105)
        print(f"{'ID':<5} {'Utas neve':<25} {'Járat':<10} {'Célállomás':<15} {'Dátum':<12} {'Ár':<10}")
        print("-" * 105)
        for foglalas in foglalasok:
            print(
                f"{foglalas.azonosito:<5} {foglalas.teljes_nev:<25} {foglalas.jarat.jaratszam:<10} "
                f"{foglalas.jarat.celallomas:<15} {str(foglalas.datum):<12} {foglalas.jarat.jegyar:<10}"
            )
        print("-" * 105)

    def foglalasok_listazasa(self, varakozzon=True):
        print("\nAktuális foglalások:")
        self.foglalasok_tablazatban_kiirasa(self._foglalasok)

        if varakozzon:
            input("\nNyomj ENTER-t a visszalépéshez...")
    def foglalas_keresese_azonosito_alapjan(self, azonosito):
        for foglalas in self._foglalasok:
            if foglalas.azonosito == azonosito:
                return foglalas
        return None

    def indulas_bekeres(self, jarat):
        print("\nElérhető indulások ehhez a járathoz:")
        elerheto_indulasok = []
        for index, indulas in enumerate(jarat.indulasok, start=1):
            if indulas.ferohely > 0:
                elerheto_indulasok.append(indulas)
                print(f"{len(elerheto_indulasok)}. {indulas.datum} | Szabad hely: {indulas.ferohely}")

        if not elerheto_indulasok:
            print("Erre a járatra nincs szabad hely egyik induláson sem.")
            return None

        while True:
            valasztas = input("Válassz indulást: ").strip()
            if self.visszalepes_e(valasztas):
                return None
            try:
                sorszam = int(valasztas)
                if 1 <= sorszam <= len(elerheto_indulasok):
                    return elerheto_indulasok[sorszam - 1]
                print("Nincs ilyen sorszámú indulás.")
            except ValueError:
                print("Hibás választás.")

    def jarat_bekeres(self):
        while True:
            jaratszam = input(
                "Add meg a járatszámot: "
            ).strip().upper()
            if self.visszalepes_e(jaratszam):
                return None
            if jaratszam == "MAVERICK":
                print("Maverick engedélyt kapott felszállásra. Danger Zone aktiválva.")
            jarat = self._legitarsasag.jarat_keresese(jaratszam)

            if jaratszam == "TARDIS":
                print("Figyelem: A TARDIS jelenleg karbantartás alatt áll. Doctor Who is a SkyTravel Airlines járataival repül ez idő alatt!")
                self.idozitett_varakozas(2, False)
                continue
            if jarat is not None:
                return jarat
            print("Nincs ilyen járat. Kérlek, próbáld újra.")

    def van_azonos_foglalas(self, vezeteknev, keresztnev, jarat, datum):
        teljes_nev = f"{vezeteknev} {keresztnev}".lower()
        for foglalas in self._foglalasok:
            if foglalas.teljes_nev.lower() == teljes_nev and foglalas.jarat.jaratszam == jarat.jaratszam and foglalas.datum == datum:
                return True
        return False

    def jegy_foglalasa(self):
        self.kepernyo_torles()
        self.jaratok_listazasa()
        print("\nVisszalépni a főmenübe a 0-as érték megadásával lehet.")

        vezeteknev = self.nev_resz_bekeres("vezetéknevét")
        if vezeteknev is None:
            print("Foglalás megszakítva.")
            self.idozitett_varakozas()
            return

        keresztnev = self.nev_resz_bekeres("keresztnevét")
        if keresztnev is None:
            print("Foglalás megszakítva.")
            self.idozitett_varakozas()
            return

        jarat = self.jarat_bekeres()
        if jarat is None:
            print("Foglalás megszakítva.")
            self.idozitett_varakozas()
            return

        indulas = self.indulas_bekeres(jarat)
        if indulas is None:
            print("Foglalás megszakítva.")
            self.idozitett_varakozas()
            return

        if self.van_azonos_foglalas(vezeteknev, keresztnev, jarat, indulas.datum):
            print("\nFigyelem! Már létezik foglalás ezzel a névvel, erre a járatra és erre az időpontra.")
            if not self.igen_nem_bekeres("Biztosan szeretnél további jegyet foglalni? (i/n): "):
                print("Foglalás megszakítva.")
                self.idozitett_varakozas()
                return

        print("\nFoglalás adatai:")
        print(f"Utas: {vezeteknev} {keresztnev}")
        print(f"Járat: {jarat.jaratszam}")
        print(f"Célállomás: {jarat.celallomas}")
        print(f"Dátum: {indulas.datum}")
        print(f"Ár: {jarat.jegyar} Ft")

        if not self.igen_nem_bekeres("Biztosan lefoglalod? (i/n): "):
            print("Foglalás megszakítva.")
            self.idozitett_varakozas()
            return

        uj_foglalas = self._foglalas_hozzaadasa(vezeteknev, keresztnev, jarat, indulas.datum)
        self._foglalasok_mentese()
        print("\nSikeres foglalás!")
        print(uj_foglalas)
        self.idozitett_varakozas(3)

    def foglalas_lemondasa(self):
        self.kepernyo_torles()
        if not self._foglalasok:
            print("Nincs lemondható foglalás.")
            self.idozitett_varakozas()
            return

        self.foglalasok_listazasa(False)
        try:
            azonosito = input("\nVisszalépni a főmenübe a 0-as érték megadásával lehet.\nAdd meg a lemondandó foglalás azonosítóját: ").strip()
            if self.visszalepes_e(azonosito):
                print("Lemondás megszakítva.")
                self.idozitett_varakozas()
                return
            foglalas = self.foglalas_keresese_azonosito_alapjan(int(azonosito))
            if foglalas is None:
                print("Nem létezik ilyen azonosítójú foglalás.")
                self.idozitett_varakozas()
                return

            print("\nLemondandó foglalás:")
            print(foglalas)
            if not self.igen_nem_bekeres("Biztosan lemondod ezt a foglalást? (i/n): "):
                print("Lemondás megszakítva.")
                self.idozitett_varakozas()
                return

            foglalas.jarat.indulas_keresese(foglalas.datum).ferohely_novelese()
            self._foglalasok.remove(foglalas)
            self._foglalasok_mentese()
            print("\nA foglalás sikeresen lemondva.")
            self.idozitett_varakozas()
        except ValueError:
            print("Hibás azonosító.")
            self.idozitett_varakozas()

    def foglalas_keresese(self):
        self.kepernyo_torles()
        print("\nKeresés típusa:")
        print("1. Keresés azonosító alapján")
        print("2. Keresés úti cél alapján")
        print("3. Keresés utas neve alapján")
        print("4. Keresés utazás dátuma alapján")
        print("0. Vissza")
        valasztas = input("Választás: ").strip().lower()
        if self.visszalepes_e(valasztas):
            print("Keresés megszakítva.")
            self.idozitett_varakozas()
            return

        talalatok = []
        if valasztas == "1":
            try:
                azonosito = int(input("Add meg a keresett foglalás azonosítóját: "))
                foglalas = self.foglalas_keresese_azonosito_alapjan(azonosito)
                if foglalas:
                    talalatok.append(foglalas)
            except ValueError:
                print("Hibás azonosító.")
                self.idozitett_varakozas()
                return
        elif valasztas == "2":
            uticel = input("Add meg a keresett úti célt: ").strip().lower()
            talalatok = [f for f in self._foglalasok if uticel in f.jarat.celallomas.lower()]
        elif valasztas == "3":
            nev = input("Add meg a keresett utas nevét: ").strip().lower()
            talalatok = [f for f in self._foglalasok if nev in f.teljes_nev.lower()]
        elif valasztas == "4":
            try:
                keresett_datum = datetime.strptime(input("Add meg a keresett dátumot (ÉÉÉÉ-HH-NN): ").strip(), "%Y-%m-%d").date()
                talalatok = [f for f in self._foglalasok if f.datum == keresett_datum]
            except ValueError:
                print("Hibás dátumformátum. Használd ezt: ÉÉÉÉ-HH-NN")
                self.idozitett_varakozas()
                return
        else:
            print("Hibás választás.")
            self.idozitett_varakozas()
            return

        print("\nTalálatok:")
        self.foglalasok_tablazatban_kiirasa(talalatok)
        self.idozitett_varakozas()

    def foglalas_modositasa(self):
        self.kepernyo_torles()
        if not self._foglalasok:
            print("Nincs módosítható foglalás.")
            self.idozitett_varakozas()
            return

        self.foglalasok_listazasa(False)
        try:
            azonosito = input("\nVisszalépni a főmenübe a 0-as érték megadássával lehet.\nAdd meg a módosítandó foglalás azonosítóját: ").strip()
            if self.visszalepes_e(azonosito):
                print("Módosítás megszakítva.")
                self.idozitett_varakozas()
                return
            foglalas = self.foglalas_keresese_azonosito_alapjan(int(azonosito))
            if foglalas is None:
                print("Nincs ilyen foglalás.")
                self.idozitett_varakozas()
                return

            print("\nJelenlegi foglalás:")
            print(foglalas)
            print("\nMit szeretnél módosítani?")
            print("1. Vezetéknév")
            print("2. Keresztnév")
            print("3. Járat és indulás")
            print("0. Mégsem")
            valasztas = input("Választás: ").strip().lower()

            if self.visszalepes_e(valasztas):
                print("Módosítás megszakítva.")
                self.idozitett_varakozas()
                return

            regi_jarat = foglalas.jarat
            regi_datum = foglalas.datum

            if valasztas == "1":
                print(f"Jelenlegi vezetéknév: {foglalas.vezeteknev}")
                uj = self.nev_resz_bekeres("új vezetéknevét")
                if uj is None:
                    print("Módosítás megszakítva.")
                    self.idozitett_varakozas()
                    return
                foglalas.vezeteknev = uj
            elif valasztas == "2":
                print(f"Jelenlegi keresztnév: {foglalas.keresztnev}")
                uj = self.nev_resz_bekeres("új keresztnevét")
                if uj is None:
                    print("Módosítás megszakítva.")
                    self.idozitett_varakozas()
                    return
                foglalas.keresztnev = uj
            elif valasztas == "3":
                print(f"Jelenlegi járat: {foglalas.jarat.jaratszam} - {foglalas.jarat.celallomas}, dátum: {foglalas.datum}")
                self.jaratok_listazasa()
                uj_jarat = self.jarat_bekeres()
                if uj_jarat is None:
                    print("Módosítás megszakítva.")
                    self.idozitett_varakozas()
                    return
                uj_indulas = self.indulas_bekeres(uj_jarat)
                if uj_indulas is None:
                    print("Módosítás megszakítva.")
                    self.idozitett_varakozas()
                    return
                regi_jarat.indulas_keresese(regi_datum).ferohely_novelese()
                uj_indulas.ferohely_csokkentese()
                foglalas.jarat = uj_jarat
                foglalas.datum = uj_indulas.datum
            else:
                print("Hibás választás.")
                self.idozitett_varakozas()
                return

            print("\nMódosított foglalás:")
            print(foglalas)
            if not self.igen_nem_bekeres("Biztosan mented a módosítást? (i/n): "):
                if valasztas == "3":
                    foglalas.jarat.indulas_keresese(foglalas.datum).ferohely_novelese()
                    regi_jarat.indulas_keresese(regi_datum).ferohely_csokkentese()
                    foglalas.jarat = regi_jarat
                    foglalas.datum = regi_datum
                print("Módosítás nem lett mentve.")
                self.idozitett_varakozas()
                return

            self._foglalasok_mentese()
            print("Foglalás sikeresen módosítva.")
            self.idozitett_varakozas()
        except ValueError:
            print("Hibás azonosító.")
            self.idozitett_varakozas()

    def foglalasok_menu(self):
        while True:
            self.kepernyo_torles()
            print("\n--- Foglalások kezelése ---")
            print("\n1. Foglalások listázása")
            print("2. Foglalás keresése")
            print("3. Foglalás módosítása")
            print("4. Foglalás lemondása")
            print("0. Vissza")
            valasztas = input("\nVálassz egy menüpontot: ").strip().lower()
            if valasztas == "1":
                self.kepernyo_torles()
                self.foglalasok_listazasa()
                self.idozitett_varakozas()
            elif valasztas == "2":
                self.foglalas_keresese()
            elif valasztas == "3":
                self.foglalas_modositasa()
            elif valasztas == "4":
                self.foglalas_lemondasa()
            elif self.visszalepes_e(valasztas):
                break
            else:
                print("Hibás menüpont, próbáld újra.")
                self.idozitett_varakozas()

    def menu(self):
        while True:
            self.kepernyo_torles()
            print("\n--- Repülőjegy Foglalási Rendszer ---")
            print(f"Légitársaság: {self._legitarsasag.nev}")
            print("\n1. Új foglalás")
            print("2. Foglalások kezelése")
            print("3. Járatok")
            print("0. Kilépés")
            valasztas = input("\nVálassz egy menüpontot: ").strip().lower()

            if valasztas == "1":
                self.jegy_foglalasa()
            elif valasztas == "2":
                self.foglalasok_menu()
            elif valasztas == "3":
                self.kepernyo_torles()
                self.jaratok_listazasa()

                valasz = input(
                    "\nNyomj ENTER-t a visszalépéshez... "
                ).strip()

                if valasz.lower() in ["0", "back", "vissza", ""]:
                    continue

            elif valasztas.lower() in ["maverick", "top gun", "topgun"]:
                self._maverick_mod = True
                print("Maverick mód aktiválva. Highway to the Danger Zone!")
                self.idozitett_varakozas(2, False)

            elif valasztas in ["0", "kilepes", "kilépés", "quit"]:
                print("Kilépés...")
                break

            elif valasztas.lower() == "neo":
                self.kepernyo_torles()

                print("Wake up, Neo...")
                self.idozitett_varakozas(2, False)

                self.kepernyo_torles()

                print("The Matrix has you...")
                self.idozitett_varakozas(2, False)

                self.kepernyo_torles()

                print("Follow the white rabbit.")
                self.idozitett_varakozas(2, False)

                self.kepernyo_torles()

                print("Knock, Knock, Neo.")
                self.idozitett_varakozas(2, False)

                break
            else:
                print("Hibás menüpont, próbáld újra.")
                self.idozitett_varakozas(1, False)
