import oci
import time

def DeleteLogGroups(config, Compartments):
    AllItems = []
    object = oci.logging.LoggingManagementClient(config)

    print ("Getting all Log Group objects")
    for Compartment in Compartments:
        items = oci.pagination.list_call_get_all_results(object.list_log_groups, compartment_id=Compartment.id).data
        for item in items:
                AllItems.append(item)
                print("- {} - {}".format(item.display_name, item.lifecycle_state))

    for item in AllItems:
        logs = object.list_logs(log_group_id=item.id)
        print (" - Log group {} has {} logs".format(item.display_name, len(logs.data)))
        while len(logs.data) > 0:
            print(" - Logs found: {}".format(len(logs.data)))
            for log in logs.data:
                try:
                    object.delete_log(log_group_id=item.id, log_id=log.id)
                except:
                    print ("Error deleting log {} in log group {}".format(log.id, item.id))
            time.sleep(5)
            logs = object.list_logs(log_group_id=item.id)

        try:
            print ("Deleting log group: {}".format(item.display_name))
            object.delete_log_group(log_group_id=item.id)
        except:
            print ("error trying to delete log group: {}".format(item.display_name))

    print ("All Objects deleted!")