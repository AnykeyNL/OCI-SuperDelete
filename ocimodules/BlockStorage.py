import oci
import time

WaitRefresh = 15


def DeleteBootVolumes(config, Compartments):
    AllItems = []
    object = oci.core.BlockstorageClient(config)
    identity = oci.identity.IdentityClient(config)

    print ("Getting all Blockstorage objects")
    for compartment in Compartments:
        ads = identity.list_availability_domains(compartment_id=compartment.id).data
        for ad in ads:
            items = oci.pagination.list_call_get_all_results(object.list_boot_volumes, availability_domain=ad.name, compartment_id=compartment.id).data
            for item in items:
                if (item.lifecycle_state != "TERMINATED"):
                    AllItems.append(item)
                    print("- {} - {}".format(item.display_name, item.lifecycle_state))

    itemsPresent = True

    while itemsPresent:
        count = 0
        for item in AllItems:
            try:
                itemstatus = object.get_boot_volume(boot_volume_id=item.id).data
                if itemstatus.lifecycle_state != "TERMINATED":
                    if itemstatus.lifecycle_state != "TERMINATING":
                        try:
                            print("Deleting: {}".format(itemstatus.display_name))
                            object.delete_boot_volume(boot_volume_id=itemstatus.id)
                        except:
                            print("error trying to delete: {}".format(itemstatus.display_name))
                    else:
                        print("{} = {}".format(itemstatus.display_name, itemstatus.lifecycle_state))
                    count = count + 1
            except:
                print("error deleting {}, probably already deleted".format(item.display_name))
        if count > 0:
            print("Waiting for all Objects to be deleted...")
            time.sleep(WaitRefresh)
        else:
            itemsPresent = False
    print("All Objects deleted!")





