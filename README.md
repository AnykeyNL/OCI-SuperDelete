# OCI-SuperDelete
Delete all OCI resources in a compartment. 

Written by Richard Garsthagen - www.oc-blog.com 

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
- Block Storage, Block Volume Backups, Volume Groups, Volume Group Backups
- Resource Manager Stacks
- VCN resources
- Autoscaling policies
- Notifications
- Alarms
- Applications and Functions
- DataScience Projects and Notebooks
- Container Cluster resources
- Nosql tables
- Data Catalogs
- Digital Assistants
- Policies
- KMS Vaults and Keys**
- API Gateways

** KMS Vaults and Keys can not instantly be deleted, but require a minimal 7 day grace period. The script will move all keys and vaults to the upper compartment and will schedule the deletion with 7 days grace period. This will allow all sub compartments to be instantly deleted, while the top compartment will only be able to be deleted after the grace period. 

## Purpose
The purpose of this script is to remove all resources from a compartment, including subcompartments. In OCI you can only remove a compartment when it contains no more resources, but it can be a challenge to find all the resources tied to a compartment. 

This script will hunt for all resources in a compartment and delete/terminate/retire them.

## Contributors (Thank you!!!)
- Allen Kubai Wangu (https://github.com/allenkubai)
- Alexey Dolganov (https://github.com/aorcl)

## Disclaimer
This is a personal repository. Any code, views or opinions represented here are personal and belong solely to me and do not represent those of people, institutions or organizations that I may or may not be associated with in professional or personal capacity, unless explicitly stated.

