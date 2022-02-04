import oci
import time

WaitRefresh = 15


##############################################
# DeleteMySQL
##############################################
def DeleteMySQL(config, Compartments):
    AllItems = []
    object = oci.mysql.DbSystemClient(config)

    print("Getting all MySQL Services")
    for Compartment in Compartments:
        try:
            items = oci.pagination.list_call_get_all_results(object.list_db_systems, compartment_id=Compartment.id).data
            for item in items:
                if (item.lifecycle_state != "DELETED"):
                    AllItems.append(item)
                    print("- {} - {}".format(item.display_name, item.lifecycle_state))
        except Exception:
            print("MSQL Service likely does not exist in this region")

    itemsPresent = True

    while itemsPresent:
        count = 0
        for item in AllItems:
            try:
                itemstatus = object.get_db_system(db_system_id=item.id).data
                if itemstatus.lifecycle_state != "DELETED":
                    if itemstatus.lifecycle_state != "DELETING":
                        try:
                            print("Deleting: {}".format(itemstatus.display_name))
                            object.delete_db_system(db_system_id=itemstatus.id)
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
    print("All MySQL Objects deleted!")
