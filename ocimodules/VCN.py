import oci
import time

WaitRefresh = 10
MaxIDeleteIteration = 5


##############################################
# DeleteVCN
##############################################
def DeleteVCN(config, Compartments):
    object = oci.core.VirtualNetworkClient(config)

    print("Getting all VCN objects")
    for C in Compartments:
        Compartment = C.details
        AllItems = []
        print("---[ Deleting Load Balancers and Reserved IPs ]----")
        DeleteLoadBalancers(config, Compartment)
        DeleteReservedIPs(config, Compartment)
        print("---[ Deleting DNS Resolvers ]----")
        DeleteDNSResolvers(config, Compartment)
        print("---[ Deleting IPSEC Connections ]----")
        DeleteIPSecConnections(config, Compartment)
        print("---[ Deleting CPEs ]----")
        DeleteCPEs(config, Compartment)
        print("---[ Deleting DRG Components ]----")
        DeleteDRGAttachments(config, Compartment)
        DeleteDRGs(config, Compartment)

        items = oci.pagination.list_call_get_all_results(object.list_vcns, compartment_id=Compartment.id).data
        for item in items:
            if item.lifecycle_state != "TERMINATED":
                AllItems.append(item)
                print("- {} - {}".format(item.display_name, item.lifecycle_state))

        for item in AllItems:
            print("----[ Deleting components of VCN: {} ]---".format(item.display_name))
            DeleteSubnets(config, Compartments, item)
            DeleteDHCPoptions(config, Compartments, item)
            DeleteSecurityLists(config, Compartments, item)
            DeleteSecurityGroups(config, Compartments, item)
            DeleteRouteTables(config, Compartments, item)
            DeleteInternetGateways(config, Compartments, item)
            DeleteServiceGateways(config, Compartments, item)
            DeleteNATGateways(config, Compartments, item)
            DeleteLocalPeeringGateways(config, Compartments, item)

            print("---[ Deleting VCN ]----")
            deleted = False
            if not deleted:
                try:
                    object.delete_vcn(vcn_id=item.id)
                    print("VNC has been deleted")
                    deleted = True
                except oci.exceptions.ServiceError as response:
                    print("Error deleting VCN : {} - {}".format(response.status, response.message))
                    time.sleep(5)


##############################################
# DeleteSubnets
##############################################
def DeleteSubnets(config, Compartments, vcn):
    AllItems = []
    object = oci.core.VirtualNetworkClient(config)

    print("Getting subnets for {}".format(vcn.display_name))
    for C in Compartments:
        compartment = C.details
        try:
            items = oci.pagination.list_call_get_all_results(object.list_subnets, compartment_id=compartment.id, vcn_id=vcn.id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY).data
            for item in items:
                if (item.lifecycle_state != "TERMINATED"):
                    AllItems.append(item)
                print("- {} - {}".format(item.display_name, item.lifecycle_state))
        except Exception:
            print("Error listing for compartment {}".format(compartment.name))
            continue

    itemsPresent = True
    iteration = 0

    while itemsPresent:
        count = 0
        for item in AllItems:
            try:
                itemstatus = object.get_subnet(subnet_id=item.id).data
                if itemstatus.lifecycle_state != "TERMINATED":
                    if itemstatus.lifecycle_state != "TERMINATING":
                        try:
                            print("Deleting: {}".format(itemstatus.display_name))
                            object.delete_subnet(subnet_id=itemstatus.id)
                        except Exception:
                            print("error trying to delete: {}".format(itemstatus.display_name))
                    else:
                        print("{} = {}".format(itemstatus.display_name, itemstatus.lifecycle_state))
                    count = count + 1
            except Exception:
                print("error deleting {}, probably already deleted".format(item.display_name))
        if count > 0:
            print("Waiting for all Objects to be deleted..." + (" Iteration " + str(iteration) + " of " + str(MaxIDeleteIteration) if iteration > 0 else ""))
            time.sleep(WaitRefresh)
            iteration += 1

            if iteration >= MaxIDeleteIteration:
                print("Some subnets not deleted, skipping!")
                return
        else:
            itemsPresent = False
    print("All Subnets Objects deleted!")


