"""Magyar Otthon szenzorok."""

from __future__ import annotations

from datetime import timedelta

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity_platform import async_get_current_platform
from homeassistant.util import dt as dt_util
import voluptuous as vol

from .const import CONF_GARBAGE_CONFIG, CONF_GARBAGE_ENABLED, DEFAULT_OPTIONS
from .holiday_sensors import async_setup_sensor_entry
from .modules.garbage import (
    GARBAGE_TIPUSOK,
    HulladekKonfiguracio,
    konfiguracio_betoltese,
    hetnap_index_to_nev,
    honap_azonosito_to_szam,
    kovetkezo_urites,
)
from .next_holiday_sensor import async_setup_entry as async_setup_next_holiday_sensor


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Szenzorok létrehozása."""

    options = {**DEFAULT_OPTIONS, **entry.options}

    entities: list[SensorEntity] = []
    if options.get(CONF_GARBAGE_ENABLED, True):
        nyers_beallitas = options.get(CONF_GARBAGE_CONFIG, {})
        if isinstance(nyers_beallitas, dict):
            for tipus_azonosito in GARBAGE_TIPUSOK:
                tipus_beallitas = nyers_beallitas.get(tipus_azonosito, {})
                if not isinstance(tipus_beallitas, dict):
                    tipus_beallitas = {}

                konfig = konfiguracio_betoltese(tipus_azonosito, tipus_beallitas)
                entities.append(HulladekKovetkezoUritesSensor(hass, entry, konfig))

    async_add_entities(entities)

    platform = async_get_current_platform()
    if not hass.data.setdefault("magyar_otthon_service_regisztralva", False):
        platform.async_register_entity_service(
            "hulladek_beallitas_frissites",
            {
                vol.Optional("engedelyezve"): bool,
                vol.Optional("uresites_tipus"): str,
                vol.Optional("het_napja"): str,
                vol.Optional("elso_gyujtes_datum"): str,
                vol.Optional("havi_pozicio"): str,
                vol.Optional("kezdo_honap"): str,
                vol.Optional("zaro_honap"): str,
                vol.Optional("kezdo_datum"): str,
                vol.Optional("zaro_datum"): str,
                vol.Optional("hozzaadando_datumok"): str,
                vol.Optional("torlendo_datumok"): str,
            },
            "async_hulladek_beallitas_frissites",
        )
        hass.data["magyar_otthon_service_regisztralva"] = True

    await async_setup_next_holiday_sensor(hass, entry, async_add_entities)
    await async_setup_sensor_entry(hass, entry, async_add_entities)


class HulladekKovetkezoUritesSensor(SensorEntity):
    """Egy hulladéktípus következő ürítési dátuma."""

    _attr_has_entity_name = True

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, konfig: HulladekKonfiguracio) -> None:
        self._hass = hass
        self._entry = entry
        self._konfig = konfig
        self._attr_name = konfig.tipus_nev
        if konfig.tipus_azonosito == "kommunalis":
            # Preserve the historical unique id so HA does not keep a duplicate municipal entity.
            self._attr_unique_id = "magyar_otthon_kommunális_hulladék"
        else:
            self._attr_unique_id = f"magyar_otthon_{entry.entry_id}_{konfig.tipus_azonosito}"

    @property
    def native_value(self) -> str | None:
        """Szenzor állapota."""

        if not self._konfig.engedelyezve:
            return "Kikapcsolva"

        today = dt_util.now().date()
        kov = kovetkezo_urites(self._konfig, today)
        return kov.isoformat() if kov is not None else "Nincs közelgő ürítés"

    @property
    def extra_state_attributes(self) -> dict[str, object]:
        """Extra attribútumok."""

        today = dt_util.now().date()
        tomorrow = today + timedelta(days=1)
        kov = kovetkezo_urites(self._konfig, today)
        if not self._konfig.engedelyezve:
            return {
                "következő_ürítés": None,
                "hátralévő_napok": None,
                "ürítés_ma": False,
                "ürítés_holnap": False,
                "következő_ürítés_napja": None,
                "aktuális_állapot": "Kikapcsolva",
                "hulladék_típusa": self._konfig.tipus_nev,
                "beállítások": "Integráció > Magyar Otthon > Beállítások",
            }

        if kov is None:
            return {
                "következő_ürítés": None,
                "hátralévő_napok": None,
                "ürítés_ma": False,
                "ürítés_holnap": False,
                "következő_ürítés_napja": None,
                "aktuális_állapot": "Nincs közelgő ürítés",
                "hulladék_típusa": self._konfig.tipus_nev,
                "beállítások": "Integráció > Magyar Otthon > Beállítások",
            }

        hatralevo = (kov - today).days

        return {
            "következő_ürítés": kov.isoformat(),
            "hátralévő_napok": hatralevo,
            "ürítés_ma": kov == today,
            "ürítés_holnap": kov == tomorrow,
            "következő_ürítés_napja": hetnap_index_to_nev(kov.weekday()),
            "aktuális_állapot": "Aktív",
            "hulladék_típusa": self._konfig.tipus_nev,
            "beállítások": "Integráció > Magyar Otthon > Beállítások",
        }

    async def async_hulladek_beallitas_frissites(self, **service_data: object) -> None:
        """Entitás szintről frissíthető hulladékbeállítások mentése."""

        aktualis_opciok = {**DEFAULT_OPTIONS, **self._entry.options}
        nyers = aktualis_opciok.get(CONF_GARBAGE_CONFIG, {})
        if not isinstance(nyers, dict):
            nyers = {}

        tipus_azonosito = self._konfig.tipus_azonosito
        tipus_beallitas = nyers.get(tipus_azonosito, {})
        if not isinstance(tipus_beallitas, dict):
            tipus_beallitas = {}

        for kulcs in (
            "engedelyezve",
            "uresites_tipus",
            "het_napja",
            "elso_gyujtes_datum",
            "havi_pozicio",
            "kezdo_datum",
            "zaro_datum",
        ):
            if kulcs in service_data and service_data[kulcs] is not None:
                tipus_beallitas[kulcs] = service_data[kulcs]

        if "kezdo_honap" in service_data and service_data["kezdo_honap"] is not None:
            tipus_beallitas["kezdo_honap"] = honap_azonosito_to_szam(str(service_data["kezdo_honap"]))
        if "zaro_honap" in service_data and service_data["zaro_honap"] is not None:
            tipus_beallitas["zaro_honap"] = honap_azonosito_to_szam(str(service_data["zaro_honap"]))

        kezidatumok = set(str(item) for item in tipus_beallitas.get("kezidatumok", []))
        hozzaad = str(service_data.get("hozzaadando_datumok", "")).strip()
        torol = str(service_data.get("torlendo_datumok", "")).strip()
        if hozzaad:
            kezidatumok.update(d.strip() for d in hozzaad.split(",") if d.strip())
        if torol:
            kezidatumok.difference_update(d.strip() for d in torol.split(",") if d.strip())
        tipus_beallitas["kezidatumok"] = sorted(kezidatumok)

        nyers[tipus_azonosito] = tipus_beallitas
        aktualis_opciok[CONF_GARBAGE_CONFIG] = nyers

        self._hass.config_entries.async_update_entry(self._entry, options=aktualis_opciok)
        await self._hass.config_entries.async_reload(self._entry.entry_id)