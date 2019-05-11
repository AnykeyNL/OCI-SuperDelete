import oci
from ocimodules.functions import *
from ocimodules.EdgeServices import *
from ocimodules.ObjectStorage import *
from ocimodules.Instances import *
from ocimodules.Database import *
from ocimodules.IAM import *
from ocimodules.VCN import *
from ocimodules.BlockStorage import *

configfile = "~/.oci/config"
DeleteCompartmentOCID = "ocid1.compartment.oc1..aaaaaaaa456vlgfybg2obpz7hrwjrqcyzme5mtgtqcetgt4tl2bs3kubmmea"
config = oci.config.from_file(configfile)

print ("\n--[ Login check and getting all compartments from starting compartment ]--")
compartments = Login(config, DeleteCompartmentOCID)
processCompartments=[]

clear()

print ("\n--[ Compartments to process ]--")
for compartment in compartments:
    if compartment.lifecycle_state== "ACTIVE":
        processCompartments.append(compartment)
        print (compartment.name)


confirm = input ("\ntype yes to delete all contents from these compartments: ")

regions = ["eu-frankfurt-1", "uk-london-1"]

if confirm == "yes":

    for region in regions:

        print ("============[ Deleting resources in {} ]================".format(region))
        config["region"] = region

        print ("\n--[ Deleting Edge Services ]--")
        DeleteWAFs(config,processCompartments)
        DeleteHTTPHealthchecks(config, processCompartments)
        DeletePINGHealthchecks(config, processCompartments)
        DeleteTrafficSteerings(config, processCompartments)
        DeleteZones(config, processCompartments)

        print ("\n--[ Deleting Object Storage ]--")
        DeleteBuckets(config, processCompartments)

        print ("\n--[ Deleting Compute Instances ]--")
        DeleteInstancePools(config,processCompartments)
        DeleteInstanceConfigs(config, processCompartments)
        DeleteInstances(config,processCompartments)
        DeleteImages(config, processCompartments)
        DeleteBootVolumes(config, processCompartments)

        print ("\n--[ Deleting Database Instances ]--")
        DeleteDBCS(config,processCompartments)
        DeleteAutonomousDB(config,processCompartments)

        print ("\n--[ Deleting Block Volumes ]--")
        DeleteVolumes(config, processCompartments)

        print ("\n--[ Deleting VCNs ]--")
        DeleteVCN(config, processCompartments)


    print ("\n--[ Hopefully deleting compartments, if empty ]--")
    config["region"] = "eu-frankfurt-1"
    DeleteCompartments(config,processCompartments, DeleteCompartmentOCID)



