#!/usr/bin/env python
from cdktf import App

from privileged_oci import PrivilegedUser
#from network_oci import Network

app = App()
privlege_user = PrivilegedUser(app, "create_privileged_user")
privlege_user.message()
#Network(app, "create_network")

app.synth()
