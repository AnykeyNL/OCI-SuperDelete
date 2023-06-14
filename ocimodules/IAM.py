import oci
import time
import sys

WaitRefresh = 10
MaxIDeleteTagIteration = 5

class OCICompartments:
    fullpath = ""
    level = 0
    details = oci.identity.models.Compartment()


def GetCompartments(identity, rootID):
    retry = True
    while retry:
        retry = False
        try:
            #print ("Getting compartments for {}".format(rootID))
            compartments = oci.pagination.list_call_get_all_results(identity.list_compartments, compartment_id=rootID, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY).data
            return compartments
        except oci.exceptions.ServiceError as e:
            if e.status == 429:
                print ("API busy.. retry", end = "\r")
                retry = True
                time.sleep(WaitRefresh)
            else:
                print ("bad error!: " + e.message)
    return []


#################################################
#                 Login                 #
#################################################
def Login(config, signer, startcomp):
    identity = oci.identity.IdentityClient(config, signer=signer)
    if "user" in config:
        user = identity.get_user(config["user"]).data
        print("Logged in as: {} @ {}".format(user.description, config["region"]))
    else:
        print("Logged in as: {} @ {}".format("InstancePrinciple/DelegationToken", config["region"]))
        user = "IP-DT"

    c = []

    # Adding Start compartment
    if "user" in config and not ".tenancy." in startcomp:
        compartment = identity.get_compartment(compartment_id=startcomp, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY).data
    else:
        # Bug fix - for working on root compartment using instance principle.
        compartment = oci.identity.models.Compartment()
        compartment.id = startcomp
        compartment.name = "root compartment"
        compartment.lifecycle_state = "ACTIVE"

    newcomp = OCICompartments()
    newcomp.details = compartment
    if ".tenancy." in startcomp:
        newcomp.fullpath = "/root"
        newcomp.level = 0
    else:
        newcomp.level = 0
        newcomp.fullpath = compartment.name
    c.append(newcomp)

    # Add first level subcompartments
    compartments = GetCompartments(identity, startcomp)

    # Add 2nd level subcompartments
    fullpath = newcomp.fullpath + "/"
    for compartment in compartments:
        if compartment.lifecycle_state == "ACTIVE":
            newcomp = OCICompartments()
            newcomp.details = compartment
            newcomp.fullpath = "{}{}".format(fullpath, compartment.name)
            newcomp.level = 1
            c.append(newcomp)
            subcompartments = GetCompartments(identity, compartment.id)
            subpath1 = compartment.name
            for sub1 in subcompartments:
                if sub1.lifecycle_state == "ACTIVE":
                    newcomp = OCICompartments()
                    newcomp.details = sub1
                    newcomp.fullpath = "{}{}/{}".format(fullpath, subpath1, sub1.name)
                    newcomp.level = 2
                    c.append(newcomp)

                    subcompartments2 = GetCompartments(identity, sub1.id)
                    subpath2 = sub1.name
                    for sub2 in subcompartments2:
                        if sub2.lifecycle_state == "ACTIVE":
                            newcomp = OCICompartments()
                            newcomp.details = sub2
                            newcomp.fullpath = "{}{}/{}/{}".format(fullpath, subpath1, subpath2, sub2.name)
                            newcomp.level = 3
                            c.append(newcomp)

                            subcompartments3 = GetCompartments(identity, sub2.id)
                            subpath3 = sub2.name
                            for sub3 in subcompartments3:
                                if sub3.lifecycle_state == "ACTIVE":
                                    newcomp = OCICompartments()
                                    newcomp.details = sub3
                                    newcomp.fullpath = "{}{}/{}/{}/{}".format(fullpath, subpath1, subpath2, subpath3, sub3.name)
                                    newcomp.level = 4
                                    c.append(newcomp)

                                    subcompartments4 = GetCompartments(identity, sub3.id)
                                    subpath4 = sub3.name
                                    for sub4 in subcompartments4:
                                        if sub4.lifecycle_state == "ACTIVE":
                                            newcomp = OCICompartments()
                                            newcomp.details = sub
                                            newcomp.fullpath = "{}{}/{}/{}/{}/{}".format(fullpath, subpath1, subpath2,
                                                                                         subpath3, subpath4, sub4.name)
                                            newcomp.level = 5
                                            c.append(newcomp)

                                            subcompartments5 = GetCompartments(identity, sub4.id)
                                            subpath5 = sub4.name
                                            for sub5 in subcompartments5:
                                                if sub5.lifecycle_state == "ACTIVE":
                                                    newcomp = OCICompartments()
                                                    newcomp.details = sub5
                                                    newcomp.fullpath = "{}{}/{}/{}/{}/{}/{}".format(fullpath,
                                                                                                         subpath1,
                                                                                                         subpath2,
                                                                                                         subpath3,
                                                                                                         subpath4,
                                                                                                         subpath5,
                                                                                                         sub5.name)
                                                    newcomp.level = 6
                                                    c.append(newcomp)

                                                    subcompartments6 = GetCompartments(identity, sub5.id)
                                                    subpath6 = sub5.name
                                                    for sub6 in subcompartments6:
                                                        if sub6.lifecycle_state == "ACTIVE":
                                                            newcomp = OCICompartments()
                                                            newcomp.details = sub6
                                                            newcomp.fullpath = "{}{}/{}/{}/{}/{}/{}/{}".format(
                                                                fullpath,
                                                                subpath1,
                                                                subpath2,
                                                                subpath3,
                                                                subpath4,
                                                                subpath5, subpath6,
                                                                sub6.name)
                                                            newcomp.level = 7
                                                            c.append(newcomp)

    return c


