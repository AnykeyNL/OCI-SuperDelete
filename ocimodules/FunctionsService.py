import oci
import time


##############################################
# DeleteDBBackups
##############################################
def DeleteApplications(config, signer, Compartments):
    object = oci.functions.FunctionsManagementClient(config, signer=signer)

    print("Deleting all Applications and Functions")
    for C in Compartments:
        Compartment = C.details
        items = oci.pagination.list_call_get_all_results(object.list_applications, compartment_id=Compartment.id).data
        for item in items:
            print("- {}".format(item.display_name))
            functions = oci.pagination.list_call_get_all_results(object.list_functions, application_id=item.id).data
            for function in functions:
                print("  * {}".format(function.display_name))
                object.delete_function(function_id=function.id)
            time.sleep(5)
            object.delete_application(application_id=item.id)

    print("All Applications and Functions Objects deleted!")
