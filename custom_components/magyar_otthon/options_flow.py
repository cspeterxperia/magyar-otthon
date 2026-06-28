"""Options flow for Magyar Otthon."""

from __future__ import annotations

from datetime import date

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers import selector

from .const import (
    CONF_CALENDAR_COLOR,
    CONF_COUNTRY,
    CONF_ENABLE_DEBUG_LOGGING,
    CONF_COUNTY,
    CONF_CUSTOM_CALENDAR_ENABLED,
    CONF_GARBAGE_CONFIG,
    CONF_GARBAGE_ENABLED,
    CONF_HOLIDAYS_ENABLED,
    CONF_MUNICIPALITY,
    CONF_NAMEDAYS_ENABLED,
    CONF_REFRESH_INTERVAL,
    CONF_SCHOOL_ENABLED,
    CONF_SCHOOL_TYPE,
    CONF_WASTE_PROVIDER,
    DEFAULT_OPTIONS,
)
from .modules.garbage import GARBAGE_TIPUSOK, alap_hulladek_beallitasok

HONAP_SELECTOR_OPCIOK = [
    selector.SelectOptionDict(value="januar", label="Január"),
    selector.SelectOptionDict(value="februar", label="Február"),
    selector.SelectOptionDict(value="marcius", label="Március"),
    selector.SelectOptionDict(value="aprilis", label="Április"),
    selector.SelectOptionDict(value="majus", label="Május"),
    selector.SelectOptionDict(value="junius", label="Június"),
    selector.SelectOptionDict(value="julius", label="Július"),
    selector.SelectOptionDict(value="augusztus", label="Augusztus"),
    selector.SelectOptionDict(value="szeptember", label="Szeptember"),
    selector.SelectOptionDict(value="oktober", label="Október"),
    selector.SelectOptionDict(value="november", label="November"),
    selector.SelectOptionDict(value="december", label="December"),
]

