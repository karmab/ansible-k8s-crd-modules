# ansible-k8s-crd-modules

Provides access to the latest release of the k8s_crd module, allowing to create/delete crd generically. 

Include this role in a playbook, and any other plays, roles, and includes will have access to the modules.

The modules are found in the [library folder](./library)

## Requirements

- Ansible
- Kubernetes Python Module

## Installation and use

Use the Galaxy client to install the role:

```
$ ansible-galaxy install karmabs.k8s-crd-modules
```

Once installed, add it to a playbook:

```
---
- hosts: localhost
  remote_user: root
  roles:
    - role: karmab.k8s-crd-modules
      install_python_requirements: no
    - role: hello-underworld
```

Because the role is referenced, the `hello-underworld` role is able to make use of the k8s_crd module

### Module parameters

install_python_requirements
> Set to true, if you want kubernetes python module installed. Defaults to false. Will install via `pip`

## LOCAL TESTING

```
pip install kubernetes
set -x ANSIBLE_LIBRARY .
ansible-playbook tests/*yml
```

## TODO

- handles missing namespace in src file
- improve documentation

## License

Apache V2
