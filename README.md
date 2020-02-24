# OCI-SuperDelete
Delete all OCI resources in a compartment

## Running the script
how to run:

python3 delete.py -c \<CompartmentID>


## WORK_IN_PROGRESS
This script is still being worked on, not all OCI resources have been added yet. Currently supported:
- Compute resources
- Database and Autonomous Database resources
- Edge Services
- File Storage services
- Tag Namespaces
- Block Storage 
- Resource Manager Stacks
- VCN resources
- Autoscaling policies
- Notifications
- Alarms
- Applications and Functions

## Purpose
The purpose of this script is to remove all resources from a compartment, including subcompartments. In OCI you can only remove a compartment when it contains no more resources, but it can be a challenge to find all the resources tied to a compartment. 

This script will hunt for all resources in a compartment and delete/terminate/retire them.

## Contributors (Thank you!!!)
- Allen Kubai Wangu (https://github.com/allenkubai)

## Disclaimer
This is a personal repository. Any code, views or opinions represented here are personal and belong solely to me and do not represent those of people, institutions or organizations that I may or may not be associated with in professional or personal capacity, unless explicitly stated.

