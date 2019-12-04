# Copyright 2008-2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.

# Permission is hereby granted, free of charge, to any person obtaining a copy of this
# software and associated documentation files (the "Software"), to deal in the Software
# without restriction, including without limitation the rights to use, copy, modify,
# merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from __future__ import print_function
import sys
import requests
import json
import yaml
import os


def update(cloud_endure, projectId, machinelist, dryrun):
    session = cloud_endure.session
    headers = cloud_endure.headers
    endpoint = cloud_endure.endpoint
    HOST = cloud_endure.host
    config = cloud_endure.config

    machine_list = {machinelist[machine]['id']: machine for machine in machinelist.keys()}
    try:
        blueprint_list = \
            json.loads(requests.get(HOST + endpoint.format('projects/{}/blueprints').format(projectId), headers=headers,
                                    cookies=session).text)["items"]
        config_machines = config['Machines']
        for blueprint in blueprint_list:
            machine_name = machine_list[blueprint["machineId"]]
            if machine_name in config_machines.keys():
                machine = config_machines[machine_name]
                url = endpoint.format('projects/{}/blueprints/').format(projectId) + blueprint['id']
                blueprint["instanceType"] = machine["instanceType"]
                if "tenancy" in machine:
                    blueprint["tenancy"] = machine["tenancy"]
                if "iamRole" in machine and machine["iamRole"].lower() != "none":
                    blueprint["iamRole"] = machine["iamRole"]
                if machine['disks']['type']:
                    tmp = []
                    disk_type = machine['disks']['type']
                    for disk in blueprint["disks"]:
                        disk["type"] = disk_type
                        tmp.append(disk)
                    blueprint["disks"] = tmp
                if "subnetIDs" in machine:
                    blueprint["subnetIDs"] = machine["subnetIDs"]
                if "securitygroupIDs" in machine:
                    blueprint["securityGroupIDs"] = machine["securitygroupIDs"]
                if "publicIPAction" in machine:
                    blueprint["publicIPAction"] = machine["publicIPAction"]
                if "privateIPs" in machine:
                    blueprint["privateIPAction"] = machine["privateIPs"]
                if "tags" in machine:
                    tags = []
                    # Update machine tags
                    for i in range(1, machine["tags"]["count"] + 1):
                        keytag = "key" + str(i)
                        valuetag = "value" + str(i)
                        tag = {"key": machine["tags"][keytag], "value": machine["tags"][valuetag]}
                        tags.append(tag)
                    blueprint["tags"] = tags
                if not dryrun:
                    result = requests.patch(HOST + url, data=json.dumps(blueprint), headers=headers,
                                            cookies=session)
                    if result.status_code != 200:
                        print(
                            "ERROR: Updating blueprint failed for machine: " + machine_name + ", invalid blueprint config....")
                        sys.exit(4)
                    machine_list[blueprint["machineId"]] = "updated"
                    print("Blueprint for machine: " + machine_name + " updated....")
                else:
                    if json.dumps(blueprint):
                        print("Blueprint information was valid, dryrun was successfull.\n" +
                              "Please proceed with your update...")
                    else:
                        print("Bluprint data was incorrect, and the udate failed." +
                              "Please verify your data before moving forward...")
            elif machine_name.lower() in [machine.lower() for machine in config_machines.keys()]:
                print("Error: Machine name ts, but case does not match between AWS and config...")
                print("Value in AWS: " + machine_name)
    except:
        print("ERROR: Updating blueprint task failed....")
        print(sys.exc_info())
        sys.exit(3)
