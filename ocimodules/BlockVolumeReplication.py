import oci
import time

WaitRefresh = 15
MaxIDeleteIteration = 20

def RemoveReplication(config, signer, Compartments):
    AllVolumes = []
    object = oci.core.BlockstorageClient(config, signer=signer)
    identity = oci.identity.IdentityClient(config, signer=signer)
    for C in Compartments:
        Compartment = C.details
        ads = identity.list_availability_domains(compartment_id=Compartment.id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY).data
        for ad in ads:
            # Remove Replicas from Volume Groups
            print("Finding volume group replications in {}                   ".format(ad.name), end = "\r")
            volumes = object.list_volume_groups(availability_domain=ad, compartment_id=Compartment.id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY).data
            for v in volumes:
                if v.volume_group_replicas is not None:
                    try:
                        print ("Removing replicas from volume group: {}                  ".format(v.display_name))
                        updatedetails = oci.core.models.UpdateVolumeGroupDetails()
                        updatedetails.volume_group_replicas = []
                        response = object.update_volume_group(volume_group_id=v.id, update_volume_group_details=updatedetails, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY)
                        wait = True
                        while wait:
                            volinfo = object.get_volume_group(volume_group_id=v.id).data
                            if volinfo.volume_group_replicas is None:
                                wait = False
                            else:
                                print ("Waiting for replication to be terminated..            ", end = "\r")
                            time.sleep(2)

                    except oci.exceptions.ServiceError as response:
                        if response.code == 404:
                            print("No items found in compartment {}   ".format(Compartment.name), end="\r")
                        else:
                            print("error {}-{} trying to delete: {}".format(response.code, response.message, "volume group replication"))
            # Remove Replicas from Volumes
            print("Finding block volume replications in {}                             ".format(ad.name), end = "\r")
            volumes = object.list_volumes(availability_domain=ad, compartment_id=Compartment.id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY).data
            for v in volumes:
                if v.block_volume_replicas is not None:
                    try:
                        print ("Removing replicas from block volume: {}                   ".format(v.display_name))
                        updatedetails = oci.core.models.UpdateVolumeDetails()
                        updatedetails.block_volume_replicas = []
                        response = object.update_volume(volume_id=v.id, update_volume_details=updatedetails, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY)
                        wait = True
                        while wait:
                            volinfo = object.get_volume(volume_id=v.id).data
                            if volinfo.block_volume_replicas is None:
                                wait = False
                            else:
                                print("Waiting for replication to be terminated..            ", end="\r")
                            time.sleep(2)

                    except oci.exceptions.ServiceError as response:
                        if response.code == 404:
                            print("No items found in compartment {}   ".format(Compartment.name), end="\r")
                        else:
                            print("error {}-{} trying to delete: {}".format(response.code, response.message, "block volume replication"))
            # Remove Replicas from Boot Volumes
            print("Finding boot volume replications in {}                                 ".format(ad.name), end = "\r")
            volumes = object.list_boot_volumes(availability_domain=ad, compartment_id=Compartment.id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY).data
            for v in volumes:
                if v.boot_volume_replicas is not None:
                    try:
                        print ("Removing replicas from boot volume: {}                     ".format(v.display_name))
                        updatedetails = oci.core.models.UpdateBootVolumeDetails()
                        updatedetails.boot_volume_replicas = []
                        response = object.update_boot_volume(boot_volume_id=v.id, update_boot_volume_details=updatedetails, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY)
                        wait = True
                        while wait:
                            volinfo = object.get_boot_volume(boot_volume_id=v.id).data
                            if volinfo.boot_volume_replicas is None:
                                wait = False
                            else:
                                print("Waiting for replication to be terminated..            ", end="\r")
                            time.sleep(2)
                    except oci.exceptions.ServiceError as response:
                        if response.code == 404:
                            print("No items found in compartment {}   ".format(Compartment.name), end="\r")
                        else:
                            print("error {}-{} trying to delete: {}".format(response.code, response.message, "boot volume replication"))









