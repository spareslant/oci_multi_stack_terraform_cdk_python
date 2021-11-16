from constructs import Construct
from cdktf import TerraformStack
from imports.oci import (
    OciProvider,
    CoreVcn
    )
from local_utils import (
    get_local_oci_config_value)

import os

network_prefix = "cdk"
profile_name = "cdk-user"
oci_config_file = f"{os.environ['HOME']}/.oci/config.{profile_name}"

class Network(TerraformStack):
    def __init__(self, scope: Construct, ns: str, priv_compartment , remote_state):
        super().__init__(scope, ns)

        fingerprint = get_local_oci_config_value(profile_name, "fingerprint", oci_config_file)
        private_key_path = get_local_oci_config_value(profile_name, "key_file", oci_config_file)
        region = get_local_oci_config_value(profile_name, "region", oci_config_file)
        tenancy_ocid = get_local_oci_config_value(profile_name, "tenancy", oci_config_file)
        user_ocid = get_local_oci_config_value(profile_name, "user", oci_config_file)

        terraform_state = remote_state(self, ns)
        priv_compartment_id = terraform_state.get_string(priv_compartment)

        # define resources here
        OciProvider(self, "oci",
                fingerprint=fingerprint,
                private_key_path=private_key_path,
                region=region,
                tenancy_ocid=tenancy_ocid,
                user_ocid=user_ocid)

        CoreVcn(self, f"{network_prefix}_vcn",
                cidr_block="10.0.0.0/16",
                display_name=f"{network_prefix}_vcn",
                compartment_id=priv_compartment_id)
