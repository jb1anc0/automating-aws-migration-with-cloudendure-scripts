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


def launch(launchtype, cloud_endure, project_id, machine_list):
    session = cloud_endure.session
    headers = cloud_endure.headers
    endpoint = cloud_endure.endpoint
    HOST = cloud_endure.host

    machine_ids = []
    machine_names = []
    config_machines = cloud_endure.config['Machines']

    for machine in config_machines.keys():
        if machine in machine_list:
            machine_ids.append({"machineId": machine_list[machine]['id']})
            machine_names.append(machine_list[machine]['sourceProperties']['name'])
    if launchtype == "test":
        machine_data = {'items': machine_ids, "launchType": "TEST"}
    elif launchtype == "cutover":
        machine_data = {'items': machine_ids, "launchType": "CUTOVER"}
    else:
        print("ERROR: Invalid Launch Type....")
    result = requests.post(HOST + endpoint.format('projects/{}/launchMachines').format(project_id),
                           data=json.dumps(machine_data), headers=headers, cookies=session)
    # Response code translate to message
    if result.status_code == 202:
        if launchtype == "test":
            print("Test Job created for machine: ")
            for machine in machine_names:
                print("****** " + machine + " ******")
        if launchtype == "cutover":
            print("Cutover Job created for machine: ")
            for machine in machine_names:
                print("****** " + machine + " ******")
    elif result.status_code == 409:
        print("ERROR: Source machines have job in progress....")
    elif result.status_code == 402:
        print("ERROR: Project license has expired....")
    else:
        print(result.text)
        print("ERROR: Launch target machine failed....")
