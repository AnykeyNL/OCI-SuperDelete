import oci
import time

WaitRefresh = 10
MaxIDeleteIteration = 5


###########################################
# DeleteWAFs
###########################################
def DeleteWAFs(config, Compartments):
    AllItems = []
    object = oci.waas.WaasClient(config)

    # functions.clear()
    print("Getting all WAF Policy objects")
    for Compartment in Compartments:
        items = []
        try:
            items = oci.pagination.list_call_get_all_results(object.list_waas_policies, compartment_id=Compartment.id).data
        except Exception:
            print("Error listing compartment {}".format(Compartment.name))
            continue
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
                itemstatus = object.get_waas_policy(waas_policy_id=item.id).data
                if itemstatus.lifecycle_state != "DELETED":
                    if itemstatus.lifecycle_state != "DELETING":
                        try:
                            print("Deleting: {}".format(itemstatus.display_name))
                            object.delete_waas_policy(waas_policy_id=itemstatus.id)
                        except Exception:
                            print("error trying to delete: {}".format(itemstatus.display_name))
                    else:
                        print("{} = {}".format(itemstatus.display_name, itemstatus.lifecycle_state))
                    count = count + 1
            except Exception:
                print("error getting : {}".format(item.display_name))
        if count > 0:
            print("Waiting for all Objects to be deleted..." + (" Iteration " + str(iteration) + " of " + str(MaxIDeleteIteration) if iteration > 0 else ""))
            time.sleep(WaitRefresh)
            iteration += 1

            if iteration >= MaxIDeleteIteration:
                print("Some WAF Policy not deleted, skipping!")
                return
        else:
            itemsPresent = False
    print("All WAF Policy Objects deleted!")


###########################################
# DeleteHTTPHealthchecks
###########################################
def DeleteHTTPHealthchecks(config, Compartments):
    AllItems = []
    object = oci.healthchecks.HealthChecksClient(config)
    currentregion = config['region']
    print("Getting all Healthchecks HTTP monitor objects")
    for Compartment in Compartments:
        items = []
        try:
            items = oci.pagination.list_call_get_all_results(object.list_http_monitors, compartment_id=Compartment.id, home_region=currentregion).data
        except Exception:
            print("Error listing compartment {}".format(Compartment.name))
            continue
        for item in items:
            AllItems.append(item)
            print("- {}".format(item.display_name))

    itemsPresent = True
    iteration = 0

    while itemsPresent:
        count = 0
        for item in AllItems:
            try:
                itemstatus = object.get_http_monitor(monitor_id=item.id).data
                try:
                    print("Deleting: {}".format(itemstatus.display_name))
                    object.delete_http_monitor(monitor_id=itemstatus.id)
                except Exception:
                    print("error trying to delete: {}".format(itemstatus.display_name))
                count = count + 1
            except Exception:
                print("Deleted : {}".format(item.display_name))
        if count > 0:
            print("Waiting for all Objects to be deleted..." + (" Iteration " + str(iteration) + " of " + str(MaxIDeleteIteration) if iteration > 0 else ""))
            time.sleep(WaitRefresh)
            iteration += 1

            if iteration >= MaxIDeleteIteration:
                print("Some Healthchecks HTTP monitor not deleted, skipping!")
                return
        else:
            itemsPresent = False
    print("All Healthchecks HTTP monitor Objects deleted!")


