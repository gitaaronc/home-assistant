"""
Support for Autohub.

For more details about this component, please refer to the documentation at
https://home-assistant.io/components/autohub/
"""
import logging
import asyncio

import voluptuous as vol

from homeassistant.components.discovery import SERVICE_AUTOHUB
from homeassistant.const import (CONF_HOST, CONF_PORT, EVENT_HOMEASSISTANT_STOP)
from homeassistant.helpers import discovery
from homeassistant.helpers import config_validation as cv

REQUIREMENTS = ['pyautohub==0.1.0']

_LOGGER = logging.getLogger(__name__)

DOMAIN = "autohub2"

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_PORT): cv.string,
		vol.Optional('devices',{}): dict
    })
}, extra = vol.ALLOW_EXTRA)

# Mapping from Wemo model_name to service.
AUTOHUB_PLATFORMS = {
}

@asyncio.coroutine
def async_setup(hass, config):
    """Setup our connectoin to autohubpp"""
    import pyautohub
	
    conf = config[DOMAIN]
    host = conf.get(CONF_HOST)
    port = conf.get(CONF_PORT)

    @callback
    def async_new_device(device):
        """
		   Registered with pyautohub.AutohubWS as callback function
		   Invoked by AutohubWS
        """
        name = device.device_name_
        address = device.device_address_
        properties = device.properties_

        _LOGGER.info('New autohub device %s (%s) %r',
                     name, address, properties)

        hass.async_add_job(
            discovery.async_load_platform(
                hass, light, DOMAIN, discovered=[device],
                hass_config=config))

    def autohub_stop(event):
        _LOGGER.info("Shutting down Authub sockets")
        autohub_object.stop()

    def discovery_dispatch(service, device):
        """ 
          Dispatcher for autohub discovery events. 
          Invoked by HomeAssistant, triggered by 
		"""
        _LOGGER.info("Discovery Dispatch!")
        device_address, device_name = device

        service = DISCOVER_LIGHTS
        component = AUTOHUB_SERVICE_DISPATCH.get(service)

        discovery.load_platform(hass, component, DOMAIN, device, config)

        discovery.discover(hass, service, device, component, config)

    autohub_object = pyautohub.AutohubWS(host, port, _LOGGER)
    hass.data['autohub_object'] = autohub_object

    # register callback handler with pyautohub
    autohub_object.on_device_added(async_new_device)

    hass.bus.listen_once(EVENT_HOMEASSISTANT_STOP, autohub_stop)

    discovery.listen(hass, SERVICE_AUTOHUB, discovery_dispatch)
	
    autohub_object.start()

    return True
