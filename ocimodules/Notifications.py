import oci
import time

WaitRefresh = 15

def DeleteNotifications(config, Compartments):
    AllItems = []
    object = oci.ons.NotificationControlPlaneClient(config)

    print ("Deleting all Notification Topics")
    for Compartment in Compartments:
        items = oci.pagination.list_call_get_all_results(object.list_topics, compartment_id=Compartment.id).data
        for item in items:
            try:
                print("- {}".format(item.name))
                object.delete_topic(topic_id =item.topic_id)
            except:
                print("Probably already deleted")

    print ("All Objects deleted!")

