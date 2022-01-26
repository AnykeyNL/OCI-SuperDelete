import oci
import time

WaitRefresh = 15
MaxIDeleteIteration = 20


##############################################
# DeleteLogGroups
##############################################
def DeleteLogGroups(config, Compartments):
    AllItems = []
    object = oci.logging.LoggingManagementClient(config)

    print("Getting all Log Group objects")
    for C in Compartments:
        Compartment = C.details
        items = oci.pagination.list_call_get_all_results(object.list_log_groups, compartment_id=Compartment.id).data
        for item in items:
            AllItems.append(item)
            print("- {} - {}".format(item.display_name, item.lifecycle_state))

    iteration = 0
    for item in AllItems:
        logs = object.list_logs(log_group_id=item.id)
        print(" - Log group {} has {} logs".format(item.display_name, len(logs.data)))
        while len(logs.data) > 0:
            print(" - Logs found: {}".format(len(logs.data)))
            for log in logs.data:
                try:
                    object.delete_log(log_group_id=item.id, log_id=log.id)
                except Exception:
                    print("Error deleting log {} in log group {}".format(log.id, item.id))

            print("Waiting for all Objects to be deleted..." + (" Iteration " + str(iteration) + " of " + str(MaxIDeleteIteration) if iteration > 0 else ""))
            time.sleep(WaitRefresh)
            iteration += 1

            if iteration >= MaxIDeleteIteration:
                print("Some Logs not deleted, skipping!")
                return

            logs = object.list_logs(log_group_id=item.id)

        try:
            print("Deleting log group: {}".format(item.display_name))
            object.delete_log_group(log_group_id=item.id)
        except Exception:
            print("error trying to delete log group: {}".format(item.display_name))

    print("All Log Group Objects deleted!")
