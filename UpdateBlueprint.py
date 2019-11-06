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
        b = requests.get(HOST + endpoint.format('projects/{}/blueprints').format(projectId), headers=headers,
                         cookies=session)
        for blueprint in json.loads(b.text)["items"]:
            machineName = machine_list[blueprint["machineId"]]
            for i in range(1, config["project"]["machinecount"] + 1):
                index = "machine" + str(i)
                if config[index]["machineName"] == machineName:
                    url = endpoint.format('projects/{}/blueprints/').format(projectId) + blueprint['id']
                    blueprint["instanceType"] = config[index]["instanceType"]
                    if "tenancy" in config[index]:
                        blueprint["tenancy"] = config[index]["tenancy"]
                    if config[index]["iamRole"].lower() != "none":
                        blueprint["iamRole"] = config[index]["iamRole"]
                    if config[index]['disks']['type']:
                        tmp = []
                        for disk in blueprint["disks"]:
                            disk["type"] = "SSD"
                            tmp.append(disk)
                        blueprint["disks"] = tmp
                    existing_subnetId = blueprint["subnetIDs"]
                    existing_SecurityGroupIds = blueprint["securityGroupIDs"]
                    if "subnetIDs" in config[index]:
                        blueprint["subnetIDs"] = config[index]["subnetIDs"]
                    if "securitygroupIDs" in config[index]:
                        blueprint["securityGroupIDs"] = config[index]["securitygroupIDs"]
                    if "publicIPAction" in config[index]:
                        blueprint["publicIPAction"] = config[index]["publicIPAction"]
                    if "privateIPs" in config[index]:
                        blueprint["privateIPAction"] = config[index]["privateIPs"]
                    existing_tag = blueprint["tags"]
                    if "tags" in config[index]:
                        tags = []
                        # Update machine tags
                        for i in range(1, config[index]["tags"]["count"] + 1):
                            keytag = "key" + str(i)
                            valuetag = "value" + str(i)
                            tag = {"key": config[index]["tags"][keytag], "value": config[index]["tags"][valuetag]}
                            tags.append(tag)
                        blueprint["tags"] = tags
                    result = requests.patch(HOST + url, data=json.dumps(blueprint), headers=headers, cookies=session)
                    if result.status_code != 200:
                        print(
                            "ERROR: Updating blueprint failed for machine: " + machineName + ", invalid blueprint config....")
                        if dryrun:
                            print("ERROR: YAML validation failed, please fix the errors in the cutover YAML file")
                        sys.exit(4)
                    machine_list[blueprint["machineId"]] = "updated"
                    print("Blueprint for machine: " + machineName + " updated....")
                    if dryrun:
                        blueprint["subnetIDs"] = existing_subnetId
                        blueprint["securityGroupIDs"] = existing_SecurityGroupIds
                        blueprint["tags"] = existing_tag
                        result = requests.patch(HOST + url, data=json.dumps(blueprint), headers=headers,
                                                cookies=session)
                        if result.status_code != 200:
                            print("ERROR: Failed to roll back subnet,SG and tags for machine: " + machineName + "....")
                            sys.exit(5)
                        else:
                            print("Dryrun was successful for machine: " + machineName + "....")
                elif config[index]["machineName"].lower() == machineName.lower():
                    print("Error: Machine name ts, but case does not match between AWS and config...")
                    print("Value in AWS: " + machineName + ", value in config: " + config[index]["machineName"])

    except:
        print("ERROR: Updating blueprint task failed....")
        print(sys.exc_info())
        sys.exit(3)
