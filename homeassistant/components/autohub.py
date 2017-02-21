"""
Support for Autohub.

For more details about this component, please refer to the documentation at
https://home-assistant.io/components/autohub/
"""
import logging

import voluptuous as vol

from homeassistant.components.discovery import SERVICE_AUTOHUB
from homeassistant.const import (CONF_HOST, CONF_PORT, EVENT_HOMEASSISTANT_STOP)
from homeassistant.helpers import discovery
from homeassistant.helpers import config_validation as cv

REQUIREMENTS = ['pyautohub==0.1.0']

_LOGGER = logging.getLogger(__name__)

AUTOHUB = None
DISCOVER_LIGHTS = "autohub.light"
DOMAIN = "autohub"

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_PORT): cv.string,
		vol.Optional('devices',{}): dict
    })
}, extra = vol.ALLOW_EXTRA)

# Mapping from Wemo model_name to service.
AUTOHUB_MODEL_DISPATCH = {
}

AUTOHUB_SERVICE_DISPATCH = {
    DISCOVER_LIGHTS: 'light',
}

AUTOHUBWS = None

def setup(hass, config):
    """Setup Autohub Hub component.
    This will automatically import associated lights.
    if not validate_config(
            config,
            {DOMAIN: [CONF_USERNAME, CONF_PASSWORD, CONF_API_KEY]},
            _LOGGER):
        return False
    """
    import pyautohub
	
    conf = config[DOMAIN]
    host = conf.get(CONF_HOST)
    port = conf.get(CONF_PORT)

    def OnDeviceAdded(device):
        """
		   Registered with pyautohub.AutohubWS as callback function
		   Invoked by AutohubWS
        """
        _LOGGER.info("Device Added!")
        config_autohub = config.get("autohub")
        kDevices = config_autohub.get("devices", {})
        if device.device_address_ in kDevices:
            device.device_name_ = kDevices[device.device_address_].get("name", device.device_name_)
        discovery_info = (device.device_address_, device.device_name_)
        discovery.discover(hass, SERVICE_AUTOHUB, discovery_info)

    def autohub_stop(event):
        _LOGGER.info("Shutting down Authub sockets")
        autohub_object.stop()

    def discovery_dispatch(service, device):
        """ 
          Dispatcher for autohub discovery events. 
          Invoked by HomeAssistant, triggered by OnDeviceAdded		
		"""
        _LOGGER.info("Discovery Dispatch!")
        device_address, device_name = device

        service = DISCOVER_LIGHTS
        component = AUTOHUB_SERVICE_DISPATCH.get(service)

        discovery.load_platform(hass, component, DOMAIN, device, config)

        discovery.discover(hass, service, device, component, config)

    autohub_object = pyautohub.AutohubWS(host, port, _LOGGER)

    # register callback handler with pyautohub
    autohub_object.on_device_added(OnDeviceAdded)

    hass.bus.listen_once(EVENT_HOMEASSISTANT_STOP, autohub_stop)

    discovery.listen(hass, SERVICE_AUTOHUB, discovery_dispatch)
	
    autohub_object.start()
    hass.data['autohub_object'] = autohub_object


    return True
