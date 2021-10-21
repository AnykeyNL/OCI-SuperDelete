# delete GoldenGate on 2021-08-23
import oci
import time

WaitRefresh = 15


####################################################
# DeleteGGDeployments
####################################################
def DeleteGGDeployments(config, Compartments):
    AllItems = []
    object = oci.golden_gate.GoldenGateClient(config)

    print("Getting all GGDeployments")
    for Compartment in Compartments:
        try:
            items = oci.pagination.list_call_get_all_results(object.list_deployments,
                                                             compartment_id=Compartment.id).data
            for item in items:
                if (item.lifecycle_state != "DELETED"):
                    AllItems.append(item)
                    print("- {} - {}".format(item.display_name, item.lifecycle_state))
            itemsPresent = True
        except Exception:
            print("Error getting all GGDeployments, likely service does not exist in this Region")
            itemsPresent = False

    while itemsPresent:
        count = 0
        for item in AllItems:
            try:
                itemstatus = object.get_deployment(deployment_id=item.id).data
                if itemstatus.lifecycle_state != "DELETED":
                    if itemstatus.lifecycle_state != "DELETING":
                        try:
                            print("Deleting: {}".format(itemstatus.display_name))
                            object.delete_deployment(deployment_id=itemstatus.id)
                        except Exception:
                            print("error trying to delete: {}".format(itemstatus.display_name))
                    else:
                        print("{} = {}".format(itemstatus.display_name, itemstatus.lifecycle_state))
                    count = count + 1
            except Exception:

                print("-----------------> error deleting {}, probably already deleted: {}".format(item.display_name, item.lifecycle_state))
        if count > 0:
            print("Waiting for all Objects to be deleted...")
            time.sleep(WaitRefresh)
        else:
            itemsPresent = False
    print("All Objects deleted!")


####################################################
# DeleteGGDeploymentsbak
####################################################
def DeleteGGDeploymentsbak(config, Compartments):
    AllItems = []
    object = oci.golden_gate.GoldenGateClient(config)

    print("Getting all GGDeploymentsbak")
    for Compartment in Compartments:
        try:
            items = oci.pagination.list_call_get_all_results(object.list_deployment_backups,
                                                             compartment_id=Compartment.id).data
            for item in items:
                if (item.lifecycle_state != "DELETED"):
                    AllItems.append(item)
                    print("- {} - {}".format(item.display_name, item.lifecycle_state))
            itemsPresent = True
        except Exception:
            print("Error getting all GGDeploymentsbak, likely service does not exist in this Region")
            itemsPresent = False

    while itemsPresent:
        count = 0
        for item in AllItems:
            try:
                itemstatus = object.get_deployment_backup(deployment_backup_id=item.id).data
                if itemstatus.lifecycle_state != "DELETED":
                    if itemstatus.lifecycle_state != "DELETING":
                        try:
                            print("Deleting: {}".format(itemstatus.display_name))
                            object.delete_deployment_backup(deployment_backup_id=itemstatus.id)
                        except Exception:
                            print("error trying to delete: {}".format(itemstatus.display_name))
                    else:
                        print("{} = {}".format(itemstatus.display_name, itemstatus.lifecycle_state))
                    count = count + 1
            except Exception:

                print("-----------------> error deleting {}, probably already deleted: {}".format(item.display_name, item.lifecycle_state))
        if count > 0:
            print("Waiting for all Objects to be deleted...")
            time.sleep(WaitRefresh)
        else:
            itemsPresent = False
    print("All Objects deleted!")


####################################################
# DeleteGGRegistered
####################################################
def DeleteGGRegistered(config, Compartments):
    AllItems = []
    object = oci.golden_gate.GoldenGateClient(config)

    print("Getting all GGRgeistered")
    for Compartment in Compartments:
        try:
            items = oci.pagination.list_call_get_all_results(object.list_database_registrations,
                                                             compartment_id=Compartment.id).data
            for item in items:
                if (item.lifecycle_state != "DELETED"):
                    AllItems.append(item)
                    print("- {} - {}".format(item.display_name, item.lifecycle_state))
            itemsPresent = True
        except Exception:
            print("Error getting all GGRegistered, likely service does not exist in this Region")
            itemsPresent = False

    while itemsPresent:
        count = 0
        for item in AllItems:
            try:
                itemstatus = object.get_database_registration(database_registration_id=item.id).data
                if itemstatus.lifecycle_state != "DELETED":
                    if itemstatus.lifecycle_state != "DELETING":
                        try:
                            print("Deleting: {}".format(itemstatus.display_name))
                            object.delete_database_registration(database_registration_id=itemstatus.id)
                        except Exception:
                            print("error trying to delete: {}".format(itemstatus.display_name))
                    else:
                        print("{} = {}".format(itemstatus.display_name, itemstatus.lifecycle_state))
                    count = count + 1
            except Exception:

                print("-----------------> error deleting {}, probably already deleted: {}".format(item.display_name, item.lifecycle_state))
        if count > 0:
            print("Waiting for all Objects to be deleted...")
            time.sleep(WaitRefresh)
        else:
            itemsPresent = False
    print("All Objects deleted!")
