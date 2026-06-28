"""Konstansok a Magyar Otthon integrációhoz."""

DOMAIN = "magyar_otthon"
NAME = "Magyar Otthon"
VERSION = "0.3.1"

CONF_HOLIDAYS_ENABLED = "holidays_enabled"
CONF_SCHOOL_ENABLED = "school_enabled"
CONF_GARBAGE_ENABLED = "garbage_enabled"
CONF_NAMEDAYS_ENABLED = "namedays_enabled"
CONF_CUSTOM_CALENDAR_ENABLED = "custom_calendar_enabled"
CONF_COUNTRY = "country"
CONF_COUNTY = "county"
CONF_MUNICIPALITY = "municipality"
CONF_WASTE_PROVIDER = "waste_provider"
CONF_SCHOOL_TYPE = "school_type"
CONF_CALENDAR_COLOR = "calendar_color"
CONF_REFRESH_INTERVAL = "refresh_interval"
CONF_ENABLE_DEBUG_LOGGING = "enable_debug_logging"

DEFAULT_OPTIONS = {
    CONF_HOLIDAYS_ENABLED: True,
    CONF_SCHOOL_ENABLED: False,
    CONF_GARBAGE_ENABLED: True,
    CONF_NAMEDAYS_ENABLED: False,
    CONF_CUSTOM_CALENDAR_ENABLED: False,
    CONF_COUNTRY: "Magyarország",
    CONF_COUNTY: "",
    CONF_MUNICIPALITY: "",
    CONF_WASTE_PROVIDER: "",
    CONF_SCHOOL_TYPE: "",
    CONF_CALENDAR_COLOR: "#03a9f4",
    CONF_REFRESH_INTERVAL: 3600,
    CONF_ENABLE_DEBUG_LOGGING: False,
}

PLATFORMS = [
    "sensor",
    "calendar",
    "binary_sensor",
]