HONAP_AZONOSITO_TO_SZAM = {
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

HONAP_SZAM_TO_AZONOSITO = {ertek: kulcs for kulcs, ertek in HONAP_AZONOSITO_TO_SZAM.items()}


class MagyarOtthonOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle integration options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize the options flow."""

        self._config_entry = config_entry
        self._options = {**DEFAULT_OPTIONS, **config_entry.options}
        self._garbage_config: dict[str, dict[str, object]] = {}
        self._aktiv_tipus: str | None = None

    async def async_step_init(self, user_input=None):
        """Main menu for options configuration."""

        self._garbage_config = self._normalizalt_hulladek_beallitasok(
            self._options.get(CONF_GARBAGE_CONFIG)
        )

        return self.async_show_menu(
            step_id="init",
            menu_options=["altalanos", "hulladek_valaszto"],
        )

    async def async_step_altalanos(self, user_input=None):
        """General options not tied to one garbage type."""

        if user_input is not None:
            self._options.update(user_input)
            self._options[CONF_GARBAGE_CONFIG] = self._garbage_config
            return self.async_create_entry(title="", data=self._options)

        return self.async_show_form(
            step_id="altalanos",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_HOLIDAYS_ENABLED, default=self._options[CONF_HOLIDAYS_ENABLED]): bool,
                    vol.Optional(CONF_SCHOOL_ENABLED, default=self._options[CONF_SCHOOL_ENABLED]): bool,
                    vol.Optional(CONF_GARBAGE_ENABLED, default=self._options[CONF_GARBAGE_ENABLED]): bool,
                    vol.Optional(CONF_NAMEDAYS_ENABLED, default=self._options[CONF_NAMEDAYS_ENABLED]): bool,
                    vol.Optional(CONF_CUSTOM_CALENDAR_ENABLED, default=self._options[CONF_CUSTOM_CALENDAR_ENABLED]): bool,
                    vol.Optional(CONF_COUNTRY, default=self._options[CONF_COUNTRY]): str,
                    vol.Optional(CONF_COUNTY, default=self._options[CONF_COUNTY]): str,
                    vol.Optional(CONF_MUNICIPALITY, default=self._options[CONF_MUNICIPALITY]): str,
                    vol.Optional(CONF_WASTE_PROVIDER, default=self._options[CONF_WASTE_PROVIDER]): str,
                    vol.Optional(CONF_SCHOOL_TYPE, default=self._options[CONF_SCHOOL_TYPE]): str,
                    vol.Optional(CONF_CALENDAR_COLOR, default=self._options[CONF_CALENDAR_COLOR]): str,
                    vol.Optional(CONF_REFRESH_INTERVAL, default=self._options[CONF_REFRESH_INTERVAL]): int,
                    vol.Optional(CONF_ENABLE_DEBUG_LOGGING, default=self._options[CONF_ENABLE_DEBUG_LOGGING]): bool,
                }
            ),
        )

    async def async_step_hulladek_valaszto(self, user_input=None):
        """Select which garbage type to configure."""

        if user_input is not None:
            kivalasztott = user_input["hulladek_tipus"]
            if kivalasztott == "mentes_es_kilepes":
                self._options[CONF_GARBAGE_CONFIG] = self._garbage_config
                return self.async_create_entry(title="", data=self._options)

            self._aktiv_tipus = kivalasztott
            if kivalasztott == "fenyofa":
                return await self.async_step_hulladek_fenyofa()
            return await self.async_step_hulladek_alap()

        tipus_opciok = [
            selector.SelectOptionDict(value=tipus, label=nev)
            for tipus, nev in GARBAGE_TIPUSOK.items()
        ]
        tipus_opciok.append(
            selector.SelectOptionDict(value="mentes_es_kilepes", label="Mentés és kilépés")
        )

        return self.async_show_form(
            step_id="hulladek_valaszto",
            data_schema=vol.Schema(
                {
                    vol.Required("hulladek_tipus"): selector.SelectSelector(
                        selector.SelectSelectorConfig(options=tipus_opciok, mode=selector.SelectSelectorMode.DROPDOWN)
                    )
                }
            ),
        )

    async def async_step_hulladek_fenyofa(self, user_input=None):
        """Fenyőfa elszállítás – csak 2 dátum megadása."""

        if self._aktiv_tipus is None:
            return await self.async_step_hulladek_valaszto()

        aktualis = self._garbage_config[self._aktiv_tipus]
        kezidatumok = aktualis.get("kezidatumok", [])
        datum1 = str(kezidatumok[0]) if len(kezidatumok) > 0 else ""
        datum2 = str(kezidatumok[1]) if len(kezidatumok) > 1 else ""
        hibak: dict[str, str] = {}

        if user_input is not None:
            datumok: list[str] = []
            for key in ("datum1", "datum2"):
                val = str(user_input.get(key, "")).strip()
                if val:
                    try:
                        date.fromisoformat(val)
                        datumok.append(val)
                    except ValueError:
                        hibak["base"] = "ervenytelen_adat"
            if not hibak:
                aktualis["engedelyezve"] = bool(user_input.get("engedelyezve", False))
                aktualis["uresites_tipus"] = "kezi_datumok"
                aktualis["kezidatumok"] = sorted(datumok)
                self._garbage_config[self._aktiv_tipus] = aktualis
                self._aktiv_tipus = None
                return await self.async_step_hulladek_valaszto()

        return self.async_show_form(
            step_id="hulladek_fenyofa",
            data_schema=vol.Schema(
                {
                    vol.Optional("engedelyezve", default=bool(aktualis.get("engedelyezve", False))): bool,
                    vol.Optional("datum1", default=datum1): str,
                    vol.Optional("datum2", default=datum2): str,
                }
            ),
            errors=hibak,
        )

    async def async_step_hulladek_alap(self, user_input=None):
        """Configure base schedule mode for a selected garbage type."""

        if self._aktiv_tipus is None:
            return await self.async_step_hulladek_valaszto()

        aktualis = self._garbage_config[self._aktiv_tipus]

        if user_input is not None:
            aktualis.update(user_input)
            return await self.async_step_hulladek_reszletek()

        return self.async_show_form(
            step_id="hulladek_alap",
            data_schema=vol.Schema(
                {
                    vol.Optional("engedelyezve", default=bool(aktualis.get("engedelyezve", False))): bool,
                    vol.Required("uresites_tipus", default=str(aktualis.get("uresites_tipus", "hetente"))): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=[
                                selector.SelectOptionDict(value="hetente", label="Minden héten"),
                                selector.SelectOptionDict(value="kethetente", label="Minden 2. héten"),
                                selector.SelectOptionDict(value="haromhetente", label="Minden 3. héten"),
                                selector.SelectOptionDict(value="negynhetente", label="Minden 4. héten"),
                                selector.SelectOptionDict(value="havi", label="Havi"),
                                selector.SelectOptionDict(value="kezi_datumok", label="Kézi dátumok"),
                            ],
                            mode=selector.SelectSelectorMode.DROPDOWN,
                        )
                    ),
                    vol.Required("aktiv_idoszak", default=str(aktualis.get("aktiv_idoszak", "egesz_ev"))): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=[
                                selector.SelectOptionDict(value="egesz_ev", label="Egész év"),
                                selector.SelectOptionDict(value="honap_tartomany", label="Kezdő hónap - záró hónap"),
                                selector.SelectOptionDict(value="datum_tartomany", label="Kezdő dátum - záró dátum"),
                            ],
                            mode=selector.SelectSelectorMode.DROPDOWN,
                        )
                    ),
                }
            ),
        )

    async def async_step_hulladek_reszletek(self, user_input=None):
        """Configure only the fields required by the selected schedule mode."""

        if self._aktiv_tipus is None:
            return await self.async_step_hulladek_valaszto()

        aktualis = self._garbage_config[self._aktiv_tipus]
        hibak: dict[str, str] = {}

        if user_input is not None:
            try:
                self._alkalmaz_hulladek_reszletek(aktualis, user_input)
                self._garbage_config[self._aktiv_tipus] = aktualis
                self._aktiv_tipus = None
                return await self.async_step_hulladek_valaszto()
            except ValueError:
                hibak["base"] = "ervenytelen_adat"

        schema_adat: dict[vol.Marker, object] = {}

        uresites_tipus = str(aktualis.get("uresites_tipus", "hetente"))
        aktiv_idoszak = str(aktualis.get("aktiv_idoszak", "egesz_ev"))

        if uresites_tipus in {"hetente", "kethetente", "haromhetente", "negynhetente"}:
            schema_adat[vol.Required("het_napja", default=str(aktualis.get("het_napja", "hetfo")))] = selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[
                        selector.SelectOptionDict(value="hetfo", label="Hétfő"),
                        selector.SelectOptionDict(value="kedd", label="Kedd"),
                        selector.SelectOptionDict(value="szerda", label="Szerda"),
                        selector.SelectOptionDict(value="csutortok", label="Csütörtök"),
                        selector.SelectOptionDict(value="pentek", label="Péntek"),
                        selector.SelectOptionDict(value="szombat", label="Szombat"),
                        selector.SelectOptionDict(value="vasarnap", label="Vasárnap"),
                    ],
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            )
            schema_adat[vol.Required("elso_gyujtes_datum", default=str(aktualis.get("elso_gyujtes_datum", "")))] = str

        elif uresites_tipus == "havi":
            schema_adat[vol.Required("havi_pozicio", default=str(aktualis.get("havi_pozicio", "elso")))] = selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[
                        selector.SelectOptionDict(value="elso", label="Első"),
                        selector.SelectOptionDict(value="masodik", label="Második"),
                        selector.SelectOptionDict(value="harmadik", label="Harmadik"),
                        selector.SelectOptionDict(value="negyedik", label="Negyedik"),
                        selector.SelectOptionDict(value="utolso", label="Utolsó"),
                    ],
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            )
            schema_adat[vol.Required("het_napja", default=str(aktualis.get("het_napja", "hetfo")))] = selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[
                        selector.SelectOptionDict(value="hetfo", label="Hétfő"),
                        selector.SelectOptionDict(value="kedd", label="Kedd"),
                        selector.SelectOptionDict(value="szerda", label="Szerda"),
                        selector.SelectOptionDict(value="csutortok", label="Csütörtök"),
                        selector.SelectOptionDict(value="pentek", label="Péntek"),
                        selector.SelectOptionDict(value="szombat", label="Szombat"),
                        selector.SelectOptionDict(value="vasarnap", label="Vasárnap"),
                    ],
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            )

        elif uresites_tipus == "kezi_datumok":
            schema_adat[vol.Optional("hozzaadando_datumok", default="")] = str
            schema_adat[vol.Optional("torlendo_datumok", default="")] = str

        if aktiv_idoszak == "honap_tartomany":
            schema_adat[vol.Required("kezdo_honap", default=HONAP_SZAM_TO_AZONOSITO.get(int(aktualis.get("kezdo_honap", 1)), "januar"))] = selector.SelectSelector(
                selector.SelectSelectorConfig(options=HONAP_SELECTOR_OPCIOK, mode=selector.SelectSelectorMode.DROPDOWN)
            )
            schema_adat[vol.Required("zaro_honap", default=HONAP_SZAM_TO_AZONOSITO.get(int(aktualis.get("zaro_honap", 12)), "december"))] = selector.SelectSelector(
                selector.SelectSelectorConfig(options=HONAP_SELECTOR_OPCIOK, mode=selector.SelectSelectorMode.DROPDOWN)
            )
        elif aktiv_idoszak == "datum_tartomany":
            schema_adat[vol.Required("kezdo_datum", default=str(aktualis.get("kezdo_datum", "")))] = str
            schema_adat[vol.Required("zaro_datum", default=str(aktualis.get("zaro_datum", "")))] = str

        return self.async_show_form(
            step_id="hulladek_reszletek",
            data_schema=vol.Schema(schema_adat),
            errors=hibak,
        )

    def _normalizalt_hulladek_beallitasok(self, jelenlegi: object) -> dict[str, dict[str, object]]:
        alap = alap_hulladek_beallitasok()
        if not isinstance(jelenlegi, dict):
            return alap

        eredmeny = alap
        for tipus, beallitas in jelenlegi.items():
            if tipus in eredmeny and isinstance(beallitas, dict):
                eredmeny[tipus].update(beallitas)
        return eredmeny

    def _alkalmaz_hulladek_reszletek(self, aktualis: dict[str, object], user_input: dict[str, object]) -> None:
        uresites_tipus = str(aktualis.get("uresites_tipus", "hetente"))
        aktiv_idoszak = str(aktualis.get("aktiv_idoszak", "egesz_ev"))

        if uresites_tipus in {"hetente", "kethetente", "haromhetente", "negynhetente"}:
            elso = str(user_input.get("elso_gyujtes_datum", "")).strip()
            if not elso:
                raise ValueError("Hianyzo elso gyujtes datum")
            aktualis["het_napja"] = str(user_input["het_napja"])
            aktualis["elso_gyujtes_datum"] = elso

        elif uresites_tipus == "havi":
            aktualis["havi_pozicio"] = str(user_input["havi_pozicio"])
            aktualis["het_napja"] = str(user_input["het_napja"])

        elif uresites_tipus == "kezi_datumok":
            kezidatumok = {str(item) for item in aktualis.get("kezidatumok", [])}

            hozzaad = self._datum_lista(user_input.get("hozzaadando_datumok", ""))
            torol = self._datum_lista(user_input.get("torlendo_datumok", ""))

            kezidatumok.update(hozzaad)
            kezidatumok.difference_update(torol)
            aktualis["kezidatumok"] = sorted(kezidatumok)

        if aktiv_idoszak == "honap_tartomany":
            aktualis["kezdo_honap"] = HONAP_AZONOSITO_TO_SZAM[str(user_input["kezdo_honap"])]
            aktualis["zaro_honap"] = HONAP_AZONOSITO_TO_SZAM[str(user_input["zaro_honap"])]
            aktualis["kezdo_datum"] = ""
            aktualis["zaro_datum"] = ""
        elif aktiv_idoszak == "datum_tartomany":
            kezdo = str(user_input["kezdo_datum"]).strip()
            zaro = str(user_input["zaro_datum"]).strip()
            if not kezdo or not zaro:
                raise ValueError("Hianyzo datum tartomany")
            aktualis["kezdo_datum"] = kezdo
            aktualis["zaro_datum"] = zaro
            aktualis["kezdo_honap"] = 1
            aktualis["zaro_honap"] = 12
        else:
            aktualis["kezdo_honap"] = 1
            aktualis["zaro_honap"] = 12
            aktualis["kezdo_datum"] = ""
            aktualis["zaro_datum"] = ""

    def _datum_lista(self, nyers: object) -> set[str]:
        if nyers is None:
            return set()
        szoveg = str(nyers).strip()
        if not szoveg:
            return set()

        elemek = [elem.strip() for elem in szoveg.split(",") if elem.strip()]
        for elem in elemek:
            try:
                date.fromisoformat(elem)
            except ValueError as err:
                raise ValueError("Ervenytelen datum") from err
        return set(elemek)
