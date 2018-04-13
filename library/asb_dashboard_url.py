#!/usr/bin/python

ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
---
module: asb_dashboard_url
short_description: Adds a annotation to the pod running the apb with the dashboard URL
description:
     - Takes a string containing the dashboard URL. This URL should point to the provisioned application.
       This URL is then added an an annotation to the pod executing the apb and read by the broker.
notes: []
requirements: []
author:
    - "Red Hat, Inc."
options:
  description:
    iption:
      - 'string describing the last operation'
    required: true
    default: ""
'''

EXAMPLES = '''
- name: update last operation
  asb_last_operation:
    description:
      "10%: creating service route"
'''
RETURN = '''

'''

import json
import base64
import os
from ansible.module_utils.basic import AnsibleModule
try:
    from kubernetes import client, config
    config.load_kube_config()
    api = client.CoreV1Api()
except Exception as error:
    ansible_module.fail_json(msg="Error attempting to load kubernetes client: {}".format(error))

DASHBOARD_URL_ANNOTATION = "apb_dashboard_url"
ENV_NAME = "POD_NAME"
ENV_NAMESPACE = "POD_NAMESPACE"


def main():

    argument_spec = dict(
        description=dict(required=True, type='str')
    )

    ansible_module = AnsibleModule(argument_spec=argument_spec)

    dashUrl = ansible_module.params['dashboard_url']

    try:
        name = os.environ[ENV_NAME]
        namespace = os.environ[ENV_NAMESPACE]
    except KeyError as error:
        ansible_module.fail_json(msg="Error attempting to update pod with dashboard_url annotation. Missing key from environment: {}".format(error))

    try:
        pod = api.read_namespaced_pod(
            name=name,
            namespace=namespace
        )

        if not pod.metadata.annotations:
            pod.metadata.annotations = {}
        pod.metadata.annotations[DASHBOARD_URL_ANNOTATION] = dashUrl
        api.replace_namespaced_pod(name=name,namespace=namespace,body=pod,pretty='true')
    except Exception as error:
        ansible_module.fail_json(msg="Error attempting to update pod with dashboard_url annotation: {}".format(error))

    ansible_module.exit_json(changed=True, dashboard_url=dashUrl)


if __name__ == '__main__':
    main()
