from constructs import Construct
from cdktf import TerraformStack
from imports.oci import (
    OciProvider,
    CoreVcn,
	CoreSubnet,
	CoreDhcpOptions,
	CoreInternetGateway,
	CoreInternetGateway,
	CoreRouteTable,
	CoreDhcpOptionsOptions,
	CoreRouteTableRouteRules,
	CoreRouteTableAttachment
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

        vcn = CoreVcn(self, f"{network_prefix}_vcn",
                cidr_block="10.0.0.0/16",
                display_name=f"{network_prefix}_vcn",
                compartment_id=priv_compartment_id)

        dhcp_options = CoreDhcpOptions(self, "DHCP_OPTIONS",
                compartment_id=priv_compartment_id,
                vcn_id=vcn.id,
                options=[
                    CoreDhcpOptionsOptions(
                    type="DomainNameServer",
                    server_type="VcnLocalPlusInternet")
                ]
            )

        public_subnet = CoreSubnet(self, f"{network_prefix}_public_subnet",
                cidr_block="10.0.0.0/24",
                vcn_id=vcn.id,
                compartment_id=priv_compartment_id,
                display_name="public_subnet",
                dhcp_options_id=dhcp_options.id)

        internet_gateway = CoreInternetGateway(self, f"{network_prefix}_internet_gateway",
                compartment_id=priv_compartment_id,
                vcn_id=vcn.id)

        route_table = CoreRouteTable(self, f"{network_prefix}_route_table",
                compartment_id=priv_compartment_id,
                vcn_id=vcn.id,
                route_rules=[
                    CoreRouteTableRouteRules(
                        network_entity_id=internet_gateway.id,
                        destination="0.0.0.0/0"
                        )
                    ])
        CoreRouteTableAttachment(self, f"{network_prefix}_route_attachment",
                subnet_id=public_subnet.id,
                route_table_id=route_table.id)

