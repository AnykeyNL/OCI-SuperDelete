import oci
import time

WaitRefresh = 15

def DeleteInstancePools(config, Compartments):
    AllItems = []
    object = oci.core.ComputeManagementClient(config)

    print ("Getting all InstancePools objects")
    for Compartment in Compartments:
        items = oci.pagination.list_call_get_all_results(object.list_instance_pools, compartment_id=Compartment.id).data
        for item in items:
            if (item.lifecycle_state != "TERMINATED"):
                AllItems.append(item)
                print("- {} - {}".format(item.display_name, item.lifecycle_state))

    itemsPresent = True

    while itemsPresent:
        count = 0
        for item in AllItems:
            try:
                itemstatus = object.get_instance_pool(instance_pool_id=item.id).data
                if itemstatus.lifecycle_state != "TERMINATED":
                    if itemstatus.lifecycle_state != "TERMINATING":
                        try:
                            print ("Deleting: {}".format(itemstatus.display_name))
                            object.terminate_instance_pool(instance_pool_id=itemstatus.id)
                        except:
                            print ("error trying to delete: {}".format(itemstatus.display_name))
                    else:
                        print("{} = {}".format(itemstatus.display_name, itemstatus.lifecycle_state))
                    count = count + 1
            except:
                print ("error deleting {}, probably already deleted".format(item.display_name))
        if count > 0 :
            print ("Waiting for all Objects to be deleted...")
            time.sleep(WaitRefresh)
        else:
            itemsPresent = False
    print ("All Objects deleted!")

def DeleteInstanceConfigs(config, Compartments):
    AllItems = []
    object = oci.core.ComputeManagementClient(config)

    print ("Deleting all InstanceConfigurations")
    for Compartment in Compartments:
        items = oci.pagination.list_call_get_all_results(object.list_instance_configurations, compartment_id=Compartment.id).data
        for item in items:
                print("- {}".format(item.display_name))
                object.delete_instance_configuration(instance_configuration_id=item.id)

    print ("All Objects deleted!")

def DeleteInstances(config, Compartments):
    AllItems = []
    object = oci.core.ComputeClient(config)

    print ("Getting all Compute objects")
    for Compartment in Compartments:
        items = oci.pagination.list_call_get_all_results(object.list_instances, compartment_id=Compartment.id).data
        for item in items:
            if (item.lifecycle_state != "TERMINATED"):
                AllItems.append(item)
                print("- {} - {}".format(item.display_name, item.lifecycle_state))

    itemsPresent = True

    while itemsPresent:
        count = 0
        for item in AllItems:
            try:
                itemstatus = object.get_instance(instance_id=item.id).data
                if itemstatus.lifecycle_state != "TERMINATED":
                    if itemstatus.lifecycle_state != "TERMINATING":
                        try:
                            print ("Deleting: {}".format(itemstatus.display_name))
                            object.terminate_instance(instance_id=itemstatus.id)
                        except:
                            print ("error trying to delete: {}".format(itemstatus.display_name))
                    else:
                        print("{} = {}".format(itemstatus.display_name, itemstatus.lifecycle_state))
                    count = count + 1
            except:

                print ("-----------------> error deleting {}, probably already deleted: {}".format(item.display_name, item.lifecycle_state))
        if count > 0 :
            print ("Waiting for all Objects to be deleted...")
            time.sleep(WaitRefresh)
        else:
            itemsPresent = False
    print ("All Objects deleted!")

def DeleteImages(config, Compartments):
    AllItems = []
    object = oci.core.ComputeClient(config)

    print("Getting all Custom Image objects")
    for Compartment in Compartments:
        items = oci.pagination.list_call_get_all_results(object.list_images, compartment_id=Compartment.id).data
        for item in items:
            if item.operating_system_version == "Custom" or item.base_image_id:
                AllItems.append(item)

    itemsPresent = True

    while itemsPresent:
        count = 0
        for item in AllItems:
            try:
                itemstatus = object.get_image(image_id=item.id).data
                if itemstatus.lifecycle_state != "DELETED":
                        try:
                            print("Deleting: {}".format(itemstatus.display_name))
                            object.delete_image(image_id=itemstatus.id)
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


def DeleteVolumes(config, Compartments):
    AllItems = []
    object = oci.core.BlockstorageClient(config)

    print ("Getting all Compute objects")
    for Compartment in Compartments:
        items = oci.pagination.list_call_get_all_results(object.list_volumes, compartment_id=Compartment.id).data
        for item in items:
            if (item.lifecycle_state != "TERMINATED"):
                AllItems.append(item)
                print("- {} - {}".format(item.display_name, item.lifecycle_state))

    itemsPresent = True

    while itemsPresent:
        count = 0
        for item in AllItems:
            try:
                itemstatus = object.get_volume(volume_id=item.id).data
                if itemstatus.lifecycle_state != "TERMINATED":
                    if itemstatus.lifecycle_state != "TERMINATING":
                        try:
                            print ("Deleting: {}".format(itemstatus.display_name))
                            object.delete_volume(volume_id=itemstatus.id)
                        except:
                            print ("error trying to delete: {}".format(itemstatus.display_name))
                    else:
                        print("{} = {}".format(itemstatus.display_name, itemstatus.lifecycle_state))
                    count = count + 1
            except:
                print ("error deleting {}, probably already deleted".format(item.display_name))
        if count > 0 :
            print ("Waiting for all Objects to be deleted...")
            time.sleep(WaitRefresh)
        else:
            itemsPresent = False
    print ("All Objects deleted!")

def DeleteDedicatedVMHosts(config, Compartments):
    AllItems = []
    object = oci.core.ComputeClient(config)

    print ("Getting all Dedicated VM Hosts objects")
    for Compartment in Compartments:
        items = oci.pagination.list_call_get_all_results(object.list_dedicated_vm_hosts, compartment_id=Compartment.id).data
        for item in items:
            if (item.lifecycle_state != "DELETED"):
                AllItems.append(item)
                print("- {} - {}".format(item.display_name, item.lifecycle_state))

    itemsPresent = True

    while itemsPresent:
        count = 0
        for item in AllItems:
            try:
                itemstatus = object.get_dedicated_vm_host(dedicated_vm_host_id =item.id).data
                if itemstatus.lifecycle_state != "DELETED":
                    if itemstatus.lifecycle_state != "DELETING":
                        try:
                            print ("Deleting: {}".format(itemstatus.display_name))
                            object.delete_dedicated_vm_host(dedicated_vm_host_id=itemstatus.id)
                        except:
                            print ("error trying to delete: {}".format(itemstatus.display_name))
                    else:
                        print("{} = {}".format(itemstatus.display_name, itemstatus.lifecycle_state))
                    count = count + 1
            except:

                print ("-----------------> error deleting {}, probably already deleted: {}".format(item.display_name, item.lifecycle_state))
        if count > 0 :
            print ("Waiting for all Objects to be deleted...")
            time.sleep(WaitRefresh)
        else:
            itemsPresent = False
    print ("All Objects deleted!")