from constructs import Construct, Node
from cdktf import TerraformStack, TerraformOutput
from imports.tls import TlsProvider, PrivateKey
from imports.local import LocalProvider, File
from imports.oci import (
    OciProvider,
    CoreInstance,
    CoreInstanceCreateVnicDetails,
    DataOciIdentityAvailabilityDomain
    )

from local_utils import (
        user_creds)

import os
network_prefix = "cdk"
profile_name = "cdk-user"
oci_config_file = f"{os.environ['HOME']}/.oci/config.{profile_name}"

class VmInstance(TerraformStack):
    def __init__(self, scope: Construct, ns: str,
            priv_compartment,
            public_subnet,
            user_comp_remote_state,
            network_remote_state):
        super().__init__(scope, ns)

        (fingerprint,
            private_key_path,
            region,
            tenancy_ocid,
            user_ocid) = user_creds(profile_name, oci_config_file)

        u_terraform_state = user_comp_remote_state(self, ns)
        n_terraform_state = network_remote_state(self, ns + "_network")
        priv_compartment_id = u_terraform_state.get_string(priv_compartment)
        public_subnet_id = n_terraform_state.get_string(public_subnet)

        image_id = "ocid1.image.oc1.uk-london-1.aaaaaaaa7p27563e2wyhmn533gp7g3wbohrhjacsy3r5rpujyr6n6atqppuq"

        # define resources here
        OciProvider(self, "oci",
                fingerprint=fingerprint,
                private_key_path=private_key_path,
                region=region,
                tenancy_ocid=tenancy_ocid,
                user_ocid=user_ocid)

        TlsProvider(self, "oci_tls")

        LocalProvider(self, "oci_local_provider")

        avail_domain = DataOciIdentityAvailabilityDomain(self, f"{network_prefix}_availability_domain",
                compartment_id=priv_compartment_id,
                ad_number=1)

        vm_keys = PrivateKey(self, f"{network_prefix}_vm_keys",
                algorithm="RSA")

        vm = CoreInstance(self, f"{network_prefix}_vm_instance",
                compartment_id=priv_compartment_id,
                shape="VM.Standard.E2.1.Micro",
                availability_domain=avail_domain.name,
                image=image_id,
                create_vnic_details=CoreInstanceCreateVnicDetails(
                        subnet_id=public_subnet_id),
                metadata={
                    "ssh_authorized_keys": vm_keys.public_key_openssh,
                    }
                    
                )
        TerraformOutput(self, f"{network_prefix}_vm_public_ip",
                value=vm.public_ip)

        File(self, f"{network_prefix}_vm_private_key_file",
                content=vm_keys.private_key_pem,
                filename=f"{os.path.dirname(os.path.abspath(__file__))}/keys/private_key.pem",
                file_permission="0600")    


    def name(self):
        return Node.of(self).id

