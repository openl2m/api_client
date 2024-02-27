#!/usr/bin/env bash
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
# This implements a Python 3 script with some examples using the class for OpenL2M's REST API.
#
import os
import pprint
import sys

import openl2m

# set these fields per your own environment:
# you can export environment variables OPENL2M_URL and OPENL2M_TOKEN
url = os.getenv("OPENL2M_URL")
token = os.getenv("OPENL2M_TOKEN")

# or you can hardcode or enter on the command line:
if not url or not token:
    url = input("Enter full OpenL2M url: ")
    token = input("Enter you token: ")


# get an object to talk to the server:
server = openl2m.Server(url=url, token=token)

#
# NOTE: once you have the server (or device) object,
# after each successful call (test on return value!),
# you can access the data retrieved
# by calling the server.response.json() function!
# you can use the pprint library to read the format.
#

# get more debugging output, 1 will show some progress steps,
# 2 shows full response data from requests (very verbose!)
server.set_verbose(verbose=1)

# if you have SSL certs that are not "recognized" (self-signed, CA-certs unavailable, etc)
# then turn off SSL verification:
server.set_verify(verify=False)

#########################
# Get some server info: #
#########################

val = server.stats()
if val:
    # success, get the response data:
    stats = server.response.json()
    pprint.pprint(stats)
else:
    # you can now parse the status code: if -1, an trapped error occured,
    # else the server returned an error:
    #
    # Note: this is the same for the device.get() calls below, but
    # code is not replicated for simplicity!
    #
    print(f"Error: status code = {server.status}")
    if server.status == -1:
        print(server.error)
    sys.exit()

val = server.environment()
pprint.pprint(server.response.json())

########################
# Get list of devices: #
########################

# get the list of accessible devices on the server
val = server.devices()
if val:
    my_devices = server.response.json()
    # pprint.pprint(my_devices)
# else: ... see above.

# you can now parse your devices dict(). There is a "groups" entry, which is indexed by group id.
# Each group contains a dict() with group info. The 'members' dict() of a group is indexed
# by switch or device id, and contains device or switch information.

# get the device information for device/switch id "272", in group "9":
device1_url = my_devices["groups"]["9"]["members"]["272"]["url"]
print(f"Accessing device 1 at {device1_url}")

# and another one:
device2_url = my_devices["groups"]["4"]["members"]["839"]["url"]
print(f"Accessing device 2 at {device2_url}")

#####################
# Reading a device: #
#####################

#
# NOTE: if you know the URL to a device, you can call it directly!
# without the need to go through the server.devices() call as shown above.
#

# get objects for these devices:
device1 = server.device(device_url=device1_url)
device2 = server.device(device_url=device2_url)

# and read the devices:
if device1.get():  # interface info only
    info1 = device1.response.json()
    # pprint.pprint(info1)
if device2.get(view="details"):  # interface and eth/arp/lldp data
    info2 = device2.response.json()
    # pprint.pprint(info2)

# the return dict() has several entries, "interfaces", "switch", "vlans"
# show the hostname:
print(f"Hostname 1: {info1['switch']['hostname']}")
# show the interfaces:
for interface in info1["interfaces"]:
    print(f"id={interface['id']}: {interface['name']} - {interface['description']}")

# show the vlans:
print(f"Hostname 2: {info2['switch']['hostname']}")
# pprint.pprint(info2['vlans'])
for vlan in info2["vlans"].values():
    print(f"id={vlan['id']}: {vlan['name']}")

###################
# Making changes: #
###################

#
# set the description for interface GigE1/0/20, which has id="20".
# Note: interface ID's are str() values !!!
#
val = device1.set_interface_description(
    interface_id="20", description="New description - 1"
)
# pprint.pprint(val)
# if this fails, there typically is a reason returned:
if val:
    print("SUCCESS set_interface_description")
    # on success, there typically is a "result" returned:
    pprint.pprint(device2.response.json())
else:
    if device1.status == -1:
        print(f"ERROR set_interface_description:\n{device1.error}")
    else:
        # if this fails, there typically is a "reason" returned:
        print(
            f"ERROR set_interface_description:\nFailed with return code {device1.response.status_code}: {device1.response.json().get('reason', 'No reason found!')}"
        )


#
# set the untagged vlan on interface GigE1/0/20 to 999
#
val = device1.set_interface_vlan(interface_id="20", vlan_id=888)
if val:
    print("SUCCESS set_interface_vlan")
    # on success, there typically is a "result" returned:
    pprint.pprint(device2.response.json())
else:
    if device1.status == -1:
        print(f"ERROR set_interface_vlan:\n{device1.error}")
    else:
        # if this fails, there typically is a "reason" returned:
        print(
            f"ERROR set_interface_vlan:\nFailed with return code {device1.response.status_code}: {device1.response.json().get('reason', 'No reason found!')}"
        )


#
# enable or disable PoE on an interface
#
val = device2.set_interface_poe_state(interface_id="10", poe_state=False)
pprint.pprint(val)
if val:
    print("SUCCESS set_interface_state")
    # on success, there typically is a "result" returned:
    pprint.pprint(device2.response.json())
else:
    if device1.status == -1:
        print(f"ERROR set_interface_poe_state:\n{device1.error}")
    else:
        # if this fails, there typically is a "reason" returned:
        print(
            f"ERROR set_interface_poe_state:\nFailed with return code {device2.response.status_code}: {device2.response.json().get('reason', 'No reason found!')}"
        )


# enable or disable an interface
val = device2.set_interface_state(interface_id="10", state=False)
if val:
    print("SUCCESS set_interface_state")
    # on success, there typically is a "result" returned:
    pprint.pprint(device2.response.json())
else:
    if device1.status == -1:
        print(f"ERROR set_interface_state:\n{device1.error}")
    else:
        # if this fails, there typically is a "reason" returned:
        print(
            f"ERROR set_interface_state:\nFailed with return code {device2.response.status_code}: {device2.response.json().get('reason', 'No reason found!')}"
        )
