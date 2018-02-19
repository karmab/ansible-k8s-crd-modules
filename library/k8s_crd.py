#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
from kubernetes import client, config
import os
import yaml


DOCUMENTATION = '''
module: k8s_crd
short_description: Handles k8s crd
description:
    - Longer description of the module
    - Use name, namespace and src
version_added: "0.1"
author: "Karim Boumedhel, @karmab"
notes:
    - Details at https://github.com/karmab/ansible-k8s-crd-module
requirements:
    - kubernetes python package you can grab from pypi'''

EXAMPLES = '''
- name: Create a guitar
  k8s_crd:
    name: strato
    kind: guitar
    namespace: default
    domain: kool.karmalabs.local

- name: Create a guitar from a source file
  k8s_crd:
    name: strato
    kind: guitar
    namespace: default
    src: /tmp/stratocaster.yml

- name: Delete that guitar
  k8s_vm:
    name: strato
    kind: guitar
    namespace: default
    domain: kool.karmalabs.local
    state: absent
'''


def exists(crds, kind, version, domain, name, namespace):
    kind = kind.lower()
    allobjs = crds.list_cluster_custom_object(domain, version, '%ss' % kind)["items"]
    objs = [o for o in allobjs if o.get("metadata")["namespace"] == namespace and o.get("metadata")["name"] == name]
    result = True if objs else False
    return result


def main():
    argument_spec = {
        "state": {
            "default": "present",
            "choices": ['present', 'absent'],
            "type": 'str'
        },
        "name": {"required": False, "type": "str"},
        "domain": {"required": False, "type": "str"},
        "version": {"required": False, "type": "str"},
        "namespace": {"required": False, "type": "str"},
        "kind": {"required": True, "type": "str"},
        "src": {"required": False, "type": "str"},
    }
    module = AnsibleModule(argument_spec=argument_spec)
    config.load_kube_config()
    crds = client.CustomObjectsApi()
    name = module.params['name']
    namespace = module.params['namespace']
    src = module.params['src']
    version = module.params['version']
    domain = module.params['domain']
    kind = module.params['kind']
    state = module.params['state']
    if src is not None:
        if not os.path.exists(src):
            module.fail_json(msg='src %s not found' % src)
        else:
            with open(src) as data:
                try:
                    obj = yaml.load(data)
                except yaml.scanner.ScannerError as err:
                    module.fail_json(msg='Error parsing src file, got %s' % err)
            name = obj.get("metadata")["name"]
            kind = obj.get("kind").lower()
            namespace = obj.get("metadata")["namespace"]
            apiversion = obj.get("apiVersion")
            domain, version = apiversion.split('/')
    if name is None:
        module.fail_json(msg='missing name')
    if namespace is None:
        module.fail_json(msg='missing namespace')
    if domain is None:
        module.fail_json(msg='missing domain')
    if version is None:
        module.fail_json(msg='missing version')
    if kind is None:
        module.fail_json(msg='missing kind')
    found = exists(crds, kind, version, domain, name, namespace)
    if state == 'present':
        if found:
            changed = False
            skipped = True
            meta = {'result': 'skipped'}
        else:
            changed = True
            skipped = False
            if src is None:
                obj = {'kind': '%s' % kind.capitalize(), 'apiVersion': '%s/%s' % (domain, version), 'metadata': {'namespace': namespace, 'name': name}}
            try:
                meta = crds.create_namespaced_custom_object(domain, version, namespace, '%ss' % kind, obj)
            except Exception as err:
                    module.fail_json(msg='Error creating object, got %s' % err)
    else:
        if found:
            try:
                meta = crds.delete_namespaced_custom_object(domain, version, namespace, '%ss' % kind, name, client.V1DeleteOptions())
            except Exception as err:
                    module.fail_json(msg='Error deleting object, got %s' % err)
            changed = True
    found = exists(crds, kind, version, domain, name, namespace)
    if state == 'present':
        if found:
            changed = False
            skipped = True
            meta = {'result': 'skipped'}
        else:
            changed = True
            skipped = False
            try:
                meta = crds.create_namespaced_custom_object(domain, version, namespace, '%ss' % kind, obj)
            except Exception as err:
                    module.fail_json(msg='Error creating object, got %s' % err)
    else:
        if found:
            try:
                meta = crds.delete_namespaced_custom_object(domain, version, namespace, '%ss' % kind, name, client.V1DeleteOptions())
            except Exception as err:
                    module.fail_json(msg='Error deleting object, got %s' % err)
            changed = True
            skipped = False
        else:
            changed = False
            skipped = True
            meta = {'result': 'skipped'}
    module.exit_json(changed=changed, skipped=skipped, meta=meta)

if __name__ == '__main__':
    main()
