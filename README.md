# OCI-SuperDelete
Delete all OCI resources in a compartment

## WORK_IN_PROGRESS
This script is still being worked on, not all OCI resources have been added yet.

## Purpose
The purpose of this script is to remove all resources from a compartment, including subcompartments. In OCI you can only remove a compartment when it contains no more resources, but it can be a challenge to find all the resources tied to a compartment. 

This script will hunt for all resources in a compartment and delete/terminate/retire them.

