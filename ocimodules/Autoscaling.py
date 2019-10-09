import oci
import time

WaitRefresh = 15

def DeleteAutoScalingConfigurations(config, Compartments):
    AllItems = []
    object = oci.autoscaling.AutoScalingClient(config)

    print ("Deleting all Autoscaling configurations")
    for Compartment in Compartments:
        items = oci.pagination.list_call_get_all_results(object.list_auto_scaling_configurations, compartment_id=Compartment.id).data
        for item in items:
            try:
                print("- {}".format(item.display_name))
                object.delete_auto_scaling_configuration(auto_scaling_configuration_id=item.id)
            except:
                print("Probably already deleted")

    print ("All Objects deleted!")

