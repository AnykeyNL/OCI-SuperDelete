import oci
import time

WaitRefresh = 10

def DeleteAnalytics(config, Compartments):
    AllItems = []
    object = oci.analytics.AnalyticsClient(config)

    print ("Getting all Analytics objects")
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
                itemstatus = object.get_analytics_instance(analytics_instance_id =item.id).data
                if itemstatus.lifecycle_state != "DELETED":
                    if itemstatus.lifecycle_state != "DELETING":
                        try:
                            print ("Deleting: {}".format(itemstatus.name))
                            object.delete_analytics_instance(analytics_instance_id=itemstatus.id)
                        except:
                            print ("error trying to delete: {}".format(itemstatus.name))
                    else:
                        print("{} = {}".format(itemstatus.name, itemstatus.lifecycle_state))
                    count = count + 1
            except:

                print ("-----------------> error deleting {}, probably already deleted: {}.".format(item.name, item.lifecycle_state))
        if count > 0 :
            print ("Waiting for all Objects to be deleted...")
            time.sleep(WaitRefresh)
        else:
            itemsPresent = False
    print ("All Objects deleted!")