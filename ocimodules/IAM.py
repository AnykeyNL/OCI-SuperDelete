import oci
import time
import sys

WaitRefresh = 10
MaxIDeleteTagIteration = 5


#################################################
#                 Login                 #
#################################################
def Login(config, startcomp):
    identity = oci.identity.IdentityClient(config)
    user = identity.get_user(config["user"]).data
    print("Logged in as: {} @ {}".format(user.description, config["region"]))

    # Add first level subcompartments
    compartments = []
    try:
        compartments = oci.pagination.list_call_get_all_results(identity.list_compartments, compartment_id=startcomp).data
    except Exception as e:
        if e.status == 404:
            print("Compartment not found")
            sys.exit(2)
        else:
            print("Error {}".format(e.status))
            sys.exit(2)

    # Add 2nd level subcompartments
    for compartment in compartments:
        subcompartments = oci.pagination.list_call_get_all_results(identity.list_compartments, compartment_id=compartment.id).data
        for sub in subcompartments:
            compartments.append(sub)

    # Add start compartment to list
    compartment = identity.get_compartment(compartment_id=startcomp).data
    compartments.append(compartment)

    return compartments


#################################################
#              SubscribedRegions
#################################################
def SubscribedRegions(config):
    regions = []
    identity = oci.identity.IdentityClient(config)
    regionDetails = identity.list_region_subscriptions(tenancy_id=config["tenancy"]).data

    # Add subscribed regions to list
    for detail in regionDetails:
        regions.append(detail.region_name)

    return regions


#################################################
#              GetHomeRegion
#################################################
def GetHomeRegion(config):
    home_region = ""
    identity = oci.identity.IdentityClient(config)
    regionDetails = identity.list_region_subscriptions(tenancy_id=config["tenancy"]).data

    # Set home region for connection
    for reg in regionDetails:
        if reg.is_home_region:
            home_region = str(reg.region_name)

    return home_region


#################################################
#              GetTenantName
#################################################
def GetTenantName(config):
    identity = oci.identity.IdentityClient(config)
    tenancy = identity.get_tenancy(config['tenancy']).data
    return tenancy.name


#################################################
#              DeleteTagNameSpaces
#################################################
def DeleteTagNameSpaces(config, compartments):

    AllItems = []
    object = oci.identity.IdentityClient(config)

    print("Getting all Tag Namespace objects")
    for Compartment in compartments:
        items = oci.pagination.list_call_get_all_results(object.list_tag_namespaces, compartment_id=Compartment.id).data
        if len(items) == 0:
            continue

        for item in items:
            if item.lifecycle_state == 'DELETING':
                continue
            AllItems.append(item)
            print("- Tag Namespace: {}".format(item.name))

        print("Retiring all namespaces.. in compartment " + str(Compartment.name))
        for item in AllItems:
            itemstatus = object.get_tag_namespace(tag_namespace_id=item.id).data
            print("Tag {} retired: {}".format(itemstatus.name, itemstatus.is_retired))
            if "{}".format(itemstatus.is_retired) == "False":
                print("Retiring tag namespace {}".format(itemstatus.name))
                tagdetails = oci.identity.models.UpdateTagNamespaceDetails()
                tagdetails.is_retired = True
                try:
                    object.update_tag_namespace(tag_namespace_id=item.id, update_tag_namespace_details=tagdetails)
                except Exception:
                    print("Error retiring Tag, could be already in deleting phase.")

        print("Retired all namespaces.. Waiting...")
        time.sleep(2)

        done = False
        iteration = 0
        while not done:
            done = True
            for item in AllItems:
                try:
                    itemstatus = object.get_tag_namespace(tag_namespace_id=item.id).data
                except Exception:
                    print("Not found, tag deleted")
                else:
                    if itemstatus.lifecycle_state != "DELETED":
                        done = False
                        if itemstatus.lifecycle_state != "DELETING":
                            try:
                                print("Deleting: {}".format(itemstatus.name))
                                object.cascade_delete_tag_namespace(tag_namespace_id=item.id)
                            except Exception as e:
                                print("failed, trying again... {} ".format(str(e)))
                        else:
                            print("Waiting for tag {} to finish deleting, status={}".format(itemstatus.name, itemstatus.lifecycle_state))

            print("Waiting for all Objects to be deleted..." + (" Iteration " + str(iteration) + " of " + str(MaxIDeleteTagIteration) if iteration > 0 else ""))
            time.sleep(WaitRefresh)
            iteration += 1

            if iteration >= MaxIDeleteTagIteration:
                print("Tag Namespace not deleted, skipping!")
                done = True
                continue

    print("All Tag Namespace Objects deleted!")


#################################################
#              DeleteCompartments
#################################################
def DeleteCompartments(config, compartments, startcomp):

    object = oci.identity.IdentityClient(config)
    for Compartment in compartments:
        if Compartment.id != startcomp:
            retry = True
            while retry:
                retry = False
                try:
                    timestr = time.strftime("%H:%M:%S", time.localtime())
                    object.delete_compartment(compartment_id=Compartment.id)
                    print("{} Deleted compartment: {}".format(timestr, Compartment.name))
                except Exception as e:
                    if e.status == 429:
                        print("{} Delaying.. api calls".format(timestr))
                        time.sleep(10)
                        retry = True


#################################################
#              DeletePolicies
#################################################
def DeletePolicies(config, compartments):
    object = oci.identity.IdentityClient(config)

    print("Getting all Policy objects")
    for Compartment in compartments:
        items = oci.pagination.list_call_get_all_results(object.list_policies, compartment_id=Compartment.id).data
        for item in items:
            try:
                print("Deleting: {}".format(item.name))
                object.delete_policy(policy_id=item.id)
            except oci.exceptions.ServiceError as itemstatus:
                print("error trying to delete: {} - {}".format(item.name, itemstatus.message))

    print("All Policies Objects deleted!")


#################################################
#              DeleteTagDefaults
#################################################
def DeleteTagDefaults(config, compartments):

    object = oci.identity.IdentityClient(config)

    print("Getting all Policy objects")
    for Compartment in compartments:
        items = oci.pagination.list_call_get_all_results(object.list_tag_defaults, compartment_id=Compartment.id).data
        for item in items:
            print("- {}".format(item.tag_definition_name))
            try:
                object.delete_tag_default(tag_default_id=item.id)
                print("- Deleted : {}".format(item.tag_definition_name))
            except oci.exceptions.ServiceError as itemstatus:
                print("- error trying to delete: {} - {}".format(item.tag_definition_name, itemstatus.message))

    print("All Tag Defaults Objects deleted!")
