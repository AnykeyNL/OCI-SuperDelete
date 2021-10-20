###########################################################
# OCI-SuperDelete                                         #
#                                                         #
# Use with PYTHON3!                                       #
###########################################################
# Application Command line parameters
#
#   -cf config     - OCI CLI Config File
#   -cp profile    - profile inside the config file
#   -force         - force delete without confirmation
#   -rg            - Regions to delete comma separated
#   -c compartment - top level compartment to delete
#   -debug         - enable debug
#
###########################################################

import sys
import time
import oci
import platform
import logging
from ocimodules.functions import *
from ocimodules.EdgeServices import *
from ocimodules.ObjectStorage import *
from ocimodules.Instances import *
from ocimodules.Database import *
from ocimodules.IAM import *
from ocimodules.VCN import *
from ocimodules.BlockStorage import *
from ocimodules.ResourceManager import *
from ocimodules.FileStorage import *
from ocimodules.Monitoring import *
from ocimodules.Notifications import *
from ocimodules.Autoscaling import *
from ocimodules.FunctionsService import *
from ocimodules.DataScience import *
from ocimodules.OKE import *
from ocimodules.kms import *
from ocimodules.Nosql import *
from ocimodules.datacatalog import *
from ocimodules.DigitalAssistant import *
from ocimodules.APIGateway import *
from ocimodules.Analytics import *
from ocimodules.MySQL import *
from ocimodules.Logging import *
from ocimodules.Integration import *
from ocimodules.Blockchain import *
from ocimodules.APM import *
from ocimodules.Artifacts import *
from ocimodules.Events import *
from ocimodules.VulnerabilityScanning import *
from ocimodules.Bastion import *


#################################################
#           Manual Configuration                #
#################################################
# Specify your config file
configfile = "~/.oci/config"  # Linux
# configfile = "\\Users\\username\\.oci\\config"  # Windows

# Specify your config profile
configProfile = "DEFAULT"

# Specify the DEFAULT compartment OCID that you want to delete, Leave Empty for no default
DeleteCompartmentOCID = ""

# Search for resources in regions, this is an Array, so you can specify multiple regions:
# If no regions specified, it will be all subscribed regions.
regions = ["eu-frankfurt-1", "eu-amsterdam-1"]
# regions = ["uk-london-1"]

#################################################
#           Application Configuration           #
#################################################
min_version_required = "2.41.1"
application_version = "21.10.19"
debug = False


#############################################
# MyWriter to redirect output
#############################################
class MyWriter:

    filename = "log.txt"

    def __init__(self, stdout, filename):
        self.stdout = stdout
        self.filename = filename
        self.logfile = open(self.filename, "a")

    def write(self, text):
        self.stdout.write(text)
        self.logfile.write(text)

    def close(self):
        self.stdout.close()
        self.logfile.close()

    def flush(self):
        self.logfile.close()
        self.logfile = open(self.filename, "a")


##########################################################################
# Main Program
##########################################################################
check_oci_version(min_version_required)

# Redirect output to log.txt
writer = MyWriter(sys.stdout, 'log.txt')
sys.stdout = writer

# Check command line
cmd = input_command_line()
configfile = cmd.config_file if cmd.config_file else configfile
configProfile = cmd.config_profile if cmd.config_profile else configProfile
debug = cmd.debug if cmd.debug else debug
force = cmd.force
regions = cmd.regions.split(",") if cmd.regions else regions
DeleteCompartmentOCID = cmd.compartment if cmd.compartment else DeleteCompartmentOCID

if DeleteCompartmentOCID == "":
    print("No compartment specified \n")
    input_command_line(help=True)
    sys.exit(2)

######################################################
# oci config and debug handle
######################################################
config = oci.config.from_file(configfile, configProfile)

if debug:
    config['log_requests'] = True
    logging.basicConfig()
    logging.getLogger('oci').setLevel(logging.DEBUG)

######################################################
# Loading Compartments
# Add all active compartments,
# exclude the ManagementCompartmentForPaas (as this is locked compartment)
######################################################
print("\nLogin check and loading comaprtments...\n")
compartments = Login(config, DeleteCompartmentOCID)
processCompartments = []
for compartment in compartments:
    if compartment.lifecycle_state == "ACTIVE" and compartment.name != "ManagedCompartmentForPaaS":
        processCompartments.append(compartment)

# Check if regions specified if not getting all subscribed regions.
if len(regions) == 0:
    regions = SubscribedRegions(config)