##############################################
# DeleteDHCPoptions
##############################################
def DeleteDHCPoptions(config, Compartments, vcn):
    AllItems = []
    object = oci.core.VirtualNetworkClient(config)

    print("Getting DHCP options for {}".format(vcn.display_name))
    for C in Compartments:
        compartment = C.details
        try:
            items = oci.pagination.list_call_get_all_results(object.list_dhcp_options, compartment_id=compartment.id, vcn_id=vcn.id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY).data
            for item in items:
                if (item.lifecycle_state != "TERMINATED"):
                    AllItems.append(item)
                print("- {} - {}".format(item.display_name, item.lifecycle_state))
        except Exception:
            print("Error listing for compartment {}".format(compartment.name))
            continue

    itemsPresent = True
    iteration = 0

    while itemsPresent:
        count = 0
        for item in AllItems:
            try:
                itemstatus = object.get_dhcp_options(dhcp_id=item.id).data
                if itemstatus.lifecycle_state != "TERMINATED":
                    if itemstatus.lifecycle_state != "TERMINATING":
                        try:
                            print("Deleting: {}".format(itemstatus.display_name))
                            object.delete_dhcp_options(dhcp_id=itemstatus.id)
                            count = count + 1
                        except Exception:
                            print("error trying to delete: {}".format(itemstatus.display_name))
                    else:
                        print("{} = {}".format(itemstatus.display_name, itemstatus.lifecycle_state))
                        count = count + 1
            except Exception:
                print("error deleting {}, probably already deleted".format(item.display_name))
        if count > 0:
            print("Waiting for all Objects to be deleted..." + (" Iteration " + str(iteration) + " of " + str(MaxIDeleteIteration) if iteration > 0 else ""))
            time.sleep(WaitRefresh)
            iteration += 1

            if iteration >= MaxIDeleteIteration:
                print("Some DHCP Options not deleted, skipping!")
                return
        else:
            itemsPresent = False
    print("All DHCP options Objects deleted!")


##############################################
# DeleteSecurityLists
##############################################
def DeleteSecurityLists(config, Compartments, vcn):
    AllItems = []
    object = oci.core.VirtualNetworkClient(config)

    print("Getting Security Lists for {}".format(vcn.display_name))
    for C in Compartments:
        compartment = C.details
        try:
            items = oci.pagination.list_call_get_all_results(object.list_security_lists, compartment_id=compartment.id, vcn_id=vcn.id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY).data
            for item in items:
                if (item.lifecycle_state != "TERMINATED"):
                    AllItems.append(item)
                print("- {} - {}".format(item.display_name, item.lifecycle_state))
        except Exception:
            print("Error listing for compartment {}".format(compartment.name))
            continue

    itemsPresent = True
    iteration = 0

    while itemsPresent:
        count = 0
        for item in AllItems:
            try:
                itemstatus = object.get_security_list(security_list_id=item.id).data
                if itemstatus.lifecycle_state != "TERMINATED":
                    if itemstatus.lifecycle_state != "TERMINATING":
                        try:
                            print("Deleting: {}".format(itemstatus.display_name))
                            object.delete_security_list(security_list_id=itemstatus.id)
                            count = count + 1
                        except Exception:
                            print("error trying to delete: {}".format(itemstatus.display_name))
                    else:
                        print("{} = {}".format(itemstatus.display_name, itemstatus.lifecycle_state))
                        count = count + 1
            except Exception:
                print("error deleting {}, probably already deleted".format(item.display_name))
        if count > 0:
            print("Waiting for all Objects to be deleted..." + (" Iteration " + str(iteration) + " of " + str(MaxIDeleteIteration) if iteration > 0 else ""))
            time.sleep(WaitRefresh)
            iteration += 1

            if iteration >= MaxIDeleteIteration:
                print("Some Security List not deleted, skipping!")
                return
        else:
            itemsPresent = False
    print("All Security Lists Objects deleted!")


