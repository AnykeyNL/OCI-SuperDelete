import oci
import time

WaitRefresh = 15


##############################################
# DeleteSDDC
##############################################
def DeleteSDDC(config, Compartments):
    AllItems = []
    object = oci.ocvp.SddcClient(config)

    print("Getting all SDDC")
    for Compartment in Compartments:
        try:
            items = oci.pagination.list_call_get_all_results(object.list_sddcs, compartment_id=Compartment.id).data
            for item in items:
                if (item.lifecycle_state != "DELETED"):
                    AllItems.append(item)
                    print("- {} - {}".format(item.display_name, item.lifecycle_state))
            itemsPresent = True
        except Exception:
            print("Error getting all SDDC, likely service does not exist in this Region")
            itemsPresent = False

    while itemsPresent:
        count = 0
        for item in AllItems:
            try:
                itemstatus = object.get_sddc(sddc_id=item.id).data
                if itemstatus.lifecycle_state != "DELETED":
                    if itemstatus.lifecycle_state != "DELETING":
                        try:
                            print("Deleting: {}".format(itemstatus.display_name))
                            object.delete_sddc(sddc_id=itemstatus.id)
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
    print("All SDDC deleted!")


##############################################
# DeleteEsxiHost
##############################################
def DeleteEsxiHost(config, Compartments):
    AllItems = []
    object = oci.ocvp.EsxiHostClient(config)

    print("Getting all ESXi hosts")
    for Compartment in Compartments:
        try:
            items = oci.pagination.list_call_get_all_results(object.list_esxi_hosts, compartment_id=Compartment.id).data
            for item in items:
                if (item.lifecycle_state != "DELETED"):
                    AllItems.append(item)
                    print("- {} - {}".format(item.display_name, item.lifecycle_state))
            itemsPresent = True
        except Exception:
            print("Error getting all ESXi hosts, likely service does not exist in this Region")
            itemsPresent = False

    while itemsPresent:
        count = 0
        for item in AllItems:
            try:
                itemstatus = object.get_esxi_host(esxi_host_id=item.id).data
                if itemstatus.lifecycle_state != "DELETED":
                    if itemstatus.lifecycle_state != "DELETING":
                        try:
                            print("Deleting: {}".format(itemstatus.display_name))
                            object.delete_esxi_host(esxi_host_id=itemstatus.id)
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
    print("All ESXi hosts deleted!")

