#!/usr/bin/env python
from cdktf import App, DataTerraformRemoteStateLocal
from constructs import Construct
from cdktf import TerraformStack

from privUserAndCompartment import PrivilegedUser
from network import Network
import os

app = App()

class RunStack(TerraformStack):

    def __init__(self, scope: Construct, ns: str):
        super().__init__(scope, ns)
        priv_user = PrivilegedUser(self, "create_priv_user_compartment")
        priv_user.message()

        def create_remote_state(scope, id):
            return DataTerraformRemoteStateLocal(scope, id,
                path=f"{os.path.dirname(os.path.abspath(__file__))}/terraform.{priv_user.name()}.tfstate")

        Network(app, "create_network", priv_user.priv_compartment, create_remote_state)

RunStack(app, "dummy_hosting_stack")
app.synth()
