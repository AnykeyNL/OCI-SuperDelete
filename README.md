# OCI-SuperDelete

Delete all OCI resources in a compartment.

Initial development by Richard Garsthagen - <www.oc-blog.com>

[[TOC]]

## Running the script

### Installation Steps

$ git clone https://github.com/AnykeyNL/OCI-SuperDelete.git
$ cd OCI-SuperDelete
$ python3 -m venv .venv
$ source .venv/bin/activate
$ python3 -m pip install --upgrade pip wheel setuptools
$ python3 -m pip install -r requirements.txt

### Running Directly with Python

To run the script directly with Python:

```bash
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

### Using GitHub Container Registry (Recommended)

The script is available as a pre-built container from GitHub Container Registry with support for both amd64 and arm64 architectures:

```bash
docker run -v ~/.oci:/root/.oci ghcr.io/Jubblin/oci-superdelete:latest -c <CompartmentID>
```

### Building from Source

If you prefer to build from source, you can use the following commands:

#### Single Architecture Build

```bash
docker build -t oci-superdelete .
```

#### Multi-architecture Build (Recommended)

The container supports both amd64 and arm64 architectures. To build for multiple architectures:

1. Create and use a new builder instance:

```bash
docker buildx create --name mybuilder --use
```

1. Build and push for multiple architectures:

```bash
docker buildx build --platform linux/amd64,linux/arm64 \
  -t ghcr.io/richardw/oci-superdelete:latest \
  --push .
```

1. Run the container (Docker will automatically select the correct architecture):

```bash
docker run -v ~/.oci:/root/.oci ghcr.io/Jubblin/oci-superdelete:latest -c <CompartmentID>
```

Note: You need to be logged in to GitHub Container Registry to push:

```bash
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin
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

``` bash
export OCIPROFILE=your-oci-cli-config-profile
export TENANCYOCID=your-tenancy-ocid
export HOMEREGION=your-home-region
export LEVEL=6
export STARTDATE=`date --date 'today - 7 days' "+%Y-%m-%d"`
export ENDDATE=`date --date 'today' "+%Y-%m-%d"`
```

### Get Cost by Region

```bash
oci usage-api usage-summary request-summarized-usages --granularity DAILY --tenant-id ${TENANCYOCID} --group-by '[ "region"]' --compartment-depth ${LEVEL} --time-usage-started "${STARTDATE}T00:00:00Z" --time-usage-ended "${ENDDATE}T00:00:00Z" --region ${HOMEREGION} --profile ${OCIPROFILE} --query "data.items[*].{Region:\"region\",Start:\"time-usage-started\",End:\"time-usage-ended\",Cost:\"computed-amount\" } | sort_by([], &Cost)[-20:]" --output table
```

### Get Cost by compartments

```bash
oci usage-api usage-summary request-summarized-usages --granularity DAILY --tenant-id ${TENANCYOCID} --group-by '[ "compartmentId"]' --compartment-depth ${LEVEL} --time-usage-started "${STARTDATE}T00:00:00Z" --time-usage-ended "${ENDDATE}T00:00:00Z" --region ${HOMEREGION} --profile ${OCIPROFILE} --query "data.items[*].{CompartmentID:\"compartment-id\",Start:\"time-usage-started\",End:\"time-usage-ended\",Cost:\"computed-amount\" } | sort_by([], &Cost)[-20:]" --output table
```

### All in one command

```bash
oci usage-api usage-summary request-summarized-usages --granularity DAILY --tenant-id ${TENANCYOCID} --group-by '[ "compartmentId","region"]' --compartment-depth ${LEVEL} --time-usage-started "${STARTDATE}T00:00:00Z" --time-usage-ended "${ENDDATE}T00:00:00Z" --region ${HOMEREGION} --profile ${OCIPROFILE} --query "data.items[*].{CompartmentID: join('',['python3 delete.py -c ',\"compartment-id\",' -rg ',\"region\", ' -cp ' ,'$OCIPROFILE',' -skip_delete_compartment -force & ']),Cost:\"computed-amount\" } | sort_by([], &Cost)[-20:]" --output table
```

The output should look like this:

```text
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
```

And if you want unique values:

```bash
oci usage-api usage-summary request-summarized-usages --granularity DAILY --tenant-id ${TENANCYOCID}  --group-by  '[ "compartmentId","region"]'  --compartment-depth ${LEVEL}  --time-usage-started "${STARTDATE}T00:00:00Z"  --time-usage-ended "${ENDDATE}T00:00:00Z"  --region ${HOMEREGION}  --profile ${OCIPROFILE}  --query "data.items[*].{CompartmentID: join('',['python3 delete.py -c ',\"compartment-id\",' -rg ',\"region\", ' -cp ' ,'$OCIPROFILE',' -skip_delete_compartment -force & ']),Cost:\"computed-amount\" } | sort_by([], &Cost)[-20:]"  | jq -r 'map(.CompartmentID) | unique '
```

The output:

```bash
[
  "python3 delete.py -c ocid1.compartment.oc1..xxxxx -rg us-ashburn-1 -cp tenancy -skip_delete_compartment -force & ",
  "python3 delete.py -c ocid1.compartment.oc1..xxxxx -rg us-chicago-1 -cp tenancy -skip_delete_compartment -force & ",
  "python3 delete.py -c ocid1.compartment.oc1..xxxxx -rg us-ashburn-1 -cp tenancy -skip_delete_compartment -force & ",
  "python3 delete.py -c ocid1.compartment.oc1..xxxxx -rg us-ashburn-1 -cp tenancy -skip_delete_compartment -force & "
]
```

And you can lower the MaxIDeleteIteration value inside AnyDelete.py to control how many retries per resource.

## Using Docker Container

### Prerequisites

- Docker installed on your system
- OCI configuration file (`~/.oci/config`) with appropriate credentials

### Building the Container

```bash
docker build -t oci-superdelete .
```

### Running the Container

The container needs access to your OCI configuration file. Mount your local OCI config directory when running the container:

```bash
docker run -v ~/.oci:/root/.oci oci-superdelete -c <CompartmentID>
```

### Example Commands

1. Delete resources in a specific compartment:

```bash
docker run -v ~/.oci:/root/.oci oci-superdelete -c ocid1.compartment.oc1..xxxxx
```

1. Force delete without confirmation:

```bash
docker run -v ~/.oci:/root/.oci oci-superdelete -c ocid1.compartment.oc1..xxxxx -force
```

1. Delete resources in specific regions:

```bash
docker run -v ~/.oci:/root/.oci oci-superdelete -c ocid1.compartment.oc1..xxxxx -rg us-ashburn-1,us-phoenix-1
```

1. Use a specific config profile:

```bash
docker run -v ~/.oci:/root/.oci oci-superdelete -c ocid1.compartment.oc1..xxxxx -cp myprofile
```

### Notes

- The container uses Python 3.11
- Your OCI configuration file must be properly set up with the necessary credentials
- The container mounts your local OCI config directory to `/root/.oci` inside the container
- All command-line arguments supported by the script can be used with the Docker container

## Contributors (Thank you!!!)

- Allen Kubai Wangu (https://github.com/allenkubai)

- Alexey Dolganov (https://github.com/aorcl)

- T-Srikanth (https://github.com/T-Srikanth)

- Adi Zohar (https://github.com/adizohar)
