import oci
import time

WaitRefresh = 10


##############################################
# DeleteDataCatalog
##############################################
def DeleteDataCatalog(config, Compartments):
    AllItems = []
    object = oci.data_catalog.DataCatalogClient(config)

    print("Getting all Data Catalog objects")
    for Compartment in Compartments:
        try:
            items = oci.pagination.list_call_get_all_results(object.list_catalogs, compartment_id=Compartment.id).data
            for item in items:
                if (item.lifecycle_state != "DELETED"):
                    AllItems.append(item)
                    print("- {} - {}".format(item.display_name, item.lifecycle_state))
        except Exception:
            print("Not possible to get Data Catalogs, likely not available in this region")

    itemsPresent = True

    while itemsPresent:
        count = 0
        for item in AllItems:
            try:
                itemstatus = object.get_catalog(catalog_id=item.id).data
                if itemstatus.lifecycle_state != "DELETED":
                    if itemstatus.lifecycle_state != "DELETING":
                        try:
                            print("Deleting: {}".format(itemstatus.display_name))
                            object.delete_catalog(catalog_id=itemstatus.id)
                        except Exception:
                            print("error trying to delete: {}".format(itemstatus.display_name))
                    else:
                        print("{} = {}".format(itemstatus.display_name, itemstatus.lifecycle_state))
                    count = count + 1
            except Exception:

                print("-----------------> error deleting {}, probably already deleted.".format(item.display_name))
        if count > 0:
            print("Waiting for all Objects to be deleted...")
            time.sleep(WaitRefresh)
        else:
            itemsPresent = False
    print("All DataCatalog Objects deleted!")
