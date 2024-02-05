#
# This file is part of Open Layer 2 Management (OpenL2M).
#
# OpenL2M is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License version 3 as published by
# the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.  You should have received a copy of the GNU General Public
# License along with OpenL2M. If not, see <http://www.gnu.org/licenses/>.
#
#
# This implements a Python 3 client class for OpenL2M's REST API.
#
import json
import requests


class Server:
    """Object that implements the OpenL2M client side of the REST API on the server"""

    def __init__(self, url, token):
        self.url = url      # the base URL where the REST queries will be made.
        self.token = token  # the API token
        self.headers =  {
            "Authorization": f"Token {token}",
            "Content-Type": "application/json",     # we use JSON posting format.
        }
        self.status = 0         # will contain the HTTP response status, or -1 if Exception caught.
        self.error = ""         # will contain string value of last caught error.
        self.response = False   # will contain the response from the last .get() or .post()
        self.verbose = 0        # debug output level. If > 0, will print debug info to stdout
        self.verify = True      # verify SSL cert chain ?

    def set_verify(self, verify):
        """
        Enable or disable SSL verification.

        Args:
            verify (bool): Verify SSL (True) or not (False).

        Returns:
            n/a
        """
        self.verify = verify

    def set_verbose(self, verbose):
        """
        Set the verbosity level.

        Args:
            verbose (int): the verbosity level.

        Returns:
            n/a
        """
        self.verbose = verbose

    def debug(self, text, level=1):
        """Show debug text if verbosity is at or above level given.

        Args:
            text (str): text to print to output.
            level (int): the level at which to print the output.

        Returns:
            n/a
        """
        if self.verbose >= level:
            print(f"DEBUG{level}: {text}")

    def execute(self, endpoint, data=False):
        """Execute a GET or a POST, depending on data given (POST) or not (GET).
        Will set self.response, self.status and self.error as applicable.

        Args:
            endpoint (str): the API endpoint, to add to the host url.
            data (dict):    if given, a dictionary of POST data that will be sent as JSON.

        Returns:
            bool:     True if successfull, False if not.
        """
        self.debug(f"execute(endpoint={endpoint})")
        self.status = 0
        self.error = ""
        self.response=False
        try:
            url = f"{self.url}{endpoint}"
            if data:
                self.debug(f"  POST: {url}")
                response = requests.post(url=url, json=data, headers=self.headers, verify=self.verify)
            else:
                self.debug(f"  GET: {url}")
                response = requests.get(url=f"{self.url}{endpoint}", headers=self.headers, verify=self.verify)
            self.debug(f"  Response code {response.status_code}")
            self.debug(f"  Body:\n{response.content}\n", level=2)
        except Exception as e:
            self.debug(f"  ERROR: {e}")
            self.status = -1
            self.error = f"{e}"
            return False
        self.response = response
        self.status = response.status_code
        if response.status_code != requests.codes.ok:   # HTTP returned error code!
            return False
        return True

    def devices(self):
        """Get the list of devices available to this token.

        Args:
            n/a

        Returns:
            bool:     True if successfull, False if not.
        """
        self.debug("devices()")
        return self.execute(endpoint="api/switches/")

    def menu(self):
        return self.devices()

    def switches(self):
        return self.devices()

    def device(self, device_url):
        """Get an object to a device.

        Args:
            device_url (str): proper URL path to this device, likely retrieved from get_menu().

        Returns:
            bool:     True if successfull, False if not.
        """
        self.debug(f"device(device_url={device_url})")

        return Device(device_url=device_url, token=self.token)

    def stats(self):
        """Get usage statistics of the OpenL2M server.

        Args:
            n/a

        Returns:
            bool:     True if successfull, False if not.
        """
        self.debug("stats()")
        return self.execute(endpoint="api/stats/")

    def environment(self):
        """Get information about the runtime environment of the OpenL2M server.

        Args:
            n/a

        Returns:
            bool:     True if successfull, False if not.
        """
        self.debug("environment()")
        return self.execute(endpoint="api/environment/")


#
# Device() implements access to a specific device
#

class Device(Server):
    """ This class allow access to a specific device
        that is accessible/manageable from the OpenL2M Server.
    """

    def __init__(self, device_url, token):
        super().__init__(url=device_url, token=token)

    def get(self, view=""):
        """Get the device/switch data for the current switch.

        args:
            view (str): if "details" API will return the ARP/Ethernet/LLDP details data.
                any other value will return regular interface data.

        Returns:
            bool:     True if successfull, False if not.
        """
        self.debug(f"read_switch(view={view})")
        endpoint = ""
        if view == "details":
            endpoint = "details/"
        else:
            endpoint = ""
        return self.execute(endpoint=endpoint)

    def set_interface_state(self, interface_id, state):
        """Set the interface state.

        Args:
            description (str): the new description for the given interface.
            state (bool): True to enable or False to disable the requested interface.

        Returns:
            bool:     True if successfull, False if not.
        """
        self.debug(f"set_interface_state(interface_id={interface_id}, state={state})")

        self.error_string = ""
        if state:
            data = { 'state': "on" }
        else:
            data = { 'state': "off" }
        endpoint = f"interface/{interface_id}/state/"
        return self.execute(endpoint=endpoint, data=data)


    def set_interface_poe_state(self, interface_id, poe_state):
        """Set the interface PoE status.

        Args:
            interface_id (str): the identifier of the requested interface, as retrieved from read_switch().
            poe_state (bool): True to enable or False to disable PoE on the requested interface.

        Returns:
            bool:     True if successfull, False if not.
        """
        self.debug(f"set_interface_poe_status(interface_id={interface_id}, poe_state={poe_state})")

        self.error_string = ""
        data = { 'poe_state': poe_state }
        endpoint = f"interface/{interface_id}/poe_state/"
        return self.execute(endpoint=endpoint, data=data)

    def set_interface_description(self, interface_id, description):
        """Set the interface description.

        Args:
            interface_id (str): the identifier of the requested interface, as retrieved from read_switch().
            description (str): the new description for the given interface.

        Returns:
            bool:     True if successfull, False if not.
        """
        self.debug(f"set_interface_description(interface_id={interface_id}, description={description})")

        data = { 'description': description }
        endpoint = f"interface/{interface_id}/description/"
        return self.execute(endpoint=endpoint, data=data)

    def set_interface_vlan(self, interface_id, vlan_id):
        """Set the interface untagged vlan id.

        Args:
            interface_id (str): the identifier of the requested interface, as retrieved from read_switch().
            vlan_id (int): the new untagged vlan id.

        Returns:
            bool:     True if successfull, False if not.
        """
        self.debug(f"set_interface_vlan(interface_id={interface_id}, vlan_id={vlan_id})")

        data = { 'vlan': vlan_id }
        endpoint = f"interface/{interface_id}/vlan/"
        return self.execute(endpoint=endpoint, data=data)
