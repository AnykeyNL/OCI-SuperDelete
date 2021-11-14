import oci
import time

WaitRefresh = 15
MaxIDeleteIteration = 20

def DeleteAny(config, Compartments, ServiceObject, ServiceName, ServiceID, ListCommand, GetCommand, DeleteCommand, ObjectNameVar, DelState, DelingSate):
    AllItems = []
    object = eval("oci.core.{}(config)".format(ServiceObject))

    print("Getting all {} objects".format(ServiceName))
    for Compartment in Compartments:
        items = eval("oci.pagination.list_call_get_all_results(object.{}, compartment_id=Compartment.id).data".format(ListCommand))
        for item in items:
            # Delete objects that do not have lifecycle management status
            if DelState == "":
                try:
                    print("Deleting: {}".format(eval("item.{}".format(ObjectNameVar))))
                    eval("object.{}({}=item.id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY)".format(DeleteCommand, ServiceID))
                except oci.exceptions.ServiceError as response:
                    if response.code == 404:
                        print("Object already deleted")
                    else:
                        print("error {}-{} trying to delete: {}".format(response.code, response.message, eval("item.{}".format(ObjectNameVar))))
            # Add objects with lifecycle management to the queue
            elif item.lifecycle_state != DelState:
                if item.compartment_id is not None:
                    AllItems.append(item)
                    print("- {} - {}".format(eval("item.{}".format(ObjectNameVar)), item.lifecycle_state))

    if DelState == "":
        print("{} Objects deleted".format(ServiceName))
    else:
        # Process queue of objects with a lifecycle object
        if len (AllItems) > 0:

            itemsPresent = True
            iteration = 0

            while itemsPresent:
                count = 0
                for item in AllItems:
                    try:
                        itemstatus = eval("object.{}({}=item.id).data".format(GetCommand, ServiceID))
                        if itemstatus.lifecycle_state != DelState:
                            if itemstatus.lifecycle_state != DelingSate:
                                try:
                                    print("Deleting: {}".format(eval("itemstatus.{}".format(ObjectNameVar))))
                                    eval("object.{}({}=itemstatus.id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY)".format(DeleteCommand, ServiceID))
                                except oci.exceptions.ServiceError as response:
                                    if response.code == 404:
                                        print ("Object deleted")
                                    else:
                                        print("error {}-{} trying to delete: {}".format(response.code, response.message, eval("itemstatus.{}".format(ObjectNameVar))))
                            else:
                                print("{} is {}".format(eval("itemstatus.{}".format(ObjectNameVar)), itemstatus.lifecycle_state))
                            count = count + 1
                    except oci.exceptions.ServiceError as response:
                        if response.code == 404:
                            print("Object deleted")
                        else:
                            print("----------------->error {}-{} trying to delete: {} - {} ".format(response.code, response.message, eval("itemstatus.{}".format(ObjectNameVar)), item.lifecycle_state))

                if count > 0:
                    print("Waiting for all " + ServiceName + "Objects to be deleted..." + (" Iteration " + str(iteration) + " of " + str(MaxIDeleteIteration) if iteration > 0 else ""))
                    time.sleep(WaitRefresh)
                    iteration += 1

                    if iteration >= MaxIDeleteIteration:
                        print("Some {} not deleted, skipping!".format(ServiceName))
                        return
                else:
                    itemsPresent = False
            print("All {} Objects deleted!".format(ServiceName))
        else:
            print("No {} Objects found".format(ServiceName))