import oci
import time
import functions

WaitRefresh = 10

def DeleteWAFs(config, Compartments):
    AllItems = []
    object = oci.waas.WaasClient(config)

    #functions.clear()
    print ("Getting all WAF Policy objects")
    for Compartment in Compartments:
        items = oci.pagination.list_call_get_all_results(object.list_waas_policies, compartment_id=Compartment.id).data
        for item in items:
            if (object.lifecycle_state != "DELETED"):
                AllItems.append(item)
                print("- {} - {}".format(item.display_name, item.lifecycle_state))

    itemsPresent = True

    while itemsPresent:
        #functions.clear()
        count = 0
        for item in AllItems:
            try:
                itemstatus = object.get_waas_policy(waas_policy_id=item.id).data
                if itemstatus.lifecycle_state != "DELETED":
                    if itemstatus.lifecycle_state != "DELETING":
                        try:
                            print ("Deleting: {}".format(itemstatus.display_name))
                            object.delete_waas_policy(waas_policy_id=itemstatus.id)
                        except:
                            print ("error trying to delete: {}".format(itemstatus.display_name))
                    else:
                        print("{} = {}".format(itemstatus.display_name, itemstatus.lifecycle_state))
                    count = count + 1
            except:
                print ("error getting : {}".format(item.display_name))
        if count > 0 :
            print ("Waiting for all Objects to be deleted...")
            time.sleep(WaitRefresh)
        else:
            itemsPresent = False
    print ("All Objects deleted!")

def DeleteHTTPHealthchecks(config, Compartments):
    AllItems = []
    object = oci.healthchecks.HealthChecksClient(config)

    #functions.clear()
    print ("Getting all Healthchecks HTTP monitor objects")
    for Compartment in Compartments:
        items = oci.pagination.list_call_get_all_results(object.list_http_monitors, compartment_id=Compartment.id).data
        for item in items:
                AllItems.append(item)
                print("- {}".format(item.display_name))

    itemsPresent = True

    while itemsPresent:
        #functions.clear()
        count = 0
        for item in AllItems:
            try:
                itemstatus = object.get_http_monitor(monitor_id=item.id).data
                try:
                    print ("Deleting: {}".format(itemstatus.display_name))
                    object.delete_http_monitor(monitor_id=itemstatus.id)
                except:
                    print ("error trying to delete: {}".format(itemstatus.display_name))
                count = count + 1
            except:
                print ("Deleted : {}".format(item.display_name))
        if count > 0 :
            print ("Waiting for all Objects to be deleted...")
            time.sleep(WaitRefresh)
        else:
            itemsPresent = False
    print ("All Objects deleted!")

def DeletePINGHealthchecks(config, Compartments):
    AllItems = []
    object = oci.healthchecks.HealthChecksClient(config)

    #functions.clear()
    print ("Getting all Healthchecks PING monitor objects")
    for Compartment in Compartments:
        items = oci.pagination.list_call_get_all_results(object.list_ping_monitors, compartment_id=Compartment.id).data
        for item in items:
                AllItems.append(item)
                print("- {}".format(item.display_name))

    itemsPresent = True

    while itemsPresent:
        #functions.clear()
        count = 0
        for item in AllItems:
            try:
                itemstatus = object.get_ping_monitor(monitor_id=item.id).data
                try:
                    print ("Deleting: {}".format(itemstatus.display_name))
                    object.delete_ping_monitor(monitor_id=itemstatus.id)
                except:
                    print ("error trying to delete: {}".format(itemstatus.display_name))
                count = count + 1
            except:
                print ("Deleted : {}".format(item.display_name))
        if count > 0 :
            print ("Waiting for all Objects to be deleted...")
            time.sleep(WaitRefresh)
        else:
            itemsPresent = False
    print ("All Objects deleted!")