##############################################
# DeleteSecurityGroups
##############################################
def DeleteSecurityGroups(config, Compartments, vcn):
    AllItems = []
    object = oci.core.VirtualNetworkClient(config)

    print("Getting Network Security Groups for {}".format(vcn.display_name))
    for C in Compartments:
        compartment = C.details
        try:
            items = oci.pagination.list_call_get_all_results(object.list_network_security_groups, compartment_id=compartment.id, vcn_id=vcn.id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY).data
            for item in items:
                if (item.lifecycle_state != "TERMINATED"):
                    AllItems.append(item)
                print("- {} - {}".format(item.display_name, item.lifecycle_state))
        except Exception:
            print("Error listing for compartment {}".format(compartment.name))
            continue

    itemsPresent = True
    iteration = 0

    while itemsPresent:
        count = 0
        for item in AllItems:
            try:
                itemstatus = object.get_network_security_group(network_security_group_id=item.id).data
                if itemstatus.lifecycle_state != "TERMINATED":
                    if itemstatus.lifecycle_state != "TERMINATING":
                        try:
                            print("Deleting: {}".format(itemstatus.display_name))
                            object.delete_network_security_group(network_security_group_id=itemstatus.id)
                            count = count + 1
                        except Exception:
                            print("error trying to delete: {}".format(itemstatus.display_name))
                    else:
                        print("{} = {}".format(itemstatus.display_name, itemstatus.lifecycle_state))
                        count = count + 1
            except Exception:
                print("error deleting {}, probably already deleted".format(item.display_name))
        if count > 0:
            print("Waiting for all Objects to be deleted..." + (" Iteration " + str(iteration) + " of " + str(MaxIDeleteIteration) if iteration > 0 else ""))
            time.sleep(WaitRefresh)
            iteration += 1

            if iteration >= MaxIDeleteIteration:
                print("Some Network Security Groups not deleted, skipping!")
                return
        else:
            itemsPresent = False
    print("All Network Security Groups Objects deleted!")


##############################################
# DeleteRouteTables
##############################################
def DeleteRouteTables(config, Compartments, vcn):
    AllItems = []
    object = oci.core.VirtualNetworkClient(config)

    print("Getting Route Tables for {}".format(vcn.display_name))
    for C in Compartments:
        compartment = C.details
        try:
            items = oci.pagination.list_call_get_all_results(object.list_route_tables, compartment_id=compartment.id, vcn_id=vcn.id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY).data
            for item in items:
                if (item.lifecycle_state != "TERMINATED"):
                    AllItems.append(item)
                    details = oci.core.models.UpdateRouteTableDetails()
                    details.route_rules = []

                    print("Emptying route table for {}".format(item.display_name))
                    object.update_route_table(rt_id=item.id, update_route_table_details=details)
                    time.sleep(1)
                print("- {} - {}".format(item.display_name, item.lifecycle_state))
        except Exception:
            print("Error listing for compartment {}".format(compartment.name))
            continue

    itemsPresent = True
    iteration = 0

    while itemsPresent:
        count = 0
        for item in AllItems:
            try:
                itemstatus = object.get_route_table(rt_id=item.id).data
                if itemstatus.lifecycle_state != "TERMINATED":
                    if itemstatus.lifecycle_state != "TERMINATING":
                        try:
                            print("Deleting: {}".format(itemstatus.display_name))
                            object.delete_route_table(rt_id=itemstatus.id)
                            count = count + 1
                        except Exception:
                            print("error trying to delete: {}".format(itemstatus.display_name))
                    else:
                        print("{} = {}".format(itemstatus.display_name, itemstatus.lifecycle_state))
                        count = count + 1
            except Exception:
                print("error deleting {}, probably already deleted".format(item.display_name))
        if count > 0:
            print("Waiting for all Objects to be deleted..." + (" Iteration " + str(iteration) + " of " + str(MaxIDeleteIteration) if iteration > 0 else ""))
            time.sleep(WaitRefresh)
            iteration += 1

            if iteration >= MaxIDeleteIteration:
                print("Some Route Tables not deleted, skipping!")
                return
        else:
            itemsPresent = False
    print("All Route Tables Objects deleted!")


