"""Magyar Otthon szenzorok."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from .const import CONF_GARBAGE_CONFIG, CONF_GARBAGE_ENABLED, DEFAULT_OPTIONS, DOMAIN
from .holiday_sensors import async_setup_sensor_entry
from .modules.garbage import (
    GARBAGE_TIPUSOK,
    HulladekKonfiguracio,
    konfiguracio_betoltese,
    hetnap_index_to_nev,
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
                if tipus_azonosito == "fenyofa":
                    entities.append(FenyofaElszallitasNapjaiSensor(entry, konfig))
                else:
                    entities.extend(
                        [
                            HulladekKovetkezoUritesSensor(entry, konfig),
                            HulladekHatralevoNapokSensor(entry, konfig),
                            HulladekKovetkezoNapSensor(entry, konfig),
                        ]
                    )

    async_add_entities(entities)

    await async_setup_next_holiday_sensor(hass, entry, async_add_entities)
    await async_setup_sensor_entry(hass, entry, async_add_entities)


class HulladekAlapSensor(SensorEntity):
    """Közös alap a hulladék szenzorokhoz."""

    _attr_has_entity_name = True

    def __init__(self, entry: ConfigEntry, konfig: HulladekKonfiguracio) -> None:
        self._entry = entry
        self._konfig = konfig

    @property
    def device_info(self) -> dict[str, object]:
        """Külön Home Assistant eszköz minden hulladéktípushoz."""

        return {
            "identifiers": {(DOMAIN, f"{self._entry.entry_id}_{self._konfig.tipus_azonosito}")},
            "name": self._konfig.tipus_nev,
            "manufacturer": "Magyar Otthon",
            "model": "Hulladéknaptár",
            "sw_version": "0.4.0",
        }

    def _kovetkezo(self):
        today = dt_util.now().date()
        return today, kovetkezo_urites(self._konfig, today)


class HulladekKovetkezoUritesSensor(HulladekAlapSensor):
    """Következő ürítés/elszállítás dátuma."""

    def __init__(self, entry: ConfigEntry, konfig: HulladekKonfiguracio) -> None:
        super().__init__(entry, konfig)
        self._attr_name = "Következő elszállítás" if konfig.tipus_azonosito == "fenyofa" else "Következő ürítés"
        self._attr_unique_id = f"magyar_otthon_{entry.entry_id}_{konfig.tipus_azonosito}_kovetkezo"

    @property
    def native_value(self) -> str | None:
        """A következő ürítés dátuma."""

        if not self._konfig.engedelyezve:
            return None

        _, kov = self._kovetkezo()
        return kov.isoformat() if kov is not None else None


class HulladekHatralevoNapokSensor(HulladekAlapSensor):
    """Hátralévő napok száma a következő ürítésig."""

    def __init__(self, entry: ConfigEntry, konfig: HulladekKonfiguracio) -> None:
        super().__init__(entry, konfig)
        self._attr_name = "Hátralévő napok"
        self._attr_unique_id = f"magyar_otthon_{entry.entry_id}_{konfig.tipus_azonosito}_hatralevo_napok"

    @property
    def native_value(self) -> int | None:
        """Hátralévő napok."""

        if not self._konfig.engedelyezve:
            return None

        today, kov = self._kovetkezo()
        if kov is None:
            return None
        return (kov - today).days


class HulladekKovetkezoNapSensor(HulladekAlapSensor):
    """Következő ürítés/elszállítás hét napja."""

    def __init__(self, entry: ConfigEntry, konfig: HulladekKonfiguracio) -> None:
        super().__init__(entry, konfig)
        self._attr_name = "Elszállítás napja" if konfig.tipus_azonosito == "fenyofa" else "Következő ürítés napja"
        self._attr_unique_id = f"magyar_otthon_{entry.entry_id}_{konfig.tipus_azonosito}_kovetkezo_nap"

    @property
    def native_value(self) -> str | None:
        """A következő ürítés napjának neve."""

        if not self._konfig.engedelyezve:
            return None

        _, kov = self._kovetkezo()
        if kov is None:
            return None
        return hetnap_index_to_nev(kov.weekday())


class FenyofaElszallitasNapjaiSensor(HulladekAlapSensor):
    """Fenyőfa elszállítás napjai (max. 2 dátum)."""

    def __init__(self, entry: ConfigEntry, konfig: HulladekKonfiguracio) -> None:
        super().__init__(entry, konfig)
        self._attr_name = "Elszállítás napjai"
        self._attr_unique_id = f"magyar_otthon_{entry.entry_id}_{konfig.tipus_azonosito}_elszallitas_napjai"

    @property
    def native_value(self) -> str | None:
        if not self._konfig.engedelyezve:
            return None
        datumok = self._konfig.kezidatumok[:2]
        if not datumok:
            return None
        return ", ".join(d.isoformat() for d in datumok)