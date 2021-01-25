import oci
import time

WaitRefresh = 10

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


def SubscribedRegions(config):
    regions = []
    identity = oci.identity.IdentityClient(config)
    regionDetails=identity.list_region_subscriptions(tenancy_id=config["tenancy"]).data
    
    #Add subscribed regions to list
    for detail in regionDetails:
        regions.append(detail.region_name)
        
    return regions        
    


def DeleteTagNameSpaces(config, compartments):

    AllItems = []
    object = oci.identity.IdentityClient(config)

    print ("Getting all Tag Namespace objects")
    for Compartment in compartments:
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
                if itemstatus.is_retired == "False":
                    print ("Retiring tag namespace {}".format(itemstatus.name))
                    tagdetails = oci.identity.models.UpdateTagNamespaceDetails()
                    tagdetails.is_retired = True
                    object.update_tag_namespace(tag_namespace_id=item.id, update_tag_namespace_details=tagdetails)
                    count = count + 1
                else:
                    if itemstatus.lifecycle_state != "DELETED":
                        if itemstatus.lifecycle_state != "DELETING":
                            #try:
                            print ("Deleting: {}".format(itemstatus.name))
                            object.cascade_delete_tag_namespace(tag_namespace_id=item.id)
                            #except oci.exceptions.ServiceError as response:
                            #    print ("error trying to delete: {} - {}".format(itemstatus.name, response.message))
                        else:
                            print ("Waiting for tag {} to finish deleting...This can take a long time :-(".format(itemstatus.name))
                        count = count + 1
            except:
                print ("Tag has been deleted")
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


def DeletePolicies(config, compartments):

    AllItems = []
    object = oci.identity.IdentityClient(config)

    print ("Getting all Policy objects")
    for Compartment in compartments:
        items = oci.pagination.list_call_get_all_results(object.list_policies, compartment_id=Compartment.id).data
        for item in items:
                AllItems.append(item)
                print("- {}".format(item.name))

    itemsPresent = True

    while itemsPresent:
        count = 0
        for item in AllItems:
            try:
                itemstatus = object.get_policy(policy_id=item.id).data
                try:
                    print ("Deleting: {}".format(itemstatus.name))
                    object.delete_policy(policy_id=itemstatus.id)
                except oci.exceptions.ServiceError as itemstatus:
                    print ("error trying to delete: {} - {}".format(itemstatus.name, itemstatus.message))
                count = count + 1
            except:
                print ("Deleted : {}".format(item.name))
        if count > 0 :
            print ("Waiting for all Objects to be deleted...")
            time.sleep(WaitRefresh)
        else:
            itemsPresent = False
    print ("All Objects deleted!")
