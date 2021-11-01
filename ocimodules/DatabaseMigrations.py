import oci
import time

WaitRefresh = 15
MaxIDeleteIteration = 20


###########################################
# DeleteMigrations
###########################################
def DeleteMigrations(config, Compartments):
    AllItems = []
    object = oci.database_migration.DatabaseMigrationClient(config)

    print("Getting all Migration objects")
    for Compartment in Compartments:
        items = oci.pagination.list_call_get_all_results(object.list_migrations, compartment_id=Compartment.id).data
        for item in items:
            if (item.lifecycle_state != "DELETED"):
                AllItems.append(item)
                print("- {} - {}".format(item.display_name, item.lifecycle_state))

    itemsPresent = True
    iteration = 0
    while itemsPresent:
        count = 0
        for item in AllItems:
            try:
                itemstatus = object.get_migration(migration_id=item.id).data
                if itemstatus.lifecycle_state != "DELETED":
                    if itemstatus.lifecycle_state != "DELETING":
                        try:
                            print("Deleting: {}".format(itemstatus.display_name))
                            object.delete_migration(migration_id=itemstatus.id)
                        except Exception:
                            print("error trying to delete: {}".format(itemstatus.display_name))
                    else:
                        print("{} = {}".format(itemstatus.display_name, itemstatus.lifecycle_state))
                    count = count + 1
            except Exception:
                print("error deleting {}, probably already deleted".format(item.display_name))
        if count > 0:
            print("Waiting for all Objects to be deleted..." + (" Iteration " + str(iteration) + " of " + str(MaxIDeleteIteration) if iteration > 0 else ""))
            time.sleep(WaitRefresh)
            iteration += 1

            if iteration >= MaxIDeleteIteration:
                print("Some migrations not deleted, skipping!")
                return
        else:
            itemsPresent = False
    print("All migration Objects deleted!")


###########################################
# DeleteConnections
###########################################
def DeleteConections(config, Compartments):
    AllItems = []
    object = oci.database_migration.DatabaseMigrationClient(config)

    print("Getting all Database Connection objects")
    for Compartment in Compartments:
        items = oci.pagination.list_call_get_all_results(object.list_connections, compartment_id=Compartment.id).data
        for item in items:
            if (item.lifecycle_state != "DELETED"):
                AllItems.append(item)
                print("- {} - {}".format(item.display_name, item.lifecycle_state))

    itemsPresent = True
    iteration = 0

    while itemsPresent:
        count = 0
        for item in AllItems:
            try:
                itemstatus = object.get_connection(connection_id=item.id).data
                if itemstatus.lifecycle_state != "DELETED":
                    if itemstatus.lifecycle_state != "DELETING":
                        try:
                            print("Deleting: {}".format(itemstatus.display_name))
                            object.delete_connection(connection_id=itemstatus.id)
                        except Exception:
                            print("error trying to delete: {}".format(itemstatus.display_name))
                    else:
                        print("{} = {}".format(itemstatus.display_name, itemstatus.lifecycle_state))
                    count = count + 1
            except Exception:
                print("-----------------> error deleting {}, probably already deleted: {}".format(item.display_name, item.lifecycle_state))

        if count > 0:
            print("Waiting for all Objects to be deleted..." + (" Iteration " + str(iteration) + " of " + str(MaxIDeleteIteration) if iteration > 0 else ""))
            time.sleep(WaitRefresh)
            iteration += 1

            if iteration >= MaxIDeleteIteration:
                print("Some Connections not deleted, skipping!")
                return
        else:
            itemsPresent = False
    print("All Connection Objects deleted!")

