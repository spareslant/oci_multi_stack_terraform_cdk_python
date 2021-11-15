---
title: "Multiple Stacks TerraformCDK Python Oracle Cloud Infrastructure (OCI)"
date: 2021-11-14T13:52:39Z
draft: true
---

# Introduction
We will be creating a public facing VM in Oracle Cloud Infrastructure (OCI) using terraform cdk toolkit. We will be writing terraform code in `Python` and we will be using `terraform stacks`. 

## What will be done in terraform stack
* We will create a stack `create_privileged_user` to create a privileged user
* We will create a stack `create_networking` to create `VCN` and `subnets`
* We will create a stack `create_vm` to create a internet facing VM


## Development Environment
* OS used: MacOS Monterey (12.0.1)
* Python version used: 3.10.0
* Package manager: brew
* Pipenv: We will be using `pipenv`

**Note:** `pipenv` creates python virtual environment behind the scenes. 

### Install `python` via `pyenv`
```bash
brew install pyenv
pyenv install 3.10.0
pyenv global 3.10.0
```

### Install `pipenv`
```bash
pip install pipenv
```

### Install `terraform` using tfenv
```bash
brew install tfenv
tfenv install 1.0.11
tfenv use 1.0.11
```

### Install `node.js` via `nvm`
```bash
brew install nvm
nvm install --lts
nvm use --lts
$ node --version
v16.13.0
nvm alias default 16.13.0
```

### Install `cdktf-cli`
```bash
npm install --global cdktf-cli

$ cdktf --version
0.7.0
```

## Prepare coding directory

### Initiate `cdktf` project
```bash
mkdir oci_multi_stack_terraform_cdk_python
cd oci_multi_stack_terraform_cdk_python
cdktf init --template="python" --local
```
Above command will initiate a `pipenv`. To see the location of virtualenv that pipenv created run this command ` pipenv --venv`.

### Install required packages (`oci sdk` and others) using `pipenv`
```bash
pipenv install pycryptodome oci oci-cli
```

#### Files in current direcotry
```bash
cdktf.json  help  main.py  Pipfile  Pipfile.lock
```

### Download OCI terraform modules libraries
#### Add terraform provider information in `cdktf.json` file
```json
{
  "language": "python",
  "app": "pipenv run python main.py",
  "projectId": "4fcb470a-7301-4f20-b90d-94dbd6efdc48",
  "terraformProviders": [
    "oci@~> 4.52.0",
    "cloudinit@~> 2.2.0",
    "tls@~> 3.1.0",
    "local@~> 2.1.0",
    "external@~> 2.1.0"
  ],
  "terraformModules": [],
  "codeMakerOutput": "imports",
  "context": {
    "excludeStackIdFromLogicalIds": "true",
"allowSepCharsInLogicalIds": "true"
  }
}
```

#### Get terraform libraries
```bash
cdktf get
```

#### Files in current direcotry
```bash
$ /bin/ls
Pipfile                 cdktf.json              imports                 package-lock.json
Pipfile.lock            help                    main.py                 package.json
```

## Prepare OCI environment
* You need an `OCI` account. Its free. SignUp at https://cloud.oracle.com. This sign-up account is called `Tenancy Admin` account.
* Login to this `Tenancy Admin` account. Make sure you have selected `Oracle Cloud Infrastructure Direct Sign-In` option on the login page.
* click hamburger icon on the top-left corner 
    * click `Identity & Security`
    * click `users`
    * click your email ID here (the one you used for sign-up)
    * click `API Keys`
    * click `Add API Key`
    * select `Generate API Key Pair`
    * click `Download private key`
    * click `Add` button
    * Copy the content in `Configuration File Preview` and save it. We need it later on.
    * click `close`

### Configure Tenancy Admin account to access OCI via APIs
You can run `oci setup config` command to setup the oci config. But we will be following direct manual method as we already have config saved in previous step when we prepared the oci envrionment.
```bash
mkdir ~/.oci
chmod g-rwx,o-rwx /root/.oci

ls -ld /root/.oci/
drwx------ 2 root root 4096 Sep 20 23:36 /root/.oci/

touch ~/.oci/tenancyAdmin_private_api_key.pem
vim ~/.oci/tenancyAdmin_private_api_key.pem
```
Paste the contents from file that you downloaded during the step `download private key` above in file `~/.oci/tenancyAdmin_private_api_key.pem`

```bash
chmod 600 ~/.oci/tenancyAdmin_private_api_key.pem
touch ~/.oci/config
chmod 600 ~/.oci/config
vim  ~/.oci/config
```
Paste the contents from file that you saved during the step `Configuration file preview` above in file `~/.oci/config`

Contents of `~/.oci/config` will be similar to the following.
```ini
[DEFAULT]
user=ocid1.user.oc1..<a very long string>
fingerprint=xx:yy:11:22:33:44:d4:56:b6:67:89:b7:b1:7f:4f:7a
tenancy=ocid1.tenancy.oc1..<a very long string>
region=uk-london-1
key_file=~/.oci/tenancyAdmin_private_api_key.pem
```
Please note `key_file=` above.

### Verify connectivity to OCI
```bash
cd oci_multi_stack_terraform_cdk_python
pipenv shell
oci iam user list
exit
```
Above command (`oci iam user list`) must run successfully.

## Start Coding

### Create a helper library `account.py` with following contents
```bash
touch account.py
```

##### `account.py` contents
```python
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
```

#### update `main.py` with following contents

##### `main.py` contents
```python
#!/usr/bin/env python
from cdktf import App

from privileged_oci import PrivilegedUser
#from network_oci import Network

app = App()
privlege_user = PrivilegedUser(app, "create_privileged_user")
privlege_user.message()
#Network(app, "create_network")

app.synth()
```

#### Create a new file `privileged_oci.py` for `create_privileged_user` stack
```bash
touch privileged_oci.py
```

##### `privileged_oci.py` contents
```python
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
oci_config_dir=f"{os.environ['HOME']}/.oci"
priv_user_private_key_file=f"{oci_config_dir}/{priv_user}_private_key.pem"
priv_user_public_key_file=f"{oci_config_dir}/{priv_user}_public_key.pem"
new_oci_config_file=f"{oci_config_dir}/config.by.terraform"


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
                algorithm="RSA")
        
        comp = IdentityCompartment(self, f"{compartment}_compartment",
                name=compartment,
                description=f"{compartment} compartment",
                enable_delete=True,
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

        TerraformOutput(self, f"{compartment}_id",
                value=comp.id)
        TerraformOutput(self, f"{priv_user}_id",
                value=user.id)
        TerraformOutput(self, f"{priv_group}_id",
                value=group.id)
        TerraformOutput(self, f"{priv_user}_private_key",
                value=api_keys.private_key_pem,
                sensitive=True)
        TerraformOutput(self, f"{priv_user}_fingerprint",
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
        priv_user_oci_creds["key_file"] = f"~/.oci/{priv_user}_private_key.pem"

        # We can't write ~/.oci/config file without File terraform resource, because
        # used.id and user_api_key.fingerprint etc will be evaluated only during the
        # File resource call.
        # If we use python file write functions here, it gets executed very first thing
        # in terraform and user.id and user_api_key.fingerprint would NOT have been
        # evaluated.
        File(self, "oci_config_file",
                content=write_oci_config_file(priv_user, priv_user_oci_creds),
                filename=new_oci_config_file)

    def message(self):
        print(f"WARNING!!!!!!!!: Terraform might have written a new oci config file at {new_oci_config_file}. Terraform will manage this file automatically.")
```
