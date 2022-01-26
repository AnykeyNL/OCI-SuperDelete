import oci
import time

WaitRefresh = 15
MaxIDeleteIteration = 20

def DeleteAny(config, Compartments, ServiceClient, ServiceName, ServiceID = "", ReturnServiceID = "id", ListCommand = "", GetCommand = "", DeleteCommand = "", ObjectNameVar = "display_name", DelState = "DELETED", DelingSate = "DELETING", Extra = "", Filter="", PerAD=False):
    AllItems = []
    object = eval("oci.{}(config)".format(ServiceClient))

    if ServiceID == "":
        ServiceID = ServiceName + "_id"
    if ListCommand == "":
        # If service name ends on 'y', make plural to 'ies', "ss" to "sses", else just add 's'
        if ServiceName[-2:] == "ay":
            ListCommand = "list_" + ServiceName + "s"
        elif ServiceName[-1] == "y":
            ListCommand = "list_" + ServiceName[0:-1] + "ies"
        elif ServiceName[-2:] == "ss":
            ListCommand = "list_" + ServiceName + "es"
        else:
            ListCommand = "list_" + ServiceName + "s"
    if GetCommand == "" :
        GetCommand = "get_" + ServiceName
    if DeleteCommand == "":
        DeleteCommand = "delete_" + ServiceName

    if PerAD:
        identity = oci.identity.IdentityClient(config)

    print("Getting all {} objects                 ".format(ServiceName), end = "\r")
    for C in Compartments:
        Compartment = C.details
        try:
            if PerAD:
                ads = identity.list_availability_domains(compartment_id=Compartment.id).data
                items = []
                for ad in ads:
                    itemstemp  = eval("oci.pagination.list_call_get_all_results(object.{}, availability_domain=\"{}\", compartment_id=Compartment.id{}, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY).data".format(ListCommand, ad.name, Extra))
                    for item in itemstemp:
                        items.append(item)
            else:
                items = eval("oci.pagination.list_call_get_all_results(object.{}, compartment_id=Compartment.id{}, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY).data".format(ListCommand, Extra))

        except oci.exceptions.ServiceError as response:
            if response.code == 404:
                print ("No items found                             ", end = "\r")
                items = []
            else:
                items = []
                print("error {}-{} trying to delete: {}".format(response.code, response.message, ServiceName))

        for item in items:
            # Delete objects that do not have lifecycle management status
            if DelState == "":
                try:
                    print("Deleting {}: {}-{} @ {}".format(C.fullpath, ServiceName, eval("item.{}".format(ObjectNameVar)), config["region"]))
                    eval("object.{}({}=item.{}, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY)".format(DeleteCommand, ServiceID, ReturnServiceID))
                except oci.exceptions.ServiceError as response:
                    if response.code == 404:
                        print("Object already deleted", end = "\r")
                    else:
                        print("error {}-{} trying to delete: {} - {}".format(response.code, response.message, eval("item.{}".format(C.fullpath, ObjectNameVar))))
            # Add objects with lifecycle management to the queue
            elif item.lifecycle_state != DelState:
                if item.compartment_id is not None:
                    if Filter == "protected": # Filter for is-protected items
                        if not item.is_protected:
                            AllItems.append(item)
                            print("- {} - {}".format(eval("item.{}".format(ObjectNameVar)), item.lifecycle_state), end = "\r")
                    if Filter == "":
                        AllItems.append(item)
                        print("- {} - {}".format(eval("item.{}".format(ObjectNameVar)), item.lifecycle_state), end = "\r")

        if DelState == "":
            print("{} Objects deleted                  ".format(ServiceName), end = "\r")
        else:
            # Process queue of objects with a lifecycle object
            if len (AllItems) > 0:

                itemsPresent = True
                iteration = 0

                while itemsPresent:
                    count = 0
                    for item in AllItems:
                        try:
                            itemstatus = eval("object.{}({}=item.{}, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY).data".format(GetCommand, ServiceID, ReturnServiceID))
                            if itemstatus.lifecycle_state != DelState:
                                if itemstatus.lifecycle_state != DelingSate:
                                    try:
                                        print("Deleting {}: {}-{} @ {}".format(C.fullpath, ServiceName, eval("itemstatus.{}".format(ObjectNameVar)), config["region"]))
                                        eval("object.{}({}=itemstatus.{}, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY)".format(DeleteCommand, ServiceID, ReturnServiceID))
                                    except oci.exceptions.ServiceError as response:
                                        print ("ERROR: {}".format(response.code))
                                        print (" ")
                                        if response.code == 404:
                                            print ("Object deleted                     ", end = "\r")
                                        elif response.code == "InvalidParameter":
                                            print ("Error invalid paratemer, likely can ignore         ", end = "\r")
                                            count = count - 1
                                        else:
                                            print("error {}-{} trying to delete: {} - {}".format(response.code, response.message, eval("itemstatus.{}".format(C.fullpath, ObjectNameVar))))
                                else:
                                    print("{} is {}".format(eval("itemstatus.{}".format(ObjectNameVar)), itemstatus.lifecycle_state), end = "\r")
                                count = count + 1
                        except oci.exceptions.ServiceError as response:
                            if response.code == 404:
                                print("Object deleted                              ", end = "\r")
                            else:
                                print("----------------->error {}-{} trying to delete: {} - {} ".format(response.code, response.message, eval("itemstatus.{}".format(ObjectNameVar)), item.lifecycle_state))

                    if count > 0:
                        print("Waiting for all " + ServiceName + " Objects to be deleted..." + (" Iteration " + str(iteration) + " of " + str(MaxIDeleteIteration) if iteration > 0 else ""), end = "\r")
                        time.sleep(WaitRefresh)
                        iteration += 1

                        if iteration >= MaxIDeleteIteration:
                            print("Some {} not deleted, skipping!                   ".format(ServiceName), end = "\r")
                            return
                    else:
                        itemsPresent = False
                print("All {} Objects deleted!                    ".format(ServiceName), end = "\r")
            else:
                print("No {} Objects found                      ".format(ServiceName), end = "\r")