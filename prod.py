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
    pprint.pprint(my_devices)
