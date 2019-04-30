import oci
import time

WaitRefresh = 10

def DeleteWAFs(config, Compartments):
    AllItems = []
    object = oci.waas.WaasClient(config)

    #functions.clear()
    print ("Getting all WAF Policy objects")
    for Compartment in Compartments:
        items = oci.pagination.list_call_get_all_results(object.list_waas_policies, compartment_id=Compartment.id).data
        for item in items:
            if (item.lifecycle_state != "DELETED"):
                AllItems.append(item)
                print("- {} - {}".format(item.display_name, item.lifecycle_state))

    itemsPresent = True

    while itemsPresent:
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

    print ("Getting all Healthchecks HTTP monitor objects")
    for Compartment in Compartments:
        items = oci.pagination.list_call_get_all_results(object.list_http_monitors, compartment_id=Compartment.id).data
        for item in items:
                AllItems.append(item)
                print("- {}".format(item.display_name))

    itemsPresent = True

    while itemsPresent:
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


def DeleteTrafficSteerings(config, Compartments):
    AllItems = []
    object = oci.dns.DnsClient(config)

    print ("Getting all Traffic Steering Policy objects")
    for Compartment in Compartments:
        items = oci.pagination.list_call_get_all_results(object.list_steering_policies, compartment_id=Compartment.id).data
        for item in items:
            if (item.lifecycle_state != "DELETED"):
                AllItems.append(item)
                print("- {} - {}".format(item.display_name, item.lifecycle_state))

    itemsPresent = True

    while itemsPresent:
        count = 0
        for item in AllItems:
            try:
                itemstatus = object.get_steering_policy(steering_policy_id=item.id).data
                if itemstatus.lifecycle_state != "DELETED":
                    if itemstatus.lifecycle_state != "DELETING":
                        try:
                            print ("Deleting: {}".format(itemstatus.display_name))
                            object.delete_steering_policy(steering_policy_id=itemstatus.id)
                        except:
                            print ("error trying to delete: {}".format(itemstatus.display_name))
                    else:
                        print("{} = {}".format(itemstatus.display_name, itemstatus.lifecycle_state))
                    count = count + 1
            except:
                print ("error getting : {}, probably already deleted".format(item.display_name))
        if count > 0 :
            print ("Waiting for all Objects to be deleted...")
            time.sleep(WaitRefresh)
        else:
            itemsPresent = False
    print ("All Objects deleted!")

def DeleteZones(config, Compartments):
    AllItems = []
    object = oci.dns.DnsClient(config)

    print ("Getting all DNS Zone objects, this can be slow, be patient")
    for Compartment in Compartments:
        items = oci.pagination.list_call_get_all_results(object.list_zones, compartment_id=Compartment.id).data
        for item in items:
            if (item.lifecycle_state != "DELETED"):
                AllItems.append(item)
                print("- {} - {}".format(item.name, item.lifecycle_state))

    itemsPresent = True

    while itemsPresent:
        count = 0
        for item in AllItems:
            try:
                itemstatus = object.get_zone(zone_name_or_id=item.id).data
                if itemstatus.lifecycle_state != "DELETED":
                    if itemstatus.lifecycle_state != "DELETING":
                        try:
                            print ("Deleting: {}".format(itemstatus.name))
                            object.delete_zone(zone_name_or_id=itemstatus.id)
                        except:
                            print ("error trying to delete: {}".format(itemstatus.name))
                    else:
                        print("{} = {}".format(itemstatus.name, itemstatus.lifecycle_state))
                    count = count + 1
            except:
                print ("error getting : {}, probably already deleted".format(item.name))
        if count > 0 :
            print ("Waiting for all Objects to be deleted...")
            time.sleep(WaitRefresh)
        else:
            itemsPresent = False
    print ("All Objects deleted!")



