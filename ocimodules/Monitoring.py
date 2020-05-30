import oci
import time

WaitRefresh = 15

def DeleteAlarms(config, Compartments):
    AllItems = []
    object = oci.monitoring.MonitoringClient(config)

    print ("Deleting all Alarms")
    for Compartment in Compartments:
        items = oci.pagination.list_call_get_all_results(object.list_alarms, compartment_id=Compartment.id).data
        for item in items:
            try:
                print("- {}".format(item.display_name))
                object.delete_alarm(alarm_id =item.id)
            except:
                print ("Probably already deleted")

    print ("All Objects deleted!")