##############################################
# DeleteDRGAttachments
##############################################
def DeleteDRGAttachments(config, compartment):
    AllItems = []
    object = oci.core.VirtualNetworkClient(config)

    print("Getting DRG Attachmentss for {}".format(compartment.name))
    AllItems = oci.pagination.list_call_get_all_results(object.list_drg_attachments, compartment_id=compartment.id).data

    itemsPresent = True
    iteration = 0

    while itemsPresent:
        count = 0
        for item in AllItems:
            try:
                itemstatus = object.get_drg_attachment(drg_attachment_id=item.id).data
                if itemstatus.lifecycle_state != "DETACHING":
                    try:
                        print("Deleting: {}".format(itemstatus.display_name))
                        object.delete_drg_attachment(drg_attachment_id=itemstatus.id)
                    except Exception:
                        print("error trying to delete: {}".format(itemstatus.display_name))
                else:
                    print("{} = {}".format(itemstatus.display_name, itemstatus.lifecycle_state))
                count = count + 1
            except Exception:
                print("error deleting {}, probably already deleted".format(item.display_name))
        if count > 0:
            print("Waiting for all Objects to be deleted..." + (" Iteration " + str(iteration) + " of " + str(MaxIDeleteIteration) if iteration > 0 else ""))
            time.sleep(WaitRefresh)
            iteration += 1

            if iteration >= MaxIDeleteIteration:
                print("Some objects not deleted, skipping!")
                return
        else:
            itemsPresent = False
    print("All DRG Attachmentss Objects deleted!")


##############################################
# DeleteLoadBalancers
##############################################
def DeleteLoadBalancers(config, compartment):
    AllItems = []
    object = oci.load_balancer.LoadBalancerClient(config)

    print("Getting all Load Balancer objects")
    items = oci.pagination.list_call_get_all_results(object.list_load_balancers, compartment_id=compartment.id).data
    for item in items:
        if (item.lifecycle_state != "DELETED"):
            AllItems.append(item)
            print("- {} - {}".format(item.display_name, item.lifecycle_state))

    itemsPresent = True
    iteration = 0

    while itemsPresent:
        count = 0
        for item in AllItems:
            try:
                itemstatus = object.get_load_balancer(load_balancer_id=item.id).data
                if itemstatus.lifecycle_state != "DELETED":
                    if itemstatus.lifecycle_state != "DELETING":
                        try:
                            print("Deleting: {}".format(itemstatus.display_name))
                            object.delete_load_balancer(load_balancer_id=itemstatus.id)
                        except Exception:
                            print("error trying to delete: {}".format(itemstatus.display_name))
                    else:
                        print("{} = {}".format(itemstatus.display_name, itemstatus.lifecycle_state))
                    count = count + 1
            except Exception:
                print("error deleting {}, probably already deleted".format(item.display_name))
        if count > 0:
            print("Waiting for all Objects to be deleted..." + (" Iteration " + str(iteration) + " of " + str(MaxIDeleteIteration) if iteration > 0 else ""))
            time.sleep(WaitRefresh)
            iteration += 1

            if iteration >= MaxIDeleteIteration:
                print("Some Load Balancers not deleted, skipping!")
                return
        else:
            itemsPresent = False
    print("All Load Balancer Objects deleted!")