#################################################
#              SubscribedRegions
#################################################
def SubscribedRegions(config, signer):
    regions = []
    identity = oci.identity.IdentityClient(config, signer=signer)
    regionDetails = identity.list_region_subscriptions(tenancy_id=config["tenancy"]).data

    # Add subscribed regions to list
    for detail in regionDetails:
        regions.append(detail.region_name)

    return regions


#################################################
#              GetHomeRegion
#################################################
def GetHomeRegion(config, signer):
    home_region = ""
    identity = oci.identity.IdentityClient(config, signer=signer)
    regionDetails = identity.list_region_subscriptions(tenancy_id=config["tenancy"]).data

    # Set home region for connection
    for reg in regionDetails:
        if reg.is_home_region:
            home_region = str(reg.region_name)

    return home_region


#################################################
#              GetTenantName
#################################################
def GetTenantName(config, signer):
    identity = oci.identity.IdentityClient(config, signer=signer)
    tenancy = identity.get_tenancy(config['tenancy']).data
    return tenancy.name


#################################################
#              DeleteTagNameSpaces
#################################################
def DeleteTagNameSpaces(config, signer, compartments):

    AllItems = []
    object = oci.identity.IdentityClient(config, signer=signer)

    print("Getting all Tag Namespace objects")
    for C in compartments:
        Compartment = C.details
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
def DeleteCompartments(config, signer, compartments, startcomp):
    oci.circuit_breaker.NoCircuitBreakerStrategy()
    object = oci.identity.IdentityClient(config, signer=signer)

    level = 7
    while level > 0:
        for C in compartments:
            Compartment = C.details
            if C.level == level:
                retry = True
                retrycount = 0
                while retry:
                    retry = False
                    try:
                        timestr = time.strftime("%H:%M:%S", time.localtime())
                        object.delete_compartment(compartment_id=Compartment.id)
                        print("{} Deleted compartment: {}".format(timestr, C.fullpath))
                    except:
                        print("{} Delaying - retry attempt {} .. api calls           ".format(timestr, retrycount), end = "\r")
                        time.sleep(10)
                        retrycount = retrycount + 1
                        retry = True

        level = level - 1


#################################################
#              DeletePolicies
#################################################
def DeletePolicies(config, signer, compartments):
    object = oci.identity.IdentityClient(config, signer=signer)

    print("Getting all Policy objects")
    for C in compartments:
        Compartment = C.details
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
def DeleteTagDefaults(config, signer, compartments):

    object = oci.identity.IdentityClient(config, signer=signer)

    print("Getting all Policy objects")
    for C in compartments:
        Compartment = C.details
        items = oci.pagination.list_call_get_all_results(object.list_tag_defaults, compartment_id=Compartment.id).data
        for item in items:
            print("- {}".format(item.tag_definition_name))
            try:
                object.delete_tag_default(tag_default_id=item.id)
                print("- Deleted : {}".format(item.tag_definition_name))
            except oci.exceptions.ServiceError as itemstatus:
                print("- error trying to delete: {} - {}".format(item.tag_definition_name, itemstatus.message))

    print("All Tag Defaults Objects deleted!")
