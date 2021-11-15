from constructs import Construct
from cdktf import TerraformStack
from imports.oci import (
    OciProvider,
    CoreVcn
    )
from local_utils import (
    get_local_oci_config_value)

import os

profile_name = "cdk-user"
oci_config_file = f"{os.environ['HOME']}/.oci/config.{profile_name}"
fingerprint = get_local_oci_config_value(profile_name, "fingerprint", oci_config_file)
private_key_path = get_local_oci_config_value(profile_name, "key_file", oci_config_file)
region = get_local_oci_config_value(profile_name, "region", oci_config_file)
tenancy_ocid = get_local_oci_config_value(profile_name, "tenancy", oci_config_file)
user_ocid = get_local_oci_config_value(profile_name, "user", oci_config_file)

class Network(TerraformStack):
    def __init__(self, scope: Construct, ns: str, desired_compartment_id , remote_state):
        super().__init__(scope, ns)

        terraform_state = remote_state(self, ns)
        
        comp_id = terraform_state.get_string(desired_compartment_id)
        # define resources here
        OciProvider(self, "oci",
                fingerprint=fingerprint,
                private_key_path=private_key_path,
                region=region,
                tenancy_ocid=tenancy_ocid,
                user_ocid=user_ocid)

        CoreVcn(self, "oci_vcn",
                cidr_block="10.0.0.0/16",
                display_name="OCI_VCN",
                compartment_id=comp_id)
