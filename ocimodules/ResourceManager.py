import oci
import time

WaitRefresh = 10


##############################################
# DeleteStacks
##############################################
def DeleteStacks(config, Compartments):
    AllItems = []
    object = oci.resource_manager.ResourceManagerClient(config)

    print("Getting all Resource Stacks")
    for Compartment in Compartments:
        items = oci.pagination.list_call_get_all_results(object.list_stacks, compartment_id=Compartment.id).data
        for item in items:
            if (item.lifecycle_state != "DELETED"):
                AllItems.append(item)
                print("- {} - {}".format(item.display_name, item.lifecycle_state))

    itemsPresent = True

    while itemsPresent:
        count = 0
        for item in AllItems:
            try:
                itemstatus = object.get_stack(stack_id=item.id).data
                if itemstatus.lifecycle_state != "DELETED":
                    if itemstatus.lifecycle_state != "DELETING":
                        try:
                            print("Deleting: {}".format(itemstatus.display_name))
                            object.delete_stack(stack_id=itemstatus.id)
                        except Exception:
                            print("error trying to delete: {}".format(itemstatus.display_name))
                    else:
                        print("{} = {}".format(itemstatus.display_name, itemstatus.lifecycle_state))
                    count = count + 1
            except Exception:
                print("error getting : {}".format(item.display_name))
        if count > 0:
            print("Waiting for all Objects to be deleted...")
            time.sleep(WaitRefresh)
        else:
            itemsPresent = False
    print("All Resource Stacks Objects deleted!")

def DeleteSourceProviders(config, Compartments):
    AllItems = []
    object = oci.resource_manager.ResourceManagerClient(config)

    print("Getting all Source Providers")
    for Compartment in Compartments:
        items = oci.pagination.list_call_get_all_results(object.list_configuration_source_providers, compartment_id=Compartment.id).data
        for item in items:
                AllItems.append(item)
                print("- {} - {}".format(item.display_name, item.lifecycle_state))

    itemsPresent = True

    while itemsPresent:
        count = 0
        for item in AllItems:
            print (item)
            # try:
            print("Deleting: {} - {}".format(item.display_name, item.id))
            object.delete_configuration_source_provider(configuration_source_provider_id=item.id)
            # except Exception:
            #     print("error trying to delete: {}".format(item.display_name))
        if count > 0:
            print("Waiting for all Objects to be deleted...")
            time.sleep(WaitRefresh)
        else:
            itemsPresent = False
    print("All Source Provider Objects deleted!")
