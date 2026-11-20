import oci
import sys
import time

WaitRefresh = 10
MaxRetries = 10
MaxIDeleteTagIteration = 5


class OCICompartments:
    fullpath = ""
    level = 0
    details = oci.identity.models.Compartment()


#################################################
# List compartments of rootID
# subtree=True is only valid when rootID is the tenancy OCID and
# returns the whole compartment hierarchy in a single (paginated) call.
# raise_errors=True re-raises non-429 errors instead of returning []
#################################################
def GetCompartments(identity, rootID, subtree=False, raise_errors=False):
    for attempt in range(MaxRetries):
        try:
            return oci.pagination.list_call_get_all_results(
                identity.list_compartments,
                compartment_id=rootID,
                compartment_id_in_subtree=subtree,
                access_level="ANY",
                retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY
            ).data
        except oci.exceptions.ServiceError as e:
            if e.status == 429:
                print("API busy.. retry {}/{}".format(attempt + 1, MaxRetries), end="\r")
                time.sleep(WaitRefresh)
            elif raise_errors:
                raise
            else:
                print("Warning: could not list sub-compartments of {}, they will be skipped: {}".format(rootID, e.message))
                return []
    message = "Giving up listing compartments for {} after {} retries".format(rootID, MaxRetries)
    if raise_errors:
        raise RuntimeError(message)
    print("Warning: " + message)
    return []


#################################################
# Add all ACTIVE descendants of parent to result (depth first)
# children_of(compartment_id) returns the direct child compartments
#################################################
def AddSubCompartments(result, parent, children_of):
    for compartment in sorted(children_of(parent.details.id), key=lambda c: c.name.lower()):
        if compartment.lifecycle_state != "ACTIVE":
            continue
        newcomp = OCICompartments()
        newcomp.details = compartment
        newcomp.fullpath = "{}/{}".format(parent.fullpath, compartment.name)
        newcomp.level = parent.level + 1
        result.append(newcomp)
        AddSubCompartments(result, newcomp, children_of)


#################################################
# Resolve -c value (OCID, full path or name) to a compartment OCID
# Full path: /root/teamA/dev ("/root" is the tenancy)
# Name: only accepted when exactly one ACTIVE compartment has that name
# Exits when the value cannot be resolved to exactly one compartment
#################################################
def ResolveCompartment(config, signer, value):
    if value.startswith("ocid1."):
        return value

    identity = oci.identity.IdentityClient(config, signer=signer)
    tenancy_id = config["tenancy"]
    try:
        all_compartments = GetCompartments(identity, tenancy_id, subtree=True, raise_errors=True)
    except (oci.exceptions.ServiceError, RuntimeError) as e:
        print("Could not load the compartments of the tenancy to look up '{}': {}".format(value, getattr(e, "message", e)))
        print("Please specify the compartment OCID with -c instead")
        sys.exit(-1)

    active = {c.id: c for c in all_compartments if c.lifecycle_state == "ACTIVE"}
    paths = {tenancy_id: "/root"}

    def path_of(compartment_id):
        if compartment_id not in paths:
            compartment = active.get(compartment_id)
            parent = path_of(compartment.compartment_id) if compartment else None
            paths[compartment_id] = "{}/{}".format(parent, compartment.name) if parent else None
        return paths[compartment_id]

    # Compartment names are unique (case-insensitive) within a parent, so a full path matches at most one
    if value.startswith("/"):
        wanted = value.rstrip("/").lower()
        matches = [cid for cid in list(active) + [tenancy_id] if (path_of(cid) or "").lower() == wanted]
    else:
        matches = [cid for cid, c in active.items() if c.name.lower() == value.lower() and path_of(cid)]

    if not matches:
        print("No active compartment found matching '{}'".format(value))
        sys.exit(-1)

    if len(matches) > 1:
        print("Multiple compartments are named '{}', please specify the full path or OCID with -c:".format(value))
        for cid in sorted(matches, key=lambda m: path_of(m).lower()):
            print("  {}  ({})".format(path_of(cid), cid))
        sys.exit(-1)

    print("Compartment '{}' resolved to {} ({})".format(value, path_of(matches[0]), matches[0]))
    return matches[0]


#################################################
#                 Login                 #
#################################################
def Login(config, signer, startcomp, sso_user=False):
    identity = oci.identity.IdentityClient(config, signer=signer)
    if "user" in config:
        try:
            user = identity.get_user(config["user"]).data
            print("Logged in as: {} @ {}".format(user.description, config["region"]))
        except oci.exceptions.ServiceError as e:
            if e.status == 404 and sso_user:
                print("Warning: user not found — assuming SSO")
                user = "IP-DT"
            else:
                raise e
    else:
        print("Logged in as: {} @ {}".format("InstancePrinciple/DelegationToken", config["region"]))
        user = "IP-DT"

    c = []

    # Adding Start compartment
    if "user" in config or ".tenancy." not in startcomp:
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

    # Fast path: load the whole tenancy hierarchy in one call (needs inspect compartments on the tenancy)
    try:
        all_compartments = GetCompartments(identity, config["tenancy"], subtree=True, raise_errors=True)
        children = {}
        for compartment in all_compartments:
            children.setdefault(compartment.compartment_id, []).append(compartment)
        AddSubCompartments(c, newcomp, lambda compartment_id: children.get(compartment_id, []))
        return c
    except (oci.exceptions.ServiceError, RuntimeError) as e:
        print("Could not load all compartments of the tenancy in one call ({}), loading them one by one..".format(getattr(e, "message", e)))

    # Fallback: list the sub-compartments of each compartment separately
    AddSubCompartments(c, newcomp, lambda compartment_id: GetCompartments(identity, compartment_id))
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
def DeleteCompartments(config, signer, compartments, startcomp, delete_self=False):
    oci.circuit_breaker.NoCircuitBreakerStrategy()
    object = oci.identity.IdentityClient(config, signer=signer)
    work_request_ocids = []

    # Start with the deepest level and work down to either 1 or 0 depending on delete_self
    level = max((C.level for C in compartments), default=0)
    min_level = 0 if delete_self else 1
    while level >= min_level:
        for C in compartments:
            Compartment = C.details
            if C.level == level:
                retry = True
                retrycount = 0
                while retry:
                    retry = False
                    try:
                        timestr = time.strftime("%H:%M:%S", time.localtime())
                        resp = object.delete_compartment(compartment_id=Compartment.id)

                        # OCI async deletes return the work request OCID in the response headers.
                        # Depending on SDK version, the SDK may expose it via `resp.headers`
                        # or `resp.data`, so we try both.
                        work_request_ocid = None
                        headers = getattr(resp, "headers", None)
                        if headers and hasattr(headers, "get"):
                            work_request_ocid = headers.get("opc-work-request-id")

                        if work_request_ocid is None:
                            data = getattr(resp, "data", None)
                            if data is not None:
                                work_request_ocid = getattr(data, "opc_work_request_id", None)

                        if work_request_ocid:
                            work_request_ocids.append(work_request_ocid)
                            print("{} Deleted compartment: {} (workRequest: {})".format(timestr, C.fullpath, work_request_ocid))
                        else:
                            print("{} Deleted compartment: {}".format(timestr, C.fullpath))
                    except Exception:
                        print("{} Delaying - retry attempt {} .. api calls           ".format(timestr, retrycount), end="\r")
                        time.sleep(10)
                        retrycount = retrycount + 1
                        retry = True

        level = level - 1

    return work_request_ocids

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