###########################################
# DeletePINGHealthchecks
###########################################
def DeletePINGHealthchecks(config, Compartments):
    AllItems = []
    object = oci.healthchecks.HealthChecksClient(config)
    currentregion = config['region']
    # functions.clear()
    print("Getting all Healthchecks PING monitor objects")
    for Compartment in Compartments:
        items = []
        try:
            items = oci.pagination.list_call_get_all_results(object.list_ping_monitors, compartment_id=Compartment.id, home_region=currentregion).data
        except Exception:
            print("Error listing compartment {}".format(Compartment.name))
            continue
        for item in items:
            AllItems.append(item)
            print("- {}".format(item.display_name))

    itemsPresent = True
    iteration = 0

    while itemsPresent:
        count = 0
        for item in AllItems:
            try:
                itemstatus = object.get_ping_monitor(monitor_id=item.id).data
                try:
                    print("Deleting: {}".format(itemstatus.display_name))
                    object.delete_ping_monitor(monitor_id=itemstatus.id)
                except Exception:
                    print("error trying to delete: {}".format(itemstatus.display_name))
                count = count + 1
            except Exception:
                print("Deleted : {}".format(item.display_name))
        if count > 0:
            print("Waiting for all Objects to be deleted..." + (" Iteration " + str(iteration) + " of " + str(MaxIDeleteIteration) if iteration > 0 else ""))
            time.sleep(WaitRefresh)
            iteration += 1

            if iteration >= MaxIDeleteIteration:
                print("Some Healthchecks PING monitor not deleted, skipping!")
                return
        else:
            itemsPresent = False
    print("All Healthchecks PING monitor Objects deleted!")


###########################################
# DeleteTrafficSteeringsAttachments
###########################################
def DeleteTrafficSteeringsAttachments(config, Compartments):
    AllItems = []
    object = oci.dns.DnsClient(config)

    print("Getting all Traffic Steering Policy Attachment objects")
    for Compartment in Compartments:
        try:
            items = oci.pagination.list_call_get_all_results(object.list_steering_policy_attachments, compartment_id=Compartment.id).data
            for item in items:
                if (item.lifecycle_state != "DELETING"):
                    AllItems.append(item)
                    print("- {} - {}".format(item.display_name, item.lifecycle_state))
        except Exception:
            print("error getting steering policy attachements")

    itemsPresent = True
    iteration = 0

    while itemsPresent:
        count = 0
        for item in AllItems:
            try:
                itemstatus = object.get_steering_policy_attachment(steering_policy_attachment_id=item.id).data
                # if itemstatus.lifecycle_state != "DELETED":
                if itemstatus.lifecycle_state != "DELETING":
                    try:
                        print("Deleting: {}".format(itemstatus.display_name))
                        object.delete_steering_policy_attachment(steering_policy_attachment_id=itemstatus.id)
                    except Exception:
                        print("error trying to delete: {}".format(itemstatus.display_name))
                else:
                    print("{} = {}".format(itemstatus.display_name, itemstatus.lifecycle_state))
                count = count + 1
            except Exception:
                print("error getting : {}, probably already deleted".format(item.display_name))
        if count > 0:
            print("Waiting for all Objects to be deleted..." + (" Iteration " + str(iteration) + " of " + str(MaxIDeleteIteration) if iteration > 0 else ""))
            time.sleep(WaitRefresh)
            iteration += 1

            if iteration >= MaxIDeleteIteration:
                print("Some Traffic Steering Policy Attachment not deleted, skipping!")
                return
        else:
            itemsPresent = False

    print("All Traffic Steering Policy Attachment Objects deleted!")


###########################################
# DeleteTrafficSteerings
###########################################
def DeleteTrafficSteerings(config, Compartments):
    AllItems = []
    object = oci.dns.DnsClient(config)

    print("Getting all Traffic Steering Policy objects")
    for Compartment in Compartments:
        items = []
        try:
            items = oci.pagination.list_call_get_all_results(object.list_steering_policies, compartment_id=Compartment.id).data
        except Exception:
            print("Error listing compartment {}".format(Compartment.name))
            continue

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
                itemstatus = object.get_steering_policy(steering_policy_id=item.id).data
                if itemstatus.lifecycle_state != "DELETED":
                    if itemstatus.lifecycle_state != "DELETING":
                        try:
                            print("Deleting: {}".format(itemstatus.display_name))
                            object.delete_steering_policy(steering_policy_id=itemstatus.id)
                        except Exception:
                            print("error trying to delete: {}".format(itemstatus.display_name))
                    else:
                        print("{} = {}".format(itemstatus.display_name, itemstatus.lifecycle_state))
                    count = count + 1
            except Exception:
                print("error getting : {}, probably already deleted".format(item.display_name))
        if count > 0:
            print("Waiting for all Objects to be deleted..." + (" Iteration " + str(iteration) + " of " + str(MaxIDeleteIteration) if iteration > 0 else ""))
            time.sleep(WaitRefresh)
            iteration += 1

            if iteration >= MaxIDeleteIteration:
                print("Some Traffic Steering Policy not deleted, skipping!")
                return
        else:
            itemsPresent = False
    print("All Traffic Steering Policy Objects deleted!")


