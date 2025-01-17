
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
usage: delete.py [-h] [-cp CONFIG_PROFILE] [-ip] [-dt] [-log LOG_FILE] [-force] [-debug] [-skip_delete_compartment] [-rg REGIONS]
                 [-c COMPARTMENT]

optional arguments:
  -h, --help                show this help message and exit
  -cp CONFIG_PROFILE        Config Profile inside the config file
  -ip                       Use Instance Principals for Authentication
  -dt                       Use Delegation Token for Authentication
  -log LOG_FILE             output log file
  -force                    force delete without confirmation
  -debug                    Enable debug
  -skip_delete_compartment  Skip Deleting the compartment at the end
  -rg REGIONS               Regions to delete comma separated
  -c COMPARTMENT            top level compartment id to delete

python3 delete.py -c <CompartmentID>
```

  

## WORK_IN_PROGRESS

This script is continuously being maintained based on newly released services. If you are noticing this script is missing a particulair service, please let us know, so we can add this.

  

This script has being massive overhauled in January/February 2022. Instead of having a complete python module for each service, most services are now being deleted via the AnyDelete method included in this script.

  

The KMS Vaults and Keys can not instantly be deleted, but require a minimal 7 day grace period. The script will move all keys and vaults to the root compartment and will schedule the deletion with 7 days grace period. This will allow all sub compartments to be instantly deleted, while the top compartment will only be able to be deleted after the grace period.

  

## Purpose

The purpose of this script is to remove all resources from a compartment, including subcompartments. In OCI you can only remove a compartment when it contains no more resources, but it can be a challenge to find all the resources tied to a compartment.

  

This script will hunt for all resources in a compartment and delete/terminate/retire them.

  
  

## Disclaimer

This is a personal repository. Any code, views or opinions represented here are personal and belong solely to me and do not represent those of people, institutions or organizations that I may or may not be associated with in professional or personal capacity, unless explicitly stated.

  

## How to Speed up the Delete Process

Let's say that you have to clean a very big tenancy (+1000 compartments, ~30 regions), here I share some simple steps to help you with that.

  

Go to Cost Analysis and build a filter:
Tenant:Your tenancy name (because you could have child accounts)
Grouping:Compartment
Take note of biggest compartments
Grouping: Regions

  

Now you know what is your biggest region and compartment and you can run the delete.py passing the compartment and region as parameter
  

If you would like to use oci cli you can run:

  

    export OCIPROFILE=your-oci-cli-config-profile
    export TENANCYOCID=your-tenancy-ocid
    export HOMEREGION=your-home-region
    export LEVEL=6
    export STARTDATE=`date --date 'today - 7 days' "+%Y-%m-%d"`
    export ENDDATE=`date --date 'today' "+%Y-%m-%d"`

### Get Cost by Region

    oci usage-api usage-summary request-summarized-usages --granularity DAILY --tenant-id ${TENANCYOCID} --group-by '[ "region"]' --compartment-depth ${LEVEL} --time-usage-started "${STARTDATE}T00:00:00Z" --time-usage-ended "${ENDDATE}T00:00:00Z" --region ${HOMEREGION} --profile ${OCIPROFILE} --query "data.items[*].{Region:\"region\",Start:\"time-usage-started\",End:\"time-usage-ended\",Cost:\"computed-amount\" } | sort_by([], &Cost)[-20:]" --output table

  

### Get Cost by compartments

    oci usage-api usage-summary request-summarized-usages --granularity DAILY --tenant-id ${TENANCYOCID} --group-by '[ "compartmentId"]' --compartment-depth ${LEVEL} --time-usage-started "${STARTDATE}T00:00:00Z" --time-usage-ended "${ENDDATE}T00:00:00Z" --region ${HOMEREGION} --profile ${OCIPROFILE} --query "data.items[*].{CompartmentID:\"compartment-id\",Start:\"time-usage-started\",End:\"time-usage-ended\",Cost:\"computed-amount\" } | sort_by([], &Cost)[-20:]" --output table

  

### All in one command

    oci usage-api usage-summary request-summarized-usages --granularity DAILY --tenant-id ${TENANCYOCID} --group-by '[ "compartmentId","region"]' --compartment-depth ${LEVEL} --time-usage-started "${STARTDATE}T00:00:00Z" --time-usage-ended "${ENDDATE}T00:00:00Z" --region ${HOMEREGION} --profile ${OCIPROFILE} --query "data.items[*].{CompartmentID: join('',['python3 delete.py -c ',\"compartment-id\",' -rg ',\"region\", ' -cp ' ,'$OCIPROFILE',' -skip_delete_compartment -force & ']),Cost:\"computed-amount\" } | sort_by([], &Cost)[-20:]" --output table

  

The output should look like this:

        +----------------------------------------------------------------------------------------------------------------------+-----------------+
    | CompartmentID                                                                                    		                 | Cost          |
    +----------------------------------------------------------------------------------------------------------------------+-----------------+
    | python3 delete.py -c ocid1.compartment.oc1..a...ta -rg us-ashburn-1 -cp tenancy -skip_delete_compartment -force &  | 33.504388600351 |
    | python3 delete.py -c ocid1.compartment.oc1..a...ta -rg us-ashburn-1 -cp tenancy -skip_delete_compartment -force &  | 33.504389859927 |
    | python3 delete.py -c ocid1.compartment.oc1..a...ta -rg us-ashburn-1 -cp tenancy -skip_delete_compartment -force &  | 33.504389859927 |
    | python3 delete.py -c ocid1.compartment.oc1..a...ta -rg us-ashburn-1 -cp tenancy -skip_delete_compartment -force &  | 33.504389859927 |
    | python3 delete.py -c ocid1.compartment.oc1..a...ka -rg us-ashburn-1 -cp tenancy -skip_delete_compartment -force &  | 35.855228224322 |
    | python3 delete.py -c ocid1.compartment.oc1..a...ka -rg us-ashburn-1 -cp tenancy -skip_delete_compartment -force &  | 36.098833174653 |
    | python3 delete.py -c ocid1.compartment.oc1..a...ka -rg us-ashburn-1 -cp tenancy -skip_delete_compartment -force &  | 37.282047912158 |
    | python3 delete.py -c ocid1.compartment.oc1..a...ka -rg us-ashburn-1 -cp tenancy -skip_delete_compartment -force &  | 37.282651431786 |
    | python3 delete.py -c ocid1.compartment.oc1..a...ka -rg us-ashburn-1 -cp tenancy -skip_delete_compartment -force &  | 37.523564309667 |
    | python3 delete.py -c ocid1.compartment.oc1..a...ka -rg us-chicago-1 -cp tenancy -skip_delete_compartment -force &  | 39.242039669197 |
    | python3 delete.py -c ocid1.compartment.oc1..a...ia -rg us-ashburn-1 -cp tenancy -skip_delete_compartment -force &  | 50.317674231791 |
    | python3 delete.py -c ocid1.compartment.oc1..a...ia -rg us-ashburn-1 -cp tenancy -skip_delete_compartment -force &  | 50.317674231791 |
    | python3 delete.py -c ocid1.compartment.oc1..a...ia -rg us-ashburn-1 -cp tenancy -skip_delete_compartment -force &  | 50.317675806259 |
    | python3 delete.py -c ocid1.compartment.oc1..a...ia -rg us-ashburn-1 -cp tenancy -skip_delete_compartment -force &  | 50.317675806261 |
    | python3 delete.py -c ocid1.compartment.oc1..a...ia -rg us-ashburn-1 -cp tenancy -skip_delete_compartment -force &  | 50.317675806262 |
    | python3 delete.py -c ocid1.compartment.oc1..a...ka -rg us-chicago-1 -cp tenancy -skip_delete_compartment -force &  | 85.618995641881 |
    | python3 delete.py -c ocid1.compartment.oc1..a...ka -rg us-chicago-1 -cp tenancy -skip_delete_compartment -force &  | 85.640163736529 |
    | python3 delete.py -c ocid1.compartment.oc1..a...ka -rg us-chicago-1 -cp tenancy -skip_delete_compartment -force &  | 85.642241765841 |
    | python3 delete.py -c ocid1.compartment.oc1..a...ka -rg us-chicago-1 -cp tenancy -skip_delete_compartment -force &  | 85.642241928985 |
    | python3 delete.py -c ocid1.compartment.oc1..a...ka -rg us-chicago-1 -cp tenancy -skip_delete_compartment -force &  | 85.642241928986 |
    +----------------------------------------------------------------------------------------------------------------------+-----------------+

And if you want unique values:

    oci usage-api usage-summary request-summarized-usages --granularity DAILY --tenant-id ${TENANCYOCID}  --group-by  '[ "compartmentId","region"]'  --compartment-depth ${LEVEL}  --time-usage-started "${STARTDATE}T00:00:00Z"  --time-usage-ended "${ENDDATE}T00:00:00Z"  --region ${HOMEREGION}  --profile ${OCIPROFILE}  --query "data.items[*].{CompartmentID: join('',['python3 delete.py -c ',\"compartment-id\",' -rg ',\"region\", ' -cp ' ,'$OCIPROFILE',' -skip_delete_compartment -force & ']),Cost:\"computed-amount\" } | sort_by([], &Cost)[-20:]"  | jq -r 'map(.CompartmentID) | unique '

The output:

    [
      "python3 delete.py -c ocid1.compartment.oc1..xxxxx -rg us-ashburn-1 -cp tenancy -skip_delete_compartment -force & ",
      "python3 delete.py -c ocid1.compartment.oc1..xxxxx -rg us-chicago-1 -cp tenancy -skip_delete_compartment -force & ",
      "python3 delete.py -c ocid1.compartment.oc1..xxxxx -rg us-ashburn-1 -cp tenancy -skip_delete_compartment -force & ",
      "python3 delete.py -c ocid1.compartment.oc1..xxxxx -rg us-ashburn-1 -cp tenancy -skip_delete_compartment -force & "
    ]

And you can lower the MaxIDeleteIteration value inside AnyDelete.py to control how many retries per resource.
