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
import datetime


def status(cloud_endure, project_id, launchtype, dryrun):
    config = cloud_endure.config
    HOST = cloud_endure.host
    endpoint = cloud_endure.endpoint
    headers = cloud_endure.headers
    session = cloud_endure.session
    machine_status = 0
    machine_list = json.loads(
        requests.get(HOST + endpoint.format('projects/{}/machines').format(project_id), headers=headers,
                     cookies=session).text)["items"]
    cloudEndure_machines = {machine['sourceProperties']['name']:machine for machine in machine_list}
    for config_machine in config['Machines'].keys():
        machine_exist = False
        if config_machine in cloudEndure_machines.keys():
            machine_exist = True
            machine = cloudEndure_machines[config_machine]
            # Check replication status
            if 'lastConsistencyDateTime' not in machine['replicationInfo']:
                print("ERROR: Machine: " + machine['sourceProperties']['name'] + " replication in progress, please wait for a few minutes....")
                sys.exit(1)
            else:
                # check replication lag
                a = int(machine['replicationInfo']['lastConsistencyDateTime'][11:13])
                b = int(machine['replicationInfo']['lastConsistencyDateTime'][14:16])
                x = int(datetime.datetime.utcnow().isoformat()[11:13])
                y = int(datetime.datetime.utcnow().isoformat()[14:16])
                result = (x - a) * 60 + (y - b)
                if result > 180:
                    print("ERROR: Machine: " + machine['sourceProperties']['name'] + " replication lag is more than 180 minutes....")
                    print("- Current Replication lag for " + machine['sourceProperties']['name'] + " is: " + str(result) + " minutes....")
                    sys.exit(6)
                else:
                    # Check dryrun flag and skip the rest of checks
                    if dryrun:
                        machine_status += 1
                    else:
                    # Check if the target machine has been tested already
                        if launchtype == "test":
                            if 'lastTestLaunchDateTime' not in machine["lifeCycle"] and 'lastCutoverDateTime' not in machine["lifeCycle"]:
                                machine_status += 1
                            else:
                                print("ERROR: Machine: " + machine['sourceProperties']['name'] + " has been tested already....")
                                sys.exit(2)
                        # Check if the target machine has been migrated to PROD already
                        elif launchtype == "cutover":
                            if 'lastTestLaunchDateTime' in machine["lifeCycle"]:
                                if 'lastCutoverDateTime' not in machine["lifeCycle"]:
                                    machine_status += 1
                                else:
                                    print("ERROR: Machine: " + machine['sourceProperties']['name'] + " has been migrated already....")
                                    sys.exit(3)
                            else:
                                print("ERROR: Machine: " + machine['sourceProperties']['name'] + " has not been tested....")
                                sys.exit(4)
        if machine_exist == False:
               print("ERROR: Machine: " + config_machine + " does not exist....")
               sys.exit(7)

    if machine_status == len(config["Machines"].keys()):
       print("All Machines in the config file are ready....")
    else:
       print("ERROR: some machines in the config file are not ready....")
       sys.exit(5)
