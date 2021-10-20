import oci
import time

WaitRefresh = 10


##############################################
# DeleteContainerRepositories
##############################################
def DeleteContainerRepositories(config, Compartments):
    AllItems = []
    object = oci.artifacts.ArtifactsClient(config)

    print("Getting all Container Repositories objects")
    for Compartment in Compartments:
        try:
            items = oci.pagination.list_call_get_all_results(object.list_container_repositories, compartment_id=Compartment.id).data
            for item in items:
                if (item.lifecycle_state != "DELETED"):
                    AllItems.append(item)
                    print("- {} - {}".format(item.display_name, item.lifecycle_state))
        except Exception:
            print("Error listing compartment {}".format(Compartment.name))
            continue

    itemsPresent = True

    while itemsPresent:
        count = 0
        for item in AllItems:
            try:
                itemstatus = object.get_container_repository(repository_id=item.id).data
                if itemstatus.lifecycle_state != "DELETED":
                    if itemstatus.lifecycle_state != "DELETING":
                        try:
                            print("Deleting: {}".format(itemstatus.display_name))
                            object.delete_container_repository(repository_id=itemstatus.id)
                        except Exception:
                            print("error trying to delete: {}".format(itemstatus.display_name))
                    else:
                        print("{} = {}".format(itemstatus.display_name, itemstatus.lifecycle_state))
                    count = count + 1
            except Exception:

                print("-----------------> error deleting {}, probably already deleted: {}.".format(item.display_name, item.lifecycle_state))
        if count > 0:
            print("Waiting for all Objects to be deleted...")
            time.sleep(WaitRefresh)
        else:
            itemsPresent = False
    print("All ContainerRepositories Objects deleted!")


##############################################
# DeleteRepositories
##############################################
def DeleteRepositories(config, Compartments):
    AllItems = []
    object = oci.artifacts.ArtifactsClient(config)

    print("Getting all Repositories objects")
    for Compartment in Compartments:
        try:
            items = oci.pagination.list_call_get_all_results(object.list_repositories, compartment_id=Compartment.id).data
            for item in items:
                if (item.lifecycle_state != "DELETED"):
                    AllItems.append(item)
                    print("- {} - {}".format(item.display_name, item.lifecycle_state))
        except Exception:
            print("Error listing compartment {}".format(Compartment.name))
            continue

    itemsPresent = True

    while itemsPresent:
        count = 0
        for item in AllItems:
            try:
                itemstatus = object.get_repository(repository_id=item.id).data
                if itemstatus.lifecycle_state != "DELETED":
                    if itemstatus.lifecycle_state != "DELETING":
                        try:
                            print("Deleting: {}".format(itemstatus.display_name))
                            object.delete_repository(repository_id=itemstatus.id)
                        except Exception:
                            print("error trying to delete: {}".format(itemstatus.display_name))
                    else:
                        print("{} = {}".format(itemstatus.display_name, itemstatus.lifecycle_state))
                    count = count + 1
            except Exception:

                print("-----------------> error deleting {}, probably already deleted: {}.".format(item.display_name, item.lifecycle_state))
        if count > 0:
            print("Waiting for all Objects to be deleted...")
            time.sleep(WaitRefresh)
        else:
            itemsPresent = False
    print("All Repositories Objects deleted!")


##############################################
# DeleteGenericArtifacts
##############################################
def DeleteGenericArtifacts(config, Compartments):
    AllItems = []
    object = oci.artifacts.ArtifactsClient(config)

    print("Getting all Repositories objects")
    for Compartment in Compartments:
        try:
            items = oci.pagination.list_call_get_all_results(object.list_generic_artifacts, compartment_id=Compartment.id).data
            for item in items:
                if (item.lifecycle_state != "DELETED"):
                    AllItems.append(item)
                    print("- {} - {}".format(item.display_name, item.lifecycle_state))
        except Exception:
            print("Error listing compartment {}".format(Compartment.name))
            continue

    itemsPresent = True

    while itemsPresent:
        count = 0
        for item in AllItems:
            try:
                itemstatus = object.get_generic_artifact(repository_id=item.id).data
                if itemstatus.lifecycle_state != "DELETED":
                    if itemstatus.lifecycle_state != "DELETING":
                        try:
                            print("Deleting: {}".format(itemstatus.display_name))
                            object.delete_generic_artifact(repository_id=itemstatus.id)
                        except Exception:
                            print("error trying to delete: {}".format(itemstatus.display_name))
                    else:
                        print("{} = {}".format(itemstatus.display_name, itemstatus.lifecycle_state))
                    count = count + 1
            except Exception:

                print("-----------------> error deleting {}, probably already deleted: {}.".format(item.display_name, item.lifecycle_state))
        if count > 0:
            print("Waiting for all Objects to be deleted...")
            time.sleep(WaitRefresh)
        else:
            itemsPresent = False
    print("All Artifacts Objects deleted!")
