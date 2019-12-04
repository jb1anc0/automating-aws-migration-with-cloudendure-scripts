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
import UpdateBlueprint
import CheckMachine
import LaunchMachine
import requests
import json


def update_blueprint(launchtype, cloud_endure, projectname, dryrun):
    project_id = cloud_endure.get_project_id(projectname)
    # Get Machine List
    machine_list = cloud_endure.get_machine_list(project_id)

    if machine_list is None:
        print("ERROR: Failed to fetch the machines....")
        sys.exit(3)
    for machine in machine_list.keys():
        print('Machine name:{}, Machine ID:{}'.format(machine, machine_list[machine]['id']))
    try:
        # Check Target Machines
        print("****************************")
        print("* Checking Target machines *")
        print("****************************")
        CheckMachine.status(cloud_endure, project_id, launchtype, dryrun)

        # Update Machine Blueprint
        print("**********************")
        print("* Updating Blueprint *")
        print("**********************")
        UpdateBlueprint.update(cloud_endure, project_id, machine_list, dryrun)

    except:
        print(sys.exc_info())
        sys.exit(6)


def execute(launchtype, cloud_endure, projectname, dryrun):
    project_id = cloud_endure.get_project_id(projectname)
    # Get Machine List
    machine_list = cloud_endure.get_machine_list(project_id)

    if machine_list is None:
        print("ERROR: Failed to fetch the machines....")
        sys.exit(3)
    for machine in machine_list.keys():
        print('Machine name:{}, Machine ID:{}'.format(machine, machine_list[machine]['id']))
    try:
        # Check Target Machines
        print("****************************")
        print("* Checking Target machines *")
        print("****************************")
        CheckMachine.status(cloud_endure, project_id, launchtype, dryrun)

        # Launch Target machines
        print("*****************************")
        print("* Launching target machines *")
        print("*****************************")
        if not dryrun:
            LaunchMachine.launch(launchtype, cloud_endure, project_id, machine_list)
        else:
            print("Dry run successfully executed!")

    except:
        print(sys.exc_info())
        sys.exit(6)
