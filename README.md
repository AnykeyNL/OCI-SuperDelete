# OCI-SuperDelete
Delete all OCI resources in a compartment. 

Initial development by Richard Garsthagen - www.oc-blog.com 

### Contributors (Thank you!!!)
- Allen Kubai Wangu (https://github.com/allenkubai)
- Alexey Dolganov (https://github.com/aorcl)
- T-Srikanth (https://github.com/T-Srikanth)
- Adi Zohar (https://github.com/adizohar)

## Running the script
how to run:

```
usage: delete.py [-h] [-cf CONFIG_FILE] [-cp CONFIG_PROFILE] [-force] [-debug] [-rg REGIONS] [-c COMPARTMENT]

optional arguments:
  -h, --help                show this help message and exit
  -cf CONFIG_FILE           OCI CLI Config file
  -cp CONFIG_PROFILE        Config Profile inside the config file
  -force                    force delete without confirmation
  -debug                    Enable debug
  -rg REGIONS               Regions to delete comma separated
  -c COMPARTMENT            top level compartment id to delete
  -skip_delete_compartment  Skip Deleting the compartments at end of the process

python3 delete.py -c <CompartmentID>
```

## WORK_IN_PROGRESS
This script is continuously being maintained based on newly released services. If you are noticing this script is missing a particulair service, please let us know, so we can add this.

This script has being massive overhauled in January/February 2022. Instead of having a complete python module for each service, most services are now being deleted via the AnyDelete method included in this script.

The KMS Vaults and Keys can not instantly be deleted, but require a minimal 7 day grace period. The script will move all keys and vaults to the root compartment and will schedule the deletion with 7 days grace period. This will allow all sub compartments to be instantly deleted, while the top compartment will only be able to be deleted after the grace period. 

## Purpose
The purpose of this script is to remove all resources from a compartment, including subcompartments. In OCI you can only remove a compartment when it contains no more resources, but it can be a challenge to find all the resources tied to a compartment. 

This script will hunt for all resources in a compartment and delete/terminate/retire them.

## TODO
Currently this script only support authentication via config file. Plan is to add instance principle support and cloud shell authentication support.

## Disclaimer
This is a personal repository. Any code, views or opinions represented here are personal and belong solely to me and do not represent those of people, institutions or organizations that I may or may not be associated with in professional or personal capacity, unless explicitly stated.

