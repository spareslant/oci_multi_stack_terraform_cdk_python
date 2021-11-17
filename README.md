---
title: "Multiple Stacks TerraformCDK Python Oracle Cloud Infrastructure (OCI)"
date: 2021-11-14T13:52:39Z
draft: true
---

# Introduction
We will be creating a public facing VM in Oracle Cloud Infrastructure (OCI) using terraform cdk toolkit. We will be writing terraform code in `Python` and we will be using `terraform stacks`. 


## What will be done in terraform stack
* We will create a stack `priv_user_compartment` to create a privileged user `cdk-user` and a compartment `CDK`. This user will have full admin rights in this compartment.
* We will create a stack `network` to create `VCN`, `subnets`, `internet gateway`, `dhcp options`, `route tables` etc. in above created `compartment`. This stack will use above created user's credentials (`cdk-user`) NOT tenancy admin credentials.
* We will create a stack `vm_instance` to create a internet facing VM in above created `VCN` and `compartment` and this stack uses above created user's credentials `cdk-user` to do so.
* Code will be passing information from one stack to another.


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

## Prepare coding directory (if starting from scratch)

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

## Prepare coding directory (if cloning the repo)

### Clone repo
```bash
git clone https://github.com/spareslant/oci_multi_stack_terraform_cdk_python.git
cd oci_multi_stack_terraform_cdk_python
```

### Install required pip modules using pipenv
```bash
pipenv sync
```

### Download OCI terraform modules libraries

#### Add terraform provider information in `cdktf.json` file
**Note:** No need for this step if using cloned repo as working directory.
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


## Prepare terraform code to execute
Populate following files with contents as mentioned in this git repo.

* `common.py`
* `main.py`
* `local_utils.py`
* `privUserAndCompartment.py`
* `network.py`
* `systemsAndApps.py`
* `cdktf.json`


## Deploy stacks

### list stacks
```
$ cdktf list

WARNING!!!!!!!!: Terraform might have written a new oci config file at /Users/gpal/.oci/config.cdk-user. Terraform will manage this file automatically.

Stack name                      Path
dummy_hosting_stack             cdktf.out/stacks/dummy_hosting_stack
priv_user_compartment           cdktf.out/stacks/priv_user_compartment
vm_instance                     cdktf.out/stacks/vm_instance
network                         cdktf.out/stacks/network
```
**Note:** Listing of stacks is not in order. You need to run the each stack separately. Hence if there is depencies among stacks then you need to remember the order of deployment and destruction of stacks.


### Deploy first stack `priv_user_compartment`
```
$ cdktf deploy priv_user_compartment --auto-approve

WARNING!!!!!!!!: Terraform might have written a new oci config file at ~/.oci/config.cdk-user. Terraform will manage this file automatically.

Deploying Stack: priv_user_compartment
Resources
 ✔ LOCAL_FILE           cdk-user_private_ke local_file.cdk-user_private_key_file
                        y_file
 ✔ LOCAL_FILE           cdk-user_public_key local_file.cdk-user_public_key_file
                        _file
 ✔ LOCAL_FILE           oci_config_file     local_file.oci_config_file
 ✔ OCI_IDENTITY_API_KEY cdk-user_api_keys   oci_identity_api_key.cdk-user_api_keys
 ✔ OCI_IDENTITY_COMPART CDK_compartment     oci_identity_compartment.CDK_compartmen
   MENT                                     t
 ✔ OCI_IDENTITY_GROUP   cdk-group           oci_identity_group.cdk-group
 ✔ OCI_IDENTITY_POLICY  cdk-group_policy    oci_identity_policy.cdk-group_policy
 ✔ OCI_IDENTITY_USER    cdk-user            oci_identity_user.cdk-user
 ✔ OCI_IDENTITY_USER_GR cdk-user_cdk-group_ oci_identity_user_group_membership.cdk-
   OUP_MEMBERSHIP       membership          user_cdk-group_membership
 ✔ TLS_PRIVATE_KEY      cdk-user_keys       tls_private_key.cdk-user_keys

Summary: 10 created, 0 updated, 0 destroyed.
```


