import oci
import time

WaitRefresh = 15


##############################################
# DeleteMountTargets
##############################################
def DeleteMountTargets(config, Compartments):
    AllItems = []
    object = oci.file_storage.FileStorageClient(config)
    identity = oci.identity.IdentityClient(config)

    print("Getting all Mount Targets objects")
    for compartment in Compartments:
        ads = identity.list_availability_domains(compartment_id=compartment.id).data
        for ad in ads:
            items = oci.pagination.list_call_get_all_results(object.list_mount_targets, availability_domain=ad.name, compartment_id=compartment.id).data
            for item in items:
                if (item.lifecycle_state != "DELETED"):
                    AllItems.append(item)
                    print("- {} - {}".format(item.display_name, item.lifecycle_state))

    itemsPresent = True

    while itemsPresent:
        count = 0
        for item in AllItems:
            try:
                itemstatus = object.get_mount_target(mount_target_id=item.id).data
                if itemstatus.lifecycle_state != "DELETED":
                    if itemstatus.lifecycle_state != "DELETING":
                        try:
                            print("Deleting: {}".format(itemstatus.display_name))
                            object.delete_mount_target(mount_target_id=itemstatus.id)
                        except Exception:
                            print("error trying to delete: {}".format(itemstatus.display_name))
                    else:
                        print("{} = {}".format(itemstatus.display_name, itemstatus.lifecycle_state))
                    count = count + 1
            except Exception:
                print("error deleting {}, probably already deleted".format(item.display_name))
        if count > 0:
            print("Waiting for all Objects to be deleted...")
            time.sleep(WaitRefresh)
        else:
            itemsPresent = False
    print("All Mount Targets Objects deleted!")


##############################################
# DeleteFileStorage
##############################################
def DeleteFileStorage(config, Compartments):
    AllItems = []
    object = oci.file_storage.FileStorageClient(config)
    identity = oci.identity.IdentityClient(config)

    print("Getting all File Storage objects")
    for compartment in Compartments:
        ads = identity.list_availability_domains(compartment_id=compartment.id).data
        for ad in ads:
            items = oci.pagination.list_call_get_all_results(object.list_file_systems, availability_domain=ad.name, compartment_id=compartment.id).data
            for item in items:
                if (item.lifecycle_state != "DELETED"):
                    AllItems.append(item)
                    print("- {} - {}".format(item.display_name, item.lifecycle_state))

    itemsPresent = True

    while itemsPresent:
        count = 0
        for item in AllItems:
            try:
                itemstatus = object.get_file_system(file_system_id=item.id).data
                if itemstatus.lifecycle_state != "DELETED":
                    if itemstatus.lifecycle_state != "DELETING":
                        try:
                            print("Deleting: {}".format(itemstatus.display_name))
                            object.delete_file_system(file_system_id=itemstatus.id)
                        except Exception:
                            print("error trying to delete: {}".format(itemstatus.display_name))
                    else:
                        print("{} = {}".format(itemstatus.display_name, itemstatus.lifecycle_state))
                    count = count + 1
            except Exception:
                print("error deleting {}, probably already deleted".format(item.display_name))
        if count > 0:
            print("Waiting for all Objects to be deleted...")
            time.sleep(WaitRefresh)
        else:
            itemsPresent = False
    print("All File Storage Objects deleted!")