###########################################
# DeleteZones
###########################################
def DeleteZones(config, Compartments):
    AllItems = []
    object = oci.dns.DnsClient(config)

    print("Getting all DNS Zone objects, this can be slow, be patient")
    for Compartment in Compartments:
        items = []
        try:
            items = oci.pagination.list_call_get_all_results(object.list_zones, compartment_id=Compartment.id).data
        except Exception:
            print("Error listing compartment {}".format(Compartment.name))
            continue

        for item in items:
            if (item.lifecycle_state != "DELETED"):
                AllItems.append(item)
                print("- {} - {}".format(item.name, item.lifecycle_state))

    itemsPresent = True
    iteration = 0

    while itemsPresent:
        count = 0
        for item in AllItems:
            try:
                itemstatus = object.get_zone(zone_name_or_id=item.id).data
                if not itemstatus.is_protected:
                    if itemstatus.lifecycle_state != "DELETED":
                        if itemstatus.lifecycle_state != "DELETING":
                            try:
                                print("Deleting: {}".format(itemstatus.name))
                                object.delete_zone(zone_name_or_id=itemstatus.id)
                            except Exception:
                                print("error trying to delete: {}".format(itemstatus.name))
                        else:
                            print("{} = {}".format(itemstatus.name, itemstatus.lifecycle_state))
                        count = count + 1
                else:
                    print("ignoring protected zone {}".format(itemstatus.name))
            except Exception:
                print("error getting : {}, probably already deleted".format(item.name))
        if count > 0:
            print("Waiting for all Objects to be deleted..." + (" Iteration " + str(iteration) + " of " + str(MaxIDeleteIteration) if iteration > 0 else ""))
            time.sleep(WaitRefresh)
            iteration += 1

            if iteration >= MaxIDeleteIteration:
                print("Some DNS Zones Objects not deleted, skipping!")
                return
        else:
            itemsPresent = False
    print("All DNS Zones Objects deleted!")


###########################################
# DeleteDNSViews
###########################################
def DeleteDNSViews(config, Compartments):
    AllItems = []
    object = oci.dns.DnsClient(config)

    print("Getting all DNS View objects, this can be slow, be patient")
    for Compartment in Compartments:
        items = []
        try:
            items = oci.pagination.list_call_get_all_results(object.list_views, compartment_id=Compartment.id, scope="PRIVATE").data
        except Exception:
            print("Error listing compartment {}".format(Compartment.name))
            continue
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
                itemstatus = object.get_view(view_id=item.id).data
                if not itemstatus.is_protected:
                    if itemstatus.lifecycle_state != "DELETED":
                        if itemstatus.lifecycle_state != "DELETING":
                            try:
                                print("Deleting: {}".format(itemstatus.display_name))
                                object.delete_view(view_id=itemstatus.id)
                            except Exception:
                                print("error trying to delete: {}".format(itemstatus.display_name))
                        else:
                            print("{} = {}".format(itemstatus.display_name, itemstatus.lifecycle_state))
                        count = count + 1
                else:
                    print("Ignoring protected view {}".format(itemstatus.display_name))
            except Exception:
                print("error getting : {}, probably already deleted".format(item.display_name))
        if count > 0:
            print("Waiting for all Objects to be deleted..." + (" Iteration " + str(iteration) + " of " + str(MaxIDeleteIteration) if iteration > 0 else ""))
            time.sleep(WaitRefresh)
            iteration += 1

            if iteration >= MaxIDeleteIteration:
                print("Some DNS View not deleted, skipping!")
                return
        else:
            itemsPresent = False
    print("All DNS View Objects deleted!")
