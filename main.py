#!/usr/bin/env python
from cdktf import App, DataTerraformRemoteStateLocal
from constructs import Construct
from cdktf import TerraformStack

from privileged_oci import PrivilegedUser
from network_oci import Network
import os

app = App()

class RunStack(TerraformStack):

    def __init__(self, scope: Construct, ns: str):
        super().__init__(scope, ns)
        privlege_user = PrivilegedUser(self, "create_privileged_user")
        privlege_user.message()

        def create_remote_state(scope, id):
            return DataTerraformRemoteStateLocal(scope, id,
                path=f"{os.path.dirname(os.path.abspath(__file__))}/terraform.{privlege_user.name()}.tfstate")

        Network(app, "create_network", privlege_user.desired_comp_id, create_remote_state)

RunStack(app, "run_all_stacks")
app.synth()
