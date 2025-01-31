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


def remove(cloud_endure, projectname, dryrun):
    project_id = cloud_endure.get_project_id(projectname)
    config = cloud_endure.config
    machines_info = cloud_endure.get_machine_list(project_id)
    launch_datetime = 'lastCutoverDateTime'
    machine_status = 0

    config_machines = config['Machines']

    for name in config_machines.keys():
        if name in machines_info.keys():
            if launch_datetime in machines_info[name]["lifeCycle"]:
                machine_data = {'machineIDs': [machines_info[name]['id']]}
                if (dryrun is True) or (cloud_endure.remove_machine(name, project_id, machine_data)):
                    print("Machine: " + name + " has been removed from CloudEndure...")
                    machine_status += 1
            else:
                # TODO: Check if removing this machine is feasible, even when it was not migrated.
                print("ERROR: Machine: " + name + " has not been migrated to PROD environment....")
                # sys.exit(4)
        else:
            print("ERROR: Machine: " + name + " does not exist....")

    if machine_status == len(config["Machines"].keys()):
        print("All Machines in the config file have been removed from CloudEndure....")
    else:
        print(
            "ERROR: Some machines in the config file do not exist or have NOT been migrated to the PROD environment....")
        sys.exit(5)
