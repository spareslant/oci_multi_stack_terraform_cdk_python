#!/usr/bin/env python
from cdktf import App, DataTerraformRemoteStateLocal
from constructs import Construct
from cdktf import TerraformStack

from privUserAndCompartment import PrivilegedUser
from network import Network
from systemsAndApps import VmInstance
import os

app = App()

class RunStack(TerraformStack):

    def __init__(self, scope: Construct, ns: str):
        super().__init__(scope, ns)

        priv_user = PrivilegedUser(self, "priv_user_compartment")
        priv_user.message()

        def user_comp_remote_state(scope, id):
            state_file=f"{os.path.dirname(os.path.abspath(__file__))}/terraform.{priv_user.name()}.tfstate"
            return DataTerraformRemoteStateLocal(scope, id,
                path=state_file)

        if os.path.exists(f"{os.environ['HOME']}/.oci/config.cdk-user"):

            network = Network(app, "network",
                    priv_user.priv_compartment,
                    user_comp_remote_state)

            def network_remote_state(scope, id):
                state_file=f"{os.path.dirname(os.path.abspath(__file__))}/terraform.{network.name()}.tfstate"
                return DataTerraformRemoteStateLocal(scope, id,
                    path=state_file)

            VmInstance(self, "vm_instance",
                   priv_user.priv_compartment,
                   network.network_public_subnet,
                   user_comp_remote_state,
                   network_remote_state) 


RunStack(app, "dummy_hosting_stack")
app.synth()
