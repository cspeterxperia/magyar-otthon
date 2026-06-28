"""Hulladékszállítás számítási modul."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

GARBAGE_TIPUSOK: dict[str, str] = {
    "kommunalis": "Kommunális hulladék",
    "szelektiv": "Szelektív hulladék",
    "zoldhulladek": "Zöldhulladék",
    "lomtalanitas": "Lomtalanítás",
    "fenyofa": "Fenyőfa elszállítás",
}

HONAPOK: dict[str, int] = {
    "januar": 1,
    "februar": 2,
    "marcius": 3,
    "aprilis": 4,
    "majus": 5,
    "junius": 6,
    "julius": 7,
    "augusztus": 8,
    "szeptember": 9,
    "oktober": 10,
    "november": 11,
    "december": 12,
}

HONAP_NEV_BY_SZAM: dict[int, str] = {
    1: "Január",
    2: "Február",
    3: "Március",
    4: "Április",
    5: "Május",
    6: "Június",
    7: "Július",
    8: "Augusztus",
    9: "Szeptember",
    10: "Október",
    11: "November",
    12: "December",
}

HETNAP_NEV_BY_INDEX: dict[int, str] = {
    0: "Hétfő",
    1: "Kedd",
    2: "Szerda",
    3: "Csütörtök",
    4: "Péntek",
    5: "Szombat",
    6: "Vasárnap",
}

URESITESI_GYAKORISAG: dict[str, int] = {
    "hetente": 1,
    "kethetente": 2,
    "haromhetente": 3,
    "negynhetente": 4,
}

HAVI_POZICIOK = {"elso", "masodik", "harmadik", "negyedik", "utolso"}
AKTIV_IDOSZAKOK = {"egesz_ev", "honap_tartomany", "datum_tartomany"}


def alap_hulladek_beallitasok() -> dict[str, dict[str, object]]:
    """Alapértelmezett hulladékbeállítások visszaadása."""

    return {
        "kommunalis": {
            "engedelyezve": True,
            "uresites_tipus": "hetente",
            "het_napja": "hetfo",
            "elso_gyujtes_datum": "",
            "havi_pozicio": "elso",
            "kezidatumok": [],
            "aktiv_idoszak": "egesz_ev",
            "kezdo_honap": 1,
            "zaro_honap": 12,
            "kezdo_datum": "",
            "zaro_datum": "",
        },
        "szelektiv": {
            "engedelyezve": False,
            "uresites_tipus": "kethetente",
            "het_napja": "hetfo",
            "elso_gyujtes_datum": "",
            "havi_pozicio": "elso",
            "kezidatumok": [],
            "aktiv_idoszak": "egesz_ev",
            "kezdo_honap": 1,
            "zaro_honap": 12,
            "kezdo_datum": "",
            "zaro_datum": "",
        },
        "zoldhulladek": {
            "engedelyezve": False,
            "uresites_tipus": "kethetente",
            "het_napja": "hetfo",
            "elso_gyujtes_datum": "",
            "havi_pozicio": "elso",
            "kezidatumok": [],
            "aktiv_idoszak": "honap_tartomany",
            "kezdo_honap": 3,
            "zaro_honap": 11,
            "kezdo_datum": "",
            "zaro_datum": "",
        },
        "lomtalanitas": {
            "engedelyezve": False,
            "uresites_tipus": "kezi_datumok",
            "het_napja": "hetfo",
            "elso_gyujtes_datum": "",
            "havi_pozicio": "elso",
            "kezidatumok": [],
            "aktiv_idoszak": "egesz_ev",
            "kezdo_honap": 1,
            "zaro_honap": 12,
            "kezdo_datum": "",
            "zaro_datum": "",
        },
        "fenyofa": {
            "engedelyezve": False,
            "uresites_tipus": "kezi_datumok",
            "het_napja": "hetfo",
            "elso_gyujtes_datum": "",
            "havi_pozicio": "elso",
            "kezidatumok": [],
            "aktiv_idoszak": "egesz_ev",
            "kezdo_honap": 1,
            "zaro_honap": 12,
            "kezdo_datum": "",
            "zaro_datum": "",
        },
    }


@dataclass(slots=True)
class HulladekKonfiguracio:
    """Egy hulladéktípus konfigurációja számításhoz."""

    tipus_azonosito: str
    tipus_nev: str
    engedelyezve: bool
    uresites_tipus: str
    het_napja: int
    elso_gyujtes_datum: date | None
    havi_pozicio: str
    kezidatumok: list[date]
    aktiv_idoszak: str
    kezdo_honap: int
    zaro_honap: int
    kezdo_datum: date | None
    zaro_datum: date | None


def konfiguracio_betoltese(tipus_azonosito: str, adatok: dict[str, object]) -> HulladekKonfiguracio:
    """Beállítások normalizálása számításra alkalmas struktúrába."""

    hetnap = _het_napja_index(str(adatok.get("het_napja", "hetfo")))
    kezidatumok = sorted(
        {
            parsed
            for parsed in (_parse_datum(item) for item in adatok.get("kezidatumok", []))
            if parsed is not None
        }
    )

    return HulladekKonfiguracio(
        tipus_azonosito=tipus_azonosito,
        tipus_nev=GARBAGE_TIPUSOK.get(tipus_azonosito, tipus_azonosito),
        engedelyezve=bool(adatok.get("engedelyezve", False)),
        uresites_tipus=str(adatok.get("uresites_tipus", "hetente")),
        het_napja=hetnap,
        elso_gyujtes_datum=_parse_datum(adatok.get("elso_gyujtes_datum")),
        havi_pozicio=str(adatok.get("havi_pozicio", "elso")),
        kezidatumok=kezidatumok,
        aktiv_idoszak=str(adatok.get("aktiv_idoszak", "egesz_ev")),
        kezdo_honap=int(adatok.get("kezdo_honap", 1)),
        zaro_honap=int(adatok.get("zaro_honap", 12)),
        kezdo_datum=_parse_datum(adatok.get("kezdo_datum")),
        zaro_datum=_parse_datum(adatok.get("zaro_datum")),
    )


def kovetkezo_urites(konfig: HulladekKonfiguracio, tol_nap: date) -> date | None:
    """Visszaadja a következő ürítés dátumát."""

    if not konfig.engedelyezve:
        return None

    if konfig.uresites_tipus == "kezi_datumok":
        for nap in konfig.kezidatumok:
            if nap >= tol_nap and _aktiv_idoszakban_van(konfig, nap):
                return nap
        return None

    nap = tol_nap
    for _ in range(1825):
        if uritesi_nap_e(konfig, nap):
            return nap
        nap += timedelta(days=1)
    return None


def uritesi_nap_e(konfig: HulladekKonfiguracio, nap: date) -> bool:
    """Igaz, ha a megadott napon ürítés van."""

    if not konfig.engedelyezve:
        return False

    if not _aktiv_idoszakban_van(konfig, nap):
        return False

    if konfig.uresites_tipus in URESITESI_GYAKORISAG:
        if nap.weekday() != konfig.het_napja:
            return False
        if konfig.elso_gyujtes_datum is None:
            return False
        kulonbseg = (nap - konfig.elso_gyujtes_datum).days
        if kulonbseg < 0:
            return False
        periodus_nap = URESITESI_GYAKORISAG[konfig.uresites_tipus] * 7
        return kulonbseg % periodus_nap == 0

    if konfig.uresites_tipus == "havi":
        if nap.weekday() != konfig.het_napja:
            return False
        pozicio = _havi_pozicio(nap)
        if konfig.havi_pozicio == "utolso":
            return pozicio == "utolso"
        return pozicio == konfig.havi_pozicio

    if konfig.uresites_tipus == "kezi_datumok":
        return nap in set(konfig.kezidatumok)

    return False


def _aktiv_idoszakban_van(konfig: HulladekKonfiguracio, nap: date) -> bool:
    if konfig.aktiv_idoszak not in AKTIV_IDOSZAKOK:
        return True

    if konfig.aktiv_idoszak == "egesz_ev":
        return True

    if konfig.aktiv_idoszak == "honap_tartomany":
        kezdo = max(1, min(12, konfig.kezdo_honap))
        zaro = max(1, min(12, konfig.zaro_honap))
        if kezdo <= zaro:
            return kezdo <= nap.month <= zaro
        return nap.month >= kezdo or nap.month <= zaro

    if konfig.kezdo_datum is None or konfig.zaro_datum is None:
        return False

    return konfig.kezdo_datum <= nap <= konfig.zaro_datum


def _parse_datum(ertek: object) -> date | None:
    if not ertek:
        return None

    try:
        return date.fromisoformat(str(ertek))
    except ValueError:
        return None


def _het_napja_index(het_napja: str) -> int:
    mapping = {
        "hetfo": 0,
        "kedd": 1,
        "szerda": 2,
        "csutortok": 3,
        "pentek": 4,
        "szombat": 5,
        "vasarnap": 6,
    }
    return mapping.get(het_napja, 0)


def _havi_pozicio(nap: date) -> str:
    het_index = (nap.day - 1) // 7
    if nap.day + 7 > _honap_napjai(nap.year, nap.month):
        return "utolso"
    mapping = {0: "elso", 1: "masodik", 2: "harmadik", 3: "negyedik"}
    return mapping.get(het_index, "utolso")


def _honap_napjai(ev: int, honap: int) -> int:
    if honap == 12:
        return 31
    kovetkezo = date(ev, honap + 1, 1)
    aktualis = date(ev, honap, 1)
    return (kovetkezo - aktualis).days


def honap_azonosito_to_szam(azonosito: str) -> int:
    """Hónap azonosító (pl. januar) -> hónapszám."""

    return HONAPOK.get(azonosito, 1)


def honap_szam_to_nev(honap: int) -> str:
    """Hónapszám -> magyar hónapnév."""

    return HONAP_NEV_BY_SZAM.get(honap, "Ismeretlen")


def hetnap_index_to_nev(index: int) -> str:
    """Hétnap index -> magyar név."""

    return HETNAP_NEV_BY_INDEX.get(index, "Ismeretlen")