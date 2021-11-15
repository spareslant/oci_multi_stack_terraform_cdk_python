from constructs import Construct
from cdktf import TerraformStack, TerraformOutput
from imports.oci import (
    OciProvider,
    IdentityCompartment
    )
from account import tenancy_profile_name, get_local_oci_config_value

class Network(TerraformStack):
    def __init__(self, scope: Construct, ns: str):
        super().__init__(scope, ns)

        # define resources here
        tenancyID = get_local_oci_config_value(tenancy_profile_name, "tenancy")
        OciProvider(self, "oci",
                config_file_profile=tenancy_profile_name)
        
        comp = IdentityCompartment(self, "network",
                name="network",
                description="network compartment",
                compartment_id=tenancyID)

        TerraformOutput(self, "network_compartment_id",
                value=comp.id)