import oci
import time

def Login(config, startcomp):
    identity = oci.identity.IdentityClient(config)
    user = identity.get_user(config["user"]).data
    RootCompartmentID = user.compartment_id
    print("Logged in as: {} @ {}".format(user.description, config["region"]))

    # Add first level subcompartments
    compartments = oci.pagination.list_call_get_all_results(identity.list_compartments, compartment_id=startcomp).data

    # Add 2nd level subcompartments
    for compartment in compartments:
        subcompartments = oci.pagination.list_call_get_all_results(identity.list_compartments, compartment_id=compartment.id).data
        for sub in subcompartments:
            compartments.append(sub)

    # Add start compartment to list
    compartment = identity.get_compartment(compartment_id=startcomp).data
    compartments.append(compartment)

    return compartments


    


def DeleteTagNameSpaces(config, compartments):

    AllItems = []
    object = oci.identity.IdentityClient(config)

    print ("Getting all Healthchecks PING monitor objects")
    for Compartment in Compartments:
        items = oci.pagination.list_call_get_all_results(object.list_tag_namespaces, compartment_id=Compartment.id).data
        for item in items:
                AllItems.append(item)
                print("- {}".format(item.name))

    itemsPresent = True

    while itemsPresent:
        count = 0
        for item in AllItems:
            try:
                itemstatus = object.get_tag_namespace(tag_namespace_id=item.id).data
                try:
                    print ("Deleting: {}".format(itemstatus.display_name))
                    # Need to retire tag namespace

                except:
                    print ("error trying to delete: {}".format(itemstatus.display_name))
                count = count + 1
            except:
                print ("Deleted : {}".format(item.display_name))
        if count > 0 :
            print ("Waiting for all Objects to be deleted...")
            time.sleep(WaitRefresh)
        else:
            itemsPresent = False
    print ("All Objects deleted!")

def DeleteCompartments(config, compartments, startcomp):

    object = oci.identity.IdentityClient(config)
    for Compartment in compartments:
        if Compartment.id != startcomp:
            retry = True
            while retry:
                retry = False
                try:
                    object.delete_compartment(compartment_id=Compartment.id)
                    print ("Deleted compartment: {}".format(Compartment.name))
                except Exception as e:
                    if e.status == 429:
                        print ("Delaying.. api calls")
                        time.sleep(10)
                        retry = True





