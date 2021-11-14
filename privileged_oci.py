from constructs import Construct
from cdktf import TerraformStack, TerraformOutput
from imports.tls import TlsProvider, PrivateKey
from imports.local import LocalProvider, File
from imports.oci import (
    OciProvider,
    IdentityCompartment,
    IdentityUser,
    IdentityGroup,
    IdentityUserGroupMembership,
    IdentityPolicy,
    IdentityApiKey
    )
from account import (
    tenancy_profile_name,
    get_local_oci_config_value,
    write_oci_config_file)

import os

compartment="CDK"
priv_user="cdk-user"
priv_group="cdk-group"
group_policy_1=f"Allow group {priv_group} to manage all-resources in compartment {compartment}"
priv_user_private_key_file=f"{os.environ['HOME']}/.oci/{priv_user}_private_key.pem"
priv_user_public_key_file=f"{os.environ['HOME']}/.oci/{priv_user}_public_key.pem"

class PrivilegedUser(TerraformStack):
    def __init__(self, scope: Construct, ns: str):
        super().__init__(scope, ns)

        # define resources here
        
        tenancyID = get_local_oci_config_value(tenancy_profile_name, "tenancy")
        region = get_local_oci_config_value(tenancy_profile_name, "region")
        OciProvider(self, "oci",
                config_file_profile=tenancy_profile_name)

        TlsProvider(self, "oci_tls")

        LocalProvider(self, "oci_local_provider")

        api_keys = PrivateKey(self, f"{priv_user}_keys",
                algorithm="rsa_bits")
        
        comp = IdentityCompartment(self, f"{compartment}_compartment",
                name=compartment,
                description=f"{compartment} compartment",
                compartment_id=tenancyID)
        user = IdentityUser(self, f"{priv_user}",
                name=priv_user,
                description=f"{priv_user} user",
                compartment_id=tenancyID)
        group = IdentityGroup(self, f"{priv_group}",
                name=priv_group,
                description=f"{priv_group} group",
                compartment_id=tenancyID)
        IdentityUserGroupMembership(self,
                f"{priv_user}_{priv_group}_membership",
                group_id=group.id,
                user_id=user.id)
        IdentityPolicy(self, f"{priv_group}_policy",
                name=f"{priv_group}_policy",
                description=f"{priv_group} policies",
                compartment_id=comp.id,
                statements=[
                   group_policy_1
                ])
        user_api_key = IdentityApiKey(self, f"{priv_user}_api_keys",
                user_id=user.id,
                key_value=api_keys.public_key_pem)

        TerraformOutput(self, "f{compartment}_id",
                value=comp.id)
        TerraformOutput(self, "f{priv_user}_id",
                value=user.id)
        TerraformOutput(self, "f{priv_group}_id",
                value=group.id)
        TerraformOutput(self, "f{priv_user}_private_key",
                value=api_keys.private_key_pem,
                sensitive=True)
        TerraformOutput(self, "f{priv_user}_fingerprint",
                value=user_api_key.fingerprint)


        File(self, f"{priv_user}_private_key_file",
                content=api_keys.private_key_pem,
                filename=priv_user_private_key_file)    
        File(self, f"{priv_user}_public_key_file",
                content=api_keys.public_key_pem,
                filename=priv_user_public_key_file)    

        priv_user_oci_creds = {}
        priv_user_oci_creds["user"] = user.id
        priv_user_oci_creds["fingerprint"] = user_api_key.fingerprint
        priv_user_oci_creds["tenancy"] = tenancyID
        priv_user_oci_creds["region"] = region
        priv_user_oci_creds["key_file"] = priv_user_private_key_file

        write_oci_config_file(priv_user, priv_user_oci_creds)