### Deploy second stack `network`
```
$ cdktf deploy network --auto-approve


WARNING!!!!!!!!: Terraform might have written a new oci config file at ~/.oci/config.cdk-user. Terraform will manage this file automatically.

Deploying Stack: network
Resources
 ✔ OCI_CORE_ROUTE_TABLE cdk_route_table     oci_core_route_table.cdk_route_table
 ✔ OCI_CORE_ROUTE_TABLE cdk_route_attachmen oci_core_route_table_attachment.cdk_rou
   _ATTACHMENT          t                   te_attachment

Summary: 2 created, 0 updated, 0 destroyed.

```


### Deploy third stack `vm_instance`
```
$ cdktf deploy vm_instance --auto-approve


WARNING!!!!!!!!: Terraform might have written a new oci config file at ~/.oci/config.cdk-user. Terraform will manage this file automatically.

Deploying Stack: vm_instance
Resources
 ✔ LOCAL_FILE           cdk_vm_private_key_ local_file.cdk_vm_private_key_file
                        file
 ✔ OCI_CORE_INSTANCE    cdk_vm_instance     oci_core_instance.cdk_vm_instance
 ✔ TLS_PRIVATE_KEY      cdk_vm_keys         tls_private_key.cdk_vm_keys

Summary: 3 created, 0 updated, 0 destroyed.

Output: cdk_vm_public_ip = xxx.yyy.zzz.vvv
```

### destroy stacks (reverse order of deployment)
```bash
cdktf destroy vm_instance --auto-approve
cdktf destroy network --auto-approve
cdktf destroy priv_user_compartment --auto-approve
```

## How is passing information among stacks working

### In file `main.py`
```python
class RunStack(TerraformStack):

    def __init__(self, scope: Construct, ns: str):
        super().__init__(scope, ns)

        priv_user = PrivilegedUser(self, "priv_user_compartment")

        def user_comp_remote_state(scope, id):
            state_file=f"{os.path.dirname(os.path.abspath(__file__))}/terraform.{priv_user.name()}.tfstate"
            return DataTerraformRemoteStateLocal(scope, id,
                path=state_file)

        network = Network(app, "network",
                priv_user.priv_compartment,
                user_comp_remote_state)

        def network_remote_state(scope, id):
            state_file=f"{os.path.dirname(os.path.abspath(__file__))}/terraform.{network.name()}.tfstate"
            return DataTerraformRemoteStateLocal(scope, id,
                path=state_file)

        VmInstance(self, "vm_instance",
               priv_user.priv_compartment,
               network.network_public_subnet,
               user_comp_remote_state,
               network_remote_state) 
```

### In file `privUserAndCompartment.py`
```python
class PrivilegedUser(TerraformStack):

    priv_compartment = None

    def __init__(self, scope: Construct, ns: str):
        super().__init__(scope, ns)

        self.priv_compartment = TerraformOutput(self, f"{priv_compartment}_id",
                value=comp.id).friendly_unique_id
```

### In file `network.py`
```python
class Network(TerraformStack):

    network_public_subnet = None

    def __init__(self, scope: Construct, ns: str, priv_compartment , remote_state):
        super().__init__(scope, ns)

        terraform_state = remote_state(self, ns)
        priv_compartment_id = terraform_state.get_string(priv_compartment)
```

### In file `systemsAndApps.py`
```python
class VmInstance(TerraformStack):
    def __init__(self, scope: Construct, ns: str,
            priv_compartment,
            public_subnet,
            user_comp_remote_state,
            network_remote_state):
        super().__init__(scope, ns)

        u_terraform_state = user_comp_remote_state(self, ns)
        n_terraform_state = network_remote_state(self, ns + "_network")
        priv_compartment_id = u_terraform_state.get_string(priv_compartment)
        public_subnet_id = n_terraform_state.get_string(public_subnet)
```