homeregion = GetHomeRegion(config)
tenane_name = GetTenantName(config)

######################################################
# Header Print and Confirmation
######################################################
print_header("OCI-SuperDelete", 0)

print("Date/Time          : " + time.strftime("%D %H:%M:%S", time.localtime()))
print("Command Line       : " + ' '.join(x for x in sys.argv[1:]))
print("App Version        : " + application_version)
print("Machine            : " + platform.node() + " (" + platform.machine() + ")")
print("OCI SDK Version    : " + oci.version.__version__)
print("Python Version     : " + platform.python_version())
print("Config File        : " + configfile)
print("Config Profile     : " + configProfile)
print("")
print("Tenant Name        : " + tenane_name)
print("Tenant Id          : " + config['tenancy'])
print("Home Region        : " + homeregion)
print("Regions to Process : " + ','.join(x for x in regions))
print("\nCompartments to Process : \n" + ','.join(x.name for x in processCompartments))

#########################################
# Check confirmation for execution
#########################################
confirm = ""
if force:
    confirm = "yes"
else:
    confirm = input("\ntype yes to delete all contents from these compartments: ")

if confirm == "yes":

    ######################################################
    # Loop on Regions
    ######################################################
    for region in regions:

        print_header("Deleting resources in region " + region, 0)
        config["region"] = region

        print_header("Moving and Scheduling KMS Vaults for deletion at " + time.strftime("%D %H:%M:%S", time.localtime()), 1)
        DeleteKMSvaults(config, processCompartments, DeleteCompartmentOCID)

        print_header("Deleting Vulnerability Scanning Services at " + time.strftime("%D %H:%M:%S", time.localtime()), 1)
        DeleteScanResults(config, processCompartments)
        DeleteTargets(config, processCompartments)
        DeleteRecipes(config, processCompartments)

        print_header("Deleting Bastion Services at " + time.strftime("%D %H:%M:%S", time.localtime()), 1)
        DeleteBastion(config, processCompartments)

        print_header("Deleting Edge Services at " + time.strftime("%D %H:%M:%S", time.localtime()), 1)
        DeleteWAFs(config, processCompartments)
        DeleteHTTPHealthchecks(config, processCompartments)
        DeletePINGHealthchecks(config, processCompartments)
        DeleteTrafficSteeringsAttachments(config, processCompartments)
        DeleteTrafficSteerings(config, processCompartments)
        DeleteZones(config, processCompartments)
        DeleteDNSViews(config, processCompartments)

        print_header("Deleting Object Storage at " + time.strftime("%D %H:%M:%S", time.localtime()), 1)
        DeleteBuckets(config, processCompartments)

        print_header("Deleting OKE Clusters at " + time.strftime("%D %H:%M:%S", time.localtime()), 1)
        DeleteClusters(config, processCompartments)

        print_header("Deleting Repositories at " + time.strftime("%D %H:%M:%S", time.localtime()), 1)
        DeleteContainerRepositories(config, processCompartments)
        DeleteRepositories(config, processCompartments)

        print_header("Deleting Auto Scaling Configurations at " + time.strftime("%D %H:%M:%S", time.localtime()), 1)
        DeleteAutoScalingConfigurations(config, processCompartments)

        print_header("Deleting Compute Instances at " + time.strftime("%D %H:%M:%S", time.localtime()), 1)
        DeleteInstancePools(config, processCompartments)
        DeleteInstanceConfigs(config, processCompartments)
        DeleteInstances(config, processCompartments)
        DeleteImages(config, processCompartments)
        DeleteBootVolumes(config, processCompartments)
        DeleteBootVolumesBackups(config, processCompartments)
        DeleteDedicatedVMHosts(config, processCompartments)

        print_header("Deleting DataScience Components at " + time.strftime("%D %H:%M:%S", time.localtime()), 1)
        DeleteNotebooks(config, processCompartments)
        DeleteModelDeployments(config, processCompartments)
        DeleteModels(config, processCompartments)
        DeleteProjects(config, processCompartments)

        print_header("Deleting Application Functions at " + time.strftime("%D %H:%M:%S", time.localtime()), 1)
        DeleteApplications(config, processCompartments)

        print_header("Deleting Deployments at " + time.strftime("%D %H:%M:%S", time.localtime()), 1)
        DeleteDeployments(config, processCompartments)

        print_header("Deleting APIs at " + time.strftime("%D %H:%M:%S", time.localtime()), 1)
        DeleteAPIs(config, processCompartments)

        print_header("Deleting API Gateways at " + time.strftime("%D %H:%M:%S", time.localtime()), 1)
        DeleteAPIGateways(config, processCompartments)
        DeleteCertificates(config, processCompartments)

        print_header("Deleting Database Instances at " + time.strftime("%D %H:%M:%S", time.localtime()), 1)
        DeleteDBCS(config, processCompartments)
        DeleteAutonomousDB(config, processCompartments)
        DeleteDBBackups(config, processCompartments)

        print_header("Deleting MySQL Database Instances at " + time.strftime("%D %H:%M:%S", time.localtime()), 1)
        DeleteMySQL(config, processCompartments)

        print_header("Deleting Nosql tables at " + time.strftime("%D %H:%M:%S", time.localtime()), 1)
        DeleteNosql(config, processCompartments)

        print_header("Deleting Data Catalogs at " + time.strftime("%D %H:%M:%S", time.localtime()), 1)
        DeleteDataCatalog(config, processCompartments)

        print_header("Deleting Digital Assistants at " + time.strftime("%D %H:%M:%S", time.localtime()), 1)
        DeleteDigitalAssistant(config, processCompartments)

        print_header("Deleting Analytics at " + time.strftime("%D %H:%M:%S", time.localtime()), 1)
        DeleteAnalytics(config, processCompartments)
        DeleteStreams(config, processCompartments)
        DeleteStreamPools(config, processCompartments)
        DeleteConnectHarnesses(config, processCompartments)
        DeleteServiceConnectors(config, processCompartments)

        print_header("Deleting Integration at " + time.strftime("%D %H:%M:%S", time.localtime()), 1)
        DeleteIntegration(config, processCompartments)

        print_header("Deleting Blockchain at " + time.strftime("%D %H:%M:%S", time.localtime()), 1)
        DeleteBlockchain(config, processCompartments)

        print_header("Deleting Resource Manager Stacks at " + time.strftime("%D %H:%M:%S", time.localtime()), 1)
        DeleteStacks(config, processCompartments)

        print_header("Deleting Block Volumes at " + time.strftime("%D %H:%M:%S", time.localtime()), 1)
        DeleteVolumeGroups(config, processCompartments)
        DeleteVolumeGroupBackups(config, processCompartments)
        DeleteVolumes(config, processCompartments)
        DeleteBlockVolumesBackups(config, processCompartments)

        print_header("Deleting FileSystem and Mount Targets at " + time.strftime("%D %H:%M:%S", time.localtime()), 1)
        DeleteMountTargets(config, processCompartments)
        DeleteFileStorage(config, processCompartments)

        print_header("Deleting VCNs at " + time.strftime("%D %H:%M:%S", time.localtime()), 1)
        DeleteVCN(config, processCompartments)

        print_header("Deleting Alarms at " + time.strftime("%D %H:%M:%S", time.localtime()), 1)
        DeleteAlarms(config, processCompartments)

        print_header("Deleting Notifications at " + time.strftime("%D %H:%M:%S", time.localtime()), 1)
        DeleteNotifications(config, processCompartments)

        print_header("Deleting Events at " + time.strftime("%D %H:%M:%S", time.localtime()), 1)
        DeleteEvents(config, processCompartments)

        print_header("Deleting Policies at " + time.strftime("%D %H:%M:%S", time.localtime()), 1)
        DeletePolicies(config, processCompartments)

        print_header("Deleting Log Groups at " + time.strftime("%D %H:%M:%S", time.localtime()), 1)
        DeleteLogGroups(config, processCompartments)

        print_header("Deleting Application Performance Monitoring at " + time.strftime("%D %H:%M:%S", time.localtime()), 1)
        DeleteAPM(config, processCompartments)

        # delete tags and namespace only if home region
        if region == homeregion:
            print_header("Deleting Tag Namespaces at " + time.strftime("%D %H:%M:%S", time.localtime()), 1)
            DeleteTagDefaults(config, processCompartments)
            DeleteTagNameSpaces(config, processCompartments)

    print("Hopefully deleting compartments, if empty at " + time.strftime("%D %H:%M:%S", time.localtime()), 1)
    config["region"] = homeregion
    DeleteCompartments(config, processCompartments, DeleteCompartmentOCID)

else:
    print("ok, doing nothing")
