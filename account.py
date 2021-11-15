#! /usr/bin/env python

import configparser
import os, io

tenancy_profile_name = "DEFAULT"

def get_local_oci_config_value(profile_name, config_field):
    c = configparser.ConfigParser()
    c.read(os.environ['HOME'] + '/.oci/config')
    return c[profile_name][config_field]

def write_oci_config_file(user, oci_user_creds):
    oci_user_config_file = os.environ['HOME'] + '/.oci/config'
    c = configparser.ConfigParser()
    c.read(oci_user_config_file)

    c[user] = oci_user_creds
    with io.StringIO() as oci_config_string:
        c.write(oci_config_string)
        oci_config = oci_config_string.getvalue()
    return oci_config

if __name__ == '__main__':
    print(f"root_compartment_id = {get_local_oci_config_value(tenancy_profile_name, 'tenancy')}")