##############################################
# DeleteReservedIPs
##############################################
def DeleteReservedIPs(config, compartment):
    AllItems = []
    object = oci.core.VirtualNetworkClient(config)

    print("Getting all Reserved IP objects")
    items = oci.pagination.list_call_get_all_results(object.list_public_ips, scope="REGION", compartment_id=compartment.id, lifetime="RESERVED").data

    for item in items:
        if (item.lifecycle_state != "TERMINATED"):
            AllItems.append(item)
        print("- {} - {}".format(item.display_name, item.lifecycle_state))

    itemsPresent = True
    iteration = 0

    if itemsPresent:
        count = 0
        for item in AllItems:
            try:
                itemstatus = object.get_public_ip(public_ip_id=item.id).data
                if itemstatus.lifecycle_state != "TERMINATED":
                    if itemstatus.lifecycle_state != "TERMINATING":
                        try:
                            print("Deleting: {}".format(itemstatus.display_name))
                            object.delete_public_ip(public_ip_id=itemstatus.id)
                        except Exception:
                            print("error trying to delete: {}".format(itemstatus.display_name))
                    else:
                        print("{} = {}".format(itemstatus.display_name, itemstatus.lifecycle_state))
                    count = count + 1
            except Exception:
                print("error deleting {}, probably already deleted".format(item.display_name))
        if count > 0:
            print("Waiting for all Objects to be deleted..." + (" Iteration " + str(iteration) + " of " + str(MaxIDeleteIteration) if iteration > 0 else ""))
            time.sleep(WaitRefresh)
            iteration += 1

            if iteration >= MaxIDeleteIteration:
                print("Some objects not deleted, skipping!")
                return
        else:
            itemsPresent = False

    print("All Reserved IP Objects deleted!")


##############################################
# DeleteInternetGateways
##############################################
def DeleteInternetGateways(config, Compartments, vcn):
    AllItems = []
    object = oci.core.VirtualNetworkClient(config)

    print("Getting all Internet Gateway objects")
    for C in Compartments:
        compartment = C.details
        try:
            items = oci.pagination.list_call_get_all_results(object.list_internet_gateways, compartment_id=compartment.id, vcn_id=vcn.id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY).data
            for item in items:
                if (item.lifecycle_state != "TERMINATED"):
                    AllItems.append(item)
                print("- {} - {}".format(item.display_name, item.lifecycle_state))
        except Exception:
            print("Error listing for compartment {}".format(compartment.name))
            continue

    itemsPresent = True
    iteration = 0

    if itemsPresent:
        count = 0
        for item in AllItems:
            try:
                itemstatus = object.get_internet_gateway(ig_id=item.id).data
                if itemstatus.lifecycle_state != "TERMINATED":
                    if itemstatus.lifecycle_state != "TERMINATING":
                        try:
                            print("Deleting: {}".format(itemstatus.display_name))
                            object.delete_internet_gateway(ig_id=itemstatus.id)
                        except Exception:
                            print("error trying to delete: {}".format(itemstatus.display_name))
                    else:
                        print("{} = {}".format(itemstatus.display_name, itemstatus.lifecycle_state))
                    count = count + 1
            except Exception:
                print("error deleting {}, probably already deleted".format(item.display_name))
        if count > 0:
            print("Waiting for all Objects to be deleted..." + (" Iteration " + str(iteration) + " of " + str(MaxIDeleteIteration) if iteration > 0 else ""))
            time.sleep(WaitRefresh)
            iteration += 1

            if iteration >= MaxIDeleteIteration:
                print("Some objects not deleted, skipping!")
                return
        else:
            itemsPresent = False

    print("All Internet Gateway Objects deleted!")


