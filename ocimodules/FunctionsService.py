import oci
import time

WaitRefresh = 15

def DeleteApplications(config, Compartments):
    AllItems = []
    object = oci.functions.FunctionsManagementClient(config)

    print ("Deleting all Applications and Functions")
    for Compartment in Compartments:
        items = oci.pagination.list_call_get_all_results(object.list_applications, compartment_id=Compartment.id).data
        for item in items:
            #try:
                print("- {}".format(item.display_name))
                functions = oci.pagination.list_call_get_all_results(object.list_functions, application_id=item.id).data
                for function in functions:
                    print ("  * {}".format(function.display_name))
                    object.delete_function(function_id=function.id)
                time.sleep(5)
                object.delete_application(application_id=item.id)
            #except:
            #    print ("Probably already deleted")

    print ("All Objects deleted!")

