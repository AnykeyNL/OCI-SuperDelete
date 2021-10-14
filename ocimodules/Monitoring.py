import oci

WaitRefresh = 15


##############################################
# DeleteAlarms
##############################################
def DeleteAlarms(config, Compartments):
    object = oci.monitoring.MonitoringClient(config)

    print("Deleting all Alarms")
    for Compartment in Compartments:
        items = oci.pagination.list_call_get_all_results(object.list_alarms, compartment_id=Compartment.id).data
        for item in items:
            try:
                print("- {}".format(item.display_name))
                object.delete_alarm(alarm_id=item.id)
            except Exception:
                print("Probably already deleted")

    print("All Alarms Objects deleted!")