##############################################
# DeleteServiceGateways
##############################################
def DeleteServiceGateways(config, Compartments, vcn):
    AllItems = []
    object = oci.core.VirtualNetworkClient(config)

    print("Getting all Service Gateway objects")
    for C in Compartments:
        compartment = C.details
        try:
            items = oci.pagination.list_call_get_all_results(object.list_service_gateways, compartment_id=compartment.id, vcn_id=vcn.id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY).data
            for item in items:
                if (item.lifecycle_state != "TERMINATED"):
                    AllItems.append(item)
                print("- {} - {}".format(item.display_name, item.lifecycle_state))
        except Exception:
            print("Error listing for compartment {}".format(compartment.name))
            continue

    itemsPresent = True
    iteration = 0

    if itemsPresent:
        count = 0
        for item in AllItems:
            try:
                itemstatus = object.get_service_gateway(service_gateway_id=item.id).data
                if itemstatus.lifecycle_state != "TERMINATED":
                    if itemstatus.lifecycle_state != "TERMINATING":
                        try:
                            print("Deleting: {}".format(itemstatus.display_name))
                            object.delete_service_gateway(service_gateway_id=itemstatus.id)
                        except Exception:
                            print("error trying to delete: {}".format(itemstatus.display_name))
                    else:
                        print("{} = {}".format(itemstatus.display_name, itemstatus.lifecycle_state))
                    count = count + 1
            except Exception:
                print("error deleting {}, probably already deleted".format(item.display_name))
        if count > 0:
            print("Waiting for all Objects to be deleted..." + (" Iteration " + str(iteration) + " of " + str(MaxIDeleteIteration) if iteration > 0 else ""))
            time.sleep(WaitRefresh)
            iteration += 1

            if iteration >= MaxIDeleteIteration:
                print("Some objects not deleted, skipping!")
                return
        else:
            itemsPresent = False

    print("All Service Gateway Objects deleted!")


##############################################
# DeleteNATGateways
##############################################
def DeleteNATGateways(config, Compartments, vcn):
    AllItems = []
    object = oci.core.VirtualNetworkClient(config)

    print("Getting all NAT Gateway objects")
    for C in Compartments:
        compartment = C.details
        try:
            items = oci.pagination.list_call_get_all_results(object.list_nat_gateways, compartment_id=compartment.id, vcn_id=vcn.id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY).data
            for item in items:
                if (item.lifecycle_state != "TERMINATED"):
                    AllItems.append(item)
                print("- {} - {}".format(item.display_name, item.lifecycle_state))
        except Exception:
            print("Error listing for compartment {}".format(compartment.name))
            continue

    itemsPresent = True
    iteration = 0

    if itemsPresent:
        count = 0
        for item in AllItems:
            try:
                itemstatus = object.get_nat_gateway(nat_gateway_id=item.id).data
                if itemstatus.lifecycle_state != "TERMINATED":
                    if itemstatus.lifecycle_state != "TERMINATING":
                        try:
                            print("Deleting: {}".format(itemstatus.display_name))
                            object.delete_nat_gateway(nat_gateway_id=itemstatus.id)
                        except Exception:
                            print("error trying to delete: {}".format(itemstatus.display_name))
                    else:
                        print("{} = {}".format(itemstatus.display_name, itemstatus.lifecycle_state))
                    count = count + 1
            except Exception:
                print("error deleting {}, probably already deleted".format(item.display_name))
        if count > 0:
            print("Waiting for all Objects to be deleted..." + (" Iteration " + str(iteration) + " of " + str(MaxIDeleteIteration) if iteration > 0 else ""))
            time.sleep(WaitRefresh)
            iteration += 1

            if iteration >= MaxIDeleteIteration:
                print("Some objects not deleted, skipping!")
                return
        else:
            itemsPresent = False

    print("All NAT Gateway Objects deleted!")


