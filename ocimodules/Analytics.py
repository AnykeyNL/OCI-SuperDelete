import oci
import time

WaitRefresh = 10


####################################################
# DeleteAnalytics
####################################################
def DeleteAnalytics(config, Compartments):
    AllItems = []
    object = oci.analytics.AnalyticsClient(config)

    print("Getting all Analytics objects")
    for Compartment in Compartments:
        items = oci.pagination.list_call_get_all_results(object.list_analytics_instances, compartment_id=Compartment.id).data
        for item in items:
            if (item.lifecycle_state != "DELETED"):
                AllItems.append(item)
                print("- {} - {}".format(item.name, item.lifecycle_state))

    itemsPresent = True

    while itemsPresent:
        count = 0
        for item in AllItems:
            try:
                itemstatus = object.get_analytics_instance(analytics_instance_id=item.id).data
                if itemstatus.lifecycle_state != "DELETED":
                    if itemstatus.lifecycle_state != "DELETING":
                        try:
                            print("Deleting: {}".format(itemstatus.name))
                            object.delete_analytics_instance(analytics_instance_id=itemstatus.id)
                        except Exception:
                            print("error trying to delete: {}".format(itemstatus.name))
                    else:
                        print("{} = {}".format(itemstatus.name, itemstatus.lifecycle_state))
                    count = count + 1
            except Exception:

                print("-----------------> error deleting {}, probably already deleted: {}.".format(item.name, item.lifecycle_state))
        if count > 0:
            print("Waiting for all Objects to be deleted...")
            time.sleep(WaitRefresh)
        else:
            itemsPresent = False
    print("All Objects deleted!")


####################################################
# DeleteStreams
####################################################
def DeleteStreams(config, Compartments):
    AllItems = []
    object = oci.streaming.StreamAdminClient(config)

    print("Getting all Streaming objects")
    for Compartment in Compartments:
        items = oci.pagination.list_call_get_all_results(object.list_streams, compartment_id=Compartment.id).data
        for item in items:
            if (item.lifecycle_state != "DELETED"):
                AllItems.append(item)
                print("- {} - {}".format(item.name, item.lifecycle_state))

    itemsPresent = True

    while itemsPresent:
        count = 0
        for item in AllItems:
            try:
                itemstatus = object.get_stream(stream_id=item.id).data
                if itemstatus.lifecycle_state != "DELETED":
                    if itemstatus.lifecycle_state != "DELETING":
                        try:
                            print("Deleting: {}".format(itemstatus.name))
                            object.delete_stream(stream_id=itemstatus.id)
                        except Exception:
                            print("error trying to delete: {}".format(itemstatus.name))
                    else:
                        print("{} = {}".format(itemstatus.name, itemstatus.lifecycle_state))
                    count = count + 1
            except Exception:

                print("-----------------> error deleting {}, probably already deleted: {}.".format(item.name, item.lifecycle_state))
        if count > 0:
            print("Waiting for all Objects to be deleted...")
            time.sleep(WaitRefresh)
        else:
            itemsPresent = False
    print("All Objects deleted!")


####################################################
# DeleteStreamPools
####################################################
def DeleteStreamPools(config, Compartments):
    AllItems = []
    object = oci.streaming.StreamAdminClient(config)

    print("Getting all Stream Pool objects")
    for Compartment in Compartments:
        items = oci.pagination.list_call_get_all_results(object.list_stream_pools, compartment_id=Compartment.id).data
        for item in items:
            if (item.lifecycle_state != "DELETED"):
                AllItems.append(item)
                print("- {} - {}".format(item.name, item.lifecycle_state))

    itemsPresent = True

    while itemsPresent:
        count = 0
        for item in AllItems:
            try:
                itemstatus = object.get_stream_pool(stream_pool_id=item.id).data
                if itemstatus.lifecycle_state != "DELETED":
                    if itemstatus.lifecycle_state != "DELETING":
                        try:
                            print("Deleting: {}".format(itemstatus.name))
                            object.delete_stream_pool(stream_pool_id=itemstatus.id)
                        except Exception:
                            print("error trying to delete: {}".format(itemstatus.name))
                    else:
                        print("{} = {}".format(itemstatus.name, itemstatus.lifecycle_state))
                    count = count + 1
            except Exception:

                print("-----------------> error deleting {}, probably already deleted: {}.".format(item.name, item.lifecycle_state))
        if count > 0:
            print("Waiting for all Objects to be deleted...")
            time.sleep(WaitRefresh)
        else:
            itemsPresent = False
    print("All Objects deleted!")


####################################################
# DeleteConnectHarnesses
####################################################
def DeleteConnectHarnesses(config, Compartments):
    AllItems = []
    object = oci.streaming.StreamAdminClient(config)

    print("Getting all Connect Harnesses objects")
    for Compartment in Compartments:
        items = oci.pagination.list_call_get_all_results(object.list_connect_harnesses, compartment_id=Compartment.id).data
        for item in items:
            if (item.lifecycle_state != "DELETED"):
                AllItems.append(item)
                print("- {} - {}".format(item.name, item.lifecycle_state))

    itemsPresent = True

    while itemsPresent:
        count = 0
        for item in AllItems:
            try:
                itemstatus = object.get_connect_harness(connect_harness_id=item.id).data
                if itemstatus.lifecycle_state != "DELETED":
                    if itemstatus.lifecycle_state != "DELETING":
                        try:
                            print("Deleting: {}".format(itemstatus.name))
                            object.delete_connect_harness(connect_harness_id=itemstatus.id)
                        except Exception:
                            print("error trying to delete: {}".format(itemstatus.name))
                    else:
                        print("{} = {}".format(itemstatus.name, itemstatus.lifecycle_state))
                    count = count + 1
            except Exception:

                print("-----------------> error deleting {}, probably already deleted: {}.".format(item.name, item.lifecycle_state))
        if count > 0:
            print("Waiting for all Objects to be deleted...")
            time.sleep(WaitRefresh)
        else:
            itemsPresent = False
    print("All Objects deleted!")


####################################################
# DeleteServiceConnectors
####################################################
def DeleteServiceConnectors(config, Compartments):
    AllItems = []
    object = oci.sch.ServiceConnectorClient(config)

    print("Getting all Service Connectors objects")
    for Compartment in Compartments:
        items = oci.pagination.list_call_get_all_results(object.list_service_connectors, compartment_id=Compartment.id).data
        for item in items:
            if (item.lifecycle_state != "DELETED"):
                AllItems.append(item)
                print("- {} - {}".format(item.display_name, item.lifecycle_state))

    itemsPresent = True

    while itemsPresent:
        count = 0
        for item in AllItems:
            try:
                itemstatus = object.get_service_connector(service_connector_id=item.id).data
                if itemstatus.lifecycle_state != "DELETED":
                    if itemstatus.lifecycle_state != "DELETING":
                        try:
                            print("Deleting: {}".format(itemstatus.display_name))
                            object.delete_service_connector(service_connector_id=itemstatus.id)
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
    print("All Analytics Objects deleted!")
