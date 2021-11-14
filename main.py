#!/usr/bin/env python
from cdktf import App

from privileged_oci import PrivilegedUser
#from network_oci import Network

app = App()
PrivilegedUser(app, "create_privileged_user")
#Network(app, "create_network")

app.synth()