##############################################
# DeleteLocalPeeringGateways
##############################################
def DeleteLocalPeeringGateways(config, Compartments, vcn):
    AllItems = []
    object = oci.core.VirtualNetworkClient(config)

    print("Getting all Local Peering Gateways objects")
    for C in Compartments:
        compartment = C.details
        try:
            items = oci.pagination.list_call_get_all_results(object.list_local_peering_gateways, compartment_id=compartment.id, vcn_id=vcn.id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY).data
            for item in items:
                if (item.lifecycle_state != "TERMINATED"):
                    AllItems.append(item)
                print("- {} - {}".format(item.display_name, item.lifecycle_state))
        except Exception:
            print("Error listing for compartment {}".format(compartment.name))
            continue

    itemsPresent = True
    iteration = 0

    if itemsPresent:
        count = 0
        for item in AllItems:
            try:
                itemstatus = object.get_local_peering_gateway(local_peering_gateway_id=item.id).data
                if itemstatus.lifecycle_state != "TERMINATED":
                    if itemstatus.lifecycle_state != "TERMINATING":
                        try:
                            print("Deleting: {}".format(itemstatus.display_name))
                            object.delete_local_peering_gateway(local_peering_gateway_id=itemstatus.id)
                        except Exception:
                            print("error trying to delete: {}".format(itemstatus.display_name))
                    else:
                        print("{} = {}".format(itemstatus.display_name, itemstatus.lifecycle_state))
                    count = count + 1
            except Exception:
                print("error deleting {}, probably already deleted".format(item.display_name))
        if count > 0:
            print("Waiting for all Objects to be deleted..." + (" Iteration " + str(iteration) + " of " + str(MaxIDeleteIteration) if iteration > 0 else ""))
            time.sleep(WaitRefresh)
            iteration += 1

            if iteration >= MaxIDeleteIteration:
                print("Some Local Peering Objects not deleted, skipping!")
                return
        else:
            itemsPresent = False

    print("All Local Peering Gateways Objects deleted!")


##############################################
# DeleteDRGs
##############################################
def DeleteDRGs(config, compartment):
    AllItems = []
    object = oci.core.VirtualNetworkClient(config)

    print("Getting all DRG objects")
    items = oci.pagination.list_call_get_all_results(object.list_drgs, compartment_id=compartment.id).data

    for item in items:
        if (item.lifecycle_state != "TERMINATED"):
            AllItems.append(item)
        print("- {} - {}".format(item.display_name, item.lifecycle_state))

    itemsPresent = True
    iteration = 0

    if itemsPresent:
        count = 0
        for item in AllItems:
            try:
                itemstatus = object.get_drg(drg_id=item.id).data
                if itemstatus.lifecycle_state != "TERMINATED":
                    if itemstatus.lifecycle_state != "TERMINATING":
                        try:
                            print("Deleting: {}".format(itemstatus.display_name))
                            object.delete_drg(drg_id=itemstatus.id)
                        except Exception:
                            print("error trying to delete: {}".format(itemstatus.display_name))
                    else:
                        print("{} = {}".format(itemstatus.display_name, itemstatus.lifecycle_state))
                    count = count + 1
            except Exception:
                print("error deleting {}, probably already deleted".format(item.display_name))
        if count > 0:
            print("Waiting for all Objects to be deleted..." + (" Iteration " + str(iteration) + " of " + str(MaxIDeleteIteration) if iteration > 0 else ""))
            time.sleep(WaitRefresh)
            iteration += 1

            if iteration >= MaxIDeleteIteration:
                print("Some DRG Objects not deleted, skipping!")
                return
        else:
            itemsPresent = False

    print("All DRG Objects deleted!")


##############################################
# DeleteDNSResolvers
##############################################
def DeleteDNSResolvers(config, compartment):
    AllItems = []
    object = oci.dns.DnsClient(config)

    print("Getting all DNS Resolvers objects")
    items = oci.pagination.list_call_get_all_results(object.list_resolvers, compartment_id=compartment.id).data
    for item in items:
        if (item.lifecycle_state != "DELETED"):
            AllItems.append(item)
            print("- {} - {}".format(item.display_name, item.lifecycle_state))

    itemsPresent = True
    iteration = 0

    while itemsPresent:
        count = 0
        for item in AllItems:
            try:
                itemstatus = object.get_resolver(item.id, scope="PRIVATE").data
                if itemstatus.lifecycle_state != "DELETED":
                    if itemstatus.lifecycle_state != "DELETING":

                        # remove resolver rules first
                        if itemstatus.rules:
                            try:
                                updateResolverDetails = oci.dns.models.UpdateResolverDetails(
                                    display_name=itemstatus.display_name,
                                    freeform_tags={},
                                    defined_tags={},
                                    attached_views=[],
                                    rules=[]
                                )
                                object.update_resolver(resolver_id=itemstatus.id, update_resolver_details=updateResolverDetails)
                            except Exception as e:
                                print("error trying to delete resolver rules: {} - {}".format(itemstatus.display_name, str(e)))

                        for ep in itemstatus.endpoints:
                            try:
                                print("Deleting: {} - {}".format(itemstatus.display_name, ep.name))
                                object.delete_resolver_endpoint(resolver_id=itemstatus.id, resolver_endpoint_name=ep.name)
                            except Exception as e:
                                print("error trying to delete resolver endpoint: {} - {} - {}".format(itemstatus.display_name, ep.name, str(e)))
                    else:
                        print("{} = {}".format(itemstatus.display_name, itemstatus.lifecycle_state))
                    count = count + 1
            except Exception:
                print("error deleting {}, probably already deleted".format(item.display_name))
        if count > 0:
            print("Waiting for all Objects to be deleted..." + (" Iteration " + str(iteration) + " of " + str(MaxIDeleteIteration) if iteration > 0 else ""))
            time.sleep(WaitRefresh)
            iteration += 1

            if iteration >= MaxIDeleteIteration:
                print("Some DNS Resolvers not deleted, skipping!")
                return
        else:
            itemsPresent = False
    print("All DNS Resolvers Objects deleted!")


