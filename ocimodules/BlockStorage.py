import oci
import time

WaitRefresh = 15


##############################################
# DeleteBootVolumes
##############################################
def DeleteBootVolumes(config, Compartments):
    AllItems = []
    object = oci.core.BlockstorageClient(config)
    identity = oci.identity.IdentityClient(config)

    print("Getting all Blockstorage objects")
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
                            print("Disable volume replication")
                            object.update_boot_volume(
                                boot_volume_id=itemstatus.id,
                                update_boot_volume_details=oci.core.models.UpdateBootVolumeDetails(boot_volume_replicas=[])
                            )
                            print("Deleting: {}".format(itemstatus.display_name))
                            object.delete_boot_volume(boot_volume_id=itemstatus.id)
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
    print("All BootVolumes Objects deleted!")


##############################################
# DeleteBlockVolumesBackups
##############################################
def DeleteBlockVolumesBackups(config, Compartments):
    AllItems = []
    object = oci.core.BlockstorageClient(config)

    print("Getting all Block Volumes Backup objects")
    for compartment in Compartments:
        items = oci.pagination.list_call_get_all_results(object.list_volume_backups, compartment_id=compartment.id).data
        for item in items:
            if (item.lifecycle_state != "TERMINATED"):
                AllItems.append(item)
                print("- {} - {}".format(item.display_name, item.lifecycle_state))

    itemsPresent = True

    while itemsPresent:
        count = 0
        for item in AllItems:
            try:
                itemstatus = object.get_volume_backup(volume_backup_id=item.id).data
                if itemstatus.lifecycle_state != "TERMINATED":
                    if itemstatus.lifecycle_state != "TERMINATING":
                        try:
                            print("Deleting: {}".format(itemstatus.display_name))
                            object.delete_volume_backup(volume_backup_id=itemstatus.id)
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
    print("All BlockVolumesBackups Objects deleted!")


##############################################
# DeleteBootVolumesBackups
##############################################
def DeleteBootVolumesBackups(config, Compartments):
    AllItems = []
    object = oci.core.BlockstorageClient(config)

    print("Getting all Boot Volumes Backup objects")
    for compartment in Compartments:
        items = oci.pagination.list_call_get_all_results(object.list_boot_volume_backups, compartment_id=compartment.id).data
        for item in items:
            if (item.lifecycle_state != "TERMINATED"):
                AllItems.append(item)
                print("- {} - {}".format(item.display_name, item.lifecycle_state))

    itemsPresent = True

    while itemsPresent:
        count = 0
        for item in AllItems:
            try:
                itemstatus = object.get_boot_volume_backup(boot_volume_backup_id=item.id).data
                if itemstatus.lifecycle_state != "TERMINATED":
                    if itemstatus.lifecycle_state != "TERMINATING":
                        try:
                            print("Deleting: {}".format(itemstatus.display_name))
                            object.delete_boot_volume_backup(boot_volume_backup_id=itemstatus.id)
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
    print("All BootVolumesBackups Objects deleted!")


##############################################
# DeleteVolumeGroups
##############################################
def DeleteVolumeGroups(config, Compartments):
    AllItems = []
    object = oci.core.BlockstorageClient(config)
    identity = oci.identity.IdentityClient(config)

    print("Getting all Block Volume Groups objects")
    for compartment in Compartments:
        ads = identity.list_availability_domains(compartment_id=compartment.id).data
        for ad in ads:
            items = oci.pagination.list_call_get_all_results(object.list_volume_groups, availability_domain=ad.name, compartment_id=compartment.id).data
            for item in items:
                if (item.lifecycle_state != "TERMINATED"):
                    AllItems.append(item)
                    print("- {} - {}".format(item.display_name, item.lifecycle_state))

    itemsPresent = True

    while itemsPresent:
        count = 0
        for item in AllItems:
            try:
                itemstatus = object.get_volume_group(volume_group_id=item.id).data
                if itemstatus.lifecycle_state != "TERMINATED":
                    if itemstatus.lifecycle_state != "TERMINATING":
                        try:
                            print("Deleting: {}".format(itemstatus.display_name))
                            object.delete_volume_group(volume_group_id=itemstatus.id)
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
    print("All VolumeGroups Objects deleted!")


##############################################
# DeleteVolumeGroupBackups
##############################################
def DeleteVolumeGroupBackups(config, Compartments):
    AllItems = []
    object = oci.core.BlockstorageClient(config)

    print("Getting all Block Volume Group Backups objects")
    for compartment in Compartments:
        items = oci.pagination.list_call_get_all_results(object.list_volume_group_backups, compartment_id=compartment.id).data
        for item in items:
            if (item.lifecycle_state != "TERMINATED"):
                AllItems.append(item)
                print("- {} - {}".format(item.display_name, item.lifecycle_state))

    itemsPresent = True

    while itemsPresent:
        count = 0
        for item in AllItems:
            try:
                itemstatus = object.get_volume_group_backup(volume_group_backup_id=item.id).data
                if itemstatus.lifecycle_state != "TERMINATED":
                    if itemstatus.lifecycle_state != "TERMINATING":
                        try:
                            print("Deleting: {}".format(itemstatus.display_name))
                            object.delete_volume_group_backup(volume_group_backup_id=itemstatus.id)
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
    print("All VolumeGroupBackups Objects deleted!")
