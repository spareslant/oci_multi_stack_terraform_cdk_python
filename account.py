#! /usr/bin/env python

import configparser
import os
import pprint

tenancy_profile_name = "DEFAULT"

def get_local_oci_config_value(profile_name, config_field):
    c = configparser.ConfigParser()
    c.read(os.environ['HOME'] + '/.oci/config')
    return c[profile_name][config_field]


if __name__ == '__main__':
    print(f"root_compartment_id = {get_local_oci_config_value(tenancy_profile_name, 'tenancy')}")