##############################################
# DeleteCPEs
##############################################
def DeleteCPEs(config, compartment):
    object = oci.core.VirtualNetworkClient(config)

    print("Getting all CPE objects")
    itemsPresent = True
    iteration = 0

    if itemsPresent:
        count = 0
        items = oci.pagination.list_call_get_all_results(object.list_cpes, compartment_id=compartment.id).data

        for item in items:
            count = count + 1
            print("{}".format(item.display_name))

            try:
                print("Deleting: {}".format(item.display_name))
                object.delete_cpe(cpe_id=item.id)
            except Exception:
                print("error trying to delete: {}".format(item.display_name))

        if count > 0:
            print("Waiting for all Objects to be deleted..." + (" Iteration " + str(iteration) + " of " + str(MaxIDeleteIteration) if iteration > 0 else ""))
            time.sleep(WaitRefresh)
            iteration += 1

            if iteration >= MaxIDeleteIteration:
                print("Some CPEs not deleted, skipping!")
                return
        else:
            itemsPresent = False

    print("All CPE Objects deleted!")


##############################################
# DeleteDRGs
##############################################
def DeleteIPSecConnections(config, compartment):
    AllItems = []
    object = oci.core.VirtualNetworkClient(config)

    print("Getting all IPSEC Connection objects")
    try:
        items = oci.pagination.list_call_get_all_results(object.list_ip_sec_connections, compartment_id=compartment.id).data
    except:
        items = []

    for item in items:
        if (item.lifecycle_state != "TERMINATED"):
            AllItems.append(item)
        print("- {} - {}".format(item.display_name, item.lifecycle_state))

    itemsPresent = True
    iteration = 0

    if itemsPresent:
        count = 0
        for item in AllItems:
            try:
                itemstatus = object.get_ip_sec_connection(ipsc_id=item.id).data
                if itemstatus.lifecycle_state != "TERMINATED":
                    if itemstatus.lifecycle_state != "TERMINATING":
                        try:
                            print("Deleting: {}".format(itemstatus.display_name))
                            object.delete_ip_sec_connection(ipsc_id=itemstatus.id)
                        except Exception:
                            print("error trying to delete: {}".format(itemstatus.display_name))
                    else:
                        print("{} = {}".format(itemstatus.display_name, itemstatus.lifecycle_state))
                    count = count + 1
            except Exception as e:
                print("error deleting {}, {}".format(item.display_name, str(e)))
        if count > 0:
            print("Waiting for all Objects to be deleted..." + (" Iteration " + str(iteration) + " of " + str(MaxIDeleteIteration) if iteration > 0 else ""))
            time.sleep(WaitRefresh)
            iteration += 1

            if iteration >= MaxIDeleteIteration:
                print("Some IPSEC Connection not deleted, skipping!")
                return
        else:
            itemsPresent = False

    print("All IPSEC Connection Objects deleted!")
