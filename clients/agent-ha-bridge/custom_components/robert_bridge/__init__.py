"""The Robert Bridge integration for Home Assistant."""
import logging
import voluptuous as vol
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_URL, CONF_API_KEY
from homeassistant.helpers import config_validation as cv

_LOGGER = logging.getLogger(__name__)

DOMAIN = "robert_bridge"
CONF_URL = "url"
CONF_SESSION_KEY = "session_key"

# Configuration schema for configuration.yaml
CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_URL, default="http://192.168.1.100:8787/agent"): cv.string,
                vol.Optional(CONF_API_KEY, default="ha-bridge-1"): cv.string,
                vol.Optional(CONF_SESSION_KEY, default="ha-chat"): cv.string,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Robert Bridge component via YAML."""
    if DOMAIN not in config:
        return True

    conf = config[DOMAIN]
    hass.data[DOMAIN] = {
        "url": conf[CONF_URL],
        "api_key": conf.get(CONF_API_KEY),
        "session_key": conf.get(CONF_SESSION_KEY),
    }

    # Register the conversation agent
    from .conversation import async_setup_agent
    await async_setup_agent(hass)
    
    _LOGGER.info("Robert Bridge setup complete. URL: %s", conf[CONF_URL])
    return True
