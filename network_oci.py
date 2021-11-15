from constructs import Construct
from cdktf import TerraformStack, TerraformOutput
from imports.oci import (
    OciProvider,
    )
from account import tenancy_profile_name

class Network(TerraformStack):
    def __init__(self, scope: Construct, ns: str):
        super().__init__(scope, ns)

        # define resources here
        OciProvider(self, "oci",
                config_file_profile=tenancy_profile_name)
        
