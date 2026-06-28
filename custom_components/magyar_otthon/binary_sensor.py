"""Binary sensor platform for Magyar Otthon."""

from __future__ import annotations

from datetime import timedelta

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from .const import CONF_GARBAGE_CONFIG, CONF_GARBAGE_ENABLED, DEFAULT_OPTIONS, DOMAIN
from .holiday_sensors import async_setup_binary_sensor_entry
from .modules.garbage import GARBAGE_TIPUSOK, HulladekKonfiguracio, konfiguracio_betoltese, uritesi_nap_e


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the integration's binary sensors."""

    options = {**DEFAULT_OPTIONS, **entry.options}
    garbage_entities: list[BinarySensorEntity] = []

    if options.get(CONF_GARBAGE_ENABLED, True):
        nyers_beallitas = options.get(CONF_GARBAGE_CONFIG, {})
        if isinstance(nyers_beallitas, dict):
            for tipus_azonosito in GARBAGE_TIPUSOK:
                tipus_beallitas = nyers_beallitas.get(tipus_azonosito, {})
                if not isinstance(tipus_beallitas, dict):
                    tipus_beallitas = {}

                konfig = konfiguracio_betoltese(tipus_azonosito, tipus_beallitas)
                garbage_entities.extend(
                    [
                        HulladekMaBinarySensor(entry, konfig),
                        HulladekHolnapBinarySensor(entry, konfig),
                    ]
                )

    async_add_entities(garbage_entities)
    await async_setup_binary_sensor_entry(hass, entry, async_add_entities)


class HulladekAlapBinarySensor(BinarySensorEntity):
    """Közös alap a hulladék bináris szenzorokhoz."""

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


class HulladekMaBinarySensor(HulladekAlapBinarySensor):
    """Jelzi, hogy ma van-e ürítés/elszállítás."""

    def __init__(self, entry: ConfigEntry, konfig: HulladekKonfiguracio) -> None:
        super().__init__(entry, konfig)
        self._attr_name = "Elszállítás ma" if konfig.tipus_azonosito == "fenyofa" else "Ürítés ma"
        self._attr_unique_id = f"magyar_otthon_{entry.entry_id}_{konfig.tipus_azonosito}_ma"

    @property
    def is_on(self) -> bool:
        if not self._konfig.engedelyezve:
            return False
        return uritesi_nap_e(self._konfig, dt_util.now().date())


class HulladekHolnapBinarySensor(HulladekAlapBinarySensor):
    """Jelzi, hogy holnap van-e ürítés/elszállítás."""

    def __init__(self, entry: ConfigEntry, konfig: HulladekKonfiguracio) -> None:
        super().__init__(entry, konfig)
        self._attr_name = "Elszállítás holnap" if konfig.tipus_azonosito == "fenyofa" else "Ürítés holnap"
        self._attr_unique_id = f"magyar_otthon_{entry.entry_id}_{konfig.tipus_azonosito}_holnap"

    @property
    def is_on(self) -> bool:
        if not self._konfig.engedelyezve:
            return False
        return uritesi_nap_e(self._konfig, dt_util.now().date() + timedelta(days=1))
