import oci
import time

WaitRefresh = 15

def DeleteVCN(config,compartments):
    AllItems = []
    object = oci.core.VirtualNetworkClient(config)

    print ("Getting all VCN objects")
    for Compartment in compartments:
        DeleteLoadBalancers(config, Compartment)
        DeleteReservedIPs(config, Compartment)

        items = oci.pagination.list_call_get_all_results(object.list_vcns, compartment_id=Compartment.id).data
        for item in items:
              if (item.lifecycle_state != "TERMINATED"):
                AllItems.append(item)
                print("- {} - {}".format(item.display_name, item.lifecycle_state))

        for item in AllItems:
            print ("----[ Deleting components of VCN: {} ]---".format(item.display_name))
            DeleteSubnets(config,Compartment, item)
            DeleteDHCPoptions(config,Compartment, item)
            DeleteSecurityLists(config, Compartment, item)
            DeleteRouteTables(config, Compartment, item)
            DeleteInternetGateways(config, Compartment, item)
            DeleteServiceGateways(config, Compartment, item)
            DeleteNATGateways(config, Compartment, item)
            DeleteLocalPeeringGateways(config, Compartment, item)

        DeleteDRGs(config, Compartment)

    print ("Getting all VCNs")
    deleting = True
    while deleting:
        deleting = False
        for Compartment in compartments:
            items = oci.pagination.list_call_get_all_results(object.list_vcns, compartment_id=Compartment.id).data
            for item in items:
                if (item.lifecycle_state != "TERMINATED"):
                    deleting = True
                    AllItems.append(item)
                    print("- {} - {}".format(item.display_name, item.lifecycle_state))
                    if (item.lifecycle_state != "TERMINATING"):
                        object.delete_vcn(vcn_id=item.id)








def DeleteSubnets(config, compartment, vcn):
    AllItems = []
    object = oci.core.VirtualNetworkClient(config)

    print ("Getting subnets for {}".format(vcn.display_name))
    items = oci.pagination.list_call_get_all_results(object.list_subnets, compartment_id=compartment.id,vcn_id=vcn.id).data
    for item in items:
        if (item.lifecycle_state != "TERMINATED"):
            AllItems.append(item)
        print("- {} - {}".format(item.display_name, item.lifecycle_state))

    itemsPresent = True

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
                        except:
                            print("error trying to delete: {}".format(itemstatus.display_name))
                    else:
                        print("{} = {}".format(itemstatus.display_name, itemstatus.lifecycle_state))
                    count = count + 1
            except:
                print("error deleting {}, probably already deleted".format(item.display_name))
        if count > 0:
            print("Waiting for all Objects to be deleted...")
            time.sleep(WaitRefresh)
        else:
            itemsPresent = False
    print("All Objects deleted!")

def DeleteDHCPoptions(config, compartment, vcn):
    AllItems = []
    object = oci.core.VirtualNetworkClient(config)

    print ("Getting DHCP options for {}".format(vcn.display_name))
    items = oci.pagination.list_call_get_all_results(object.list_dhcp_options, compartment_id=compartment.id,vcn_id=vcn.id).data
    for item in items:
        if (item.lifecycle_state != "TERMINATED"):
            AllItems.append(item)
        print("- {} - {}".format(item.display_name, item.lifecycle_state))

    itemsPresent = True

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
                        except Exception as e:
                            print("error trying to delete: {}".format(itemstatus.display_name))
                            #print (e)
                    else:
                        print("{} = {}".format(itemstatus.display_name, itemstatus.lifecycle_state))
                        count = count + 1
            except:
                print("error deleting {}, probably already deleted".format(item.display_name))
                print (e)
        if count > 0:
            print("Waiting for all Objects to be deleted...")
            time.sleep(WaitRefresh)
        else:
            itemsPresent = False
    print("All Objects deleted!")

def DeleteSecurityLists(config, compartment, vcn):
    AllItems = []
    object = oci.core.VirtualNetworkClient(config)

    print ("Getting SecurityLists for {}".format(vcn.display_name))
    items = oci.pagination.list_call_get_all_results(object.list_security_lists, compartment_id=compartment.id,vcn_id=vcn.id).data
    for item in items:
        if (item.lifecycle_state != "TERMINATED"):
            AllItems.append(item)
        print("- {} - {}".format(item.display_name, item.lifecycle_state))

    itemsPresent = True

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
                        except:
                            print("error trying to delete: {}".format(itemstatus.display_name))
                    else:
                        print("{} = {}".format(itemstatus.display_name, itemstatus.lifecycle_state))
                        count = count + 1
            except:
                print("error deleting {}, probably already deleted".format(item.display_name))
        if count > 0:
            print("Waiting for all Objects to be deleted...")
            time.sleep(WaitRefresh)
        else:
            itemsPresent = False
    print("All Objects deleted!")

def DeleteRouteTables(config, compartment, vcn):
    AllItems = []
    object = oci.core.VirtualNetworkClient(config)

    print ("Getting Route Tables for {}".format(vcn.display_name))
    items = oci.pagination.list_call_get_all_results(object.list_route_tables, compartment_id=compartment.id,vcn_id=vcn.id).data
    for item in items:
        if (item.lifecycle_state != "TERMINATED"):
            AllItems.append(item)
            details = oci.core.models.UpdateRouteTableDetails()
            details.route_rules = []

            print ("Emptying route table for {}".format(item.display_name))
            result = object.update_route_table(rt_id=item.id, update_route_table_details=details)
            time.sleep(1)

        print("- {} - {}".format(item.display_name, item.lifecycle_state))

    itemsPresent = True

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
                        except:
                            print("error trying to delete: {}".format(itemstatus.display_name))
                    else:
                        print("{} = {}".format(itemstatus.display_name, itemstatus.lifecycle_state))
                        count = count + 1
            except:
                print("error deleting {}, probably already deleted".format(item.display_name))
        if count > 0:
            print("Waiting for all Objects to be deleted...")
            time.sleep(WaitRefresh)
        else:
            itemsPresent = False
    print("All Objects deleted!")

def DeleteDRGAttachments(config, compartment):
    AllItems = []
    object = oci.core.VirtualNetworkClient(config)

    print ("Getting DRG Attachmentss for {}".format(compartment.name))
    AllItems = oci.pagination.list_call_get_all_results(object.list_drg_attachments, compartment_id=compartment.id).data
    itemsPresent = True

    while itemsPresent:
        count = 0
        for item in AllItems:
            try:
                itemstatus = object.get_drg_attachment(drg_attachment_id=item.id).data
                if itemstatus.lifecycle_state != "DETACHING":
                    try:
                        print("Deleting: {}".format(itemstatus.display_name))
                        object.delete_drg_attachment(drg_attachment_id=itemstatus.id)
                    except:
                        print("error trying to delete: {}".format(itemstatus.display_name))
                else:
                    print("{} = {}".format(itemstatus.display_name, itemstatus.lifecycle_state))
                count = count + 1
            except:
                print("error deleting {}, probably already deleted".format(item.display_name))
        if count > 0:
            print("Waiting for all Objects to be deleted...")
            time.sleep(WaitRefresh)
        else:
            itemsPresent = False
    print("All Objects deleted!")

def DeleteDRGs(config, compartment):
    AllItems = []
    object = oci.core.VirtualNetworkClient(config)

    print ("Getting DRGs for {}".format(compartment.name))
    AllItems = oci.pagination.list_call_get_all_results(object.list_drgs, compartment_id=compartment.id).data
    itemsPresent = True

    while itemsPresent:
        count = 0
        for item in AllItems:
            try:
                itemstatus = object.get_drg_attachment(drg_attachment_id=item.id).data
                if itemstatus.lifecycle_state != "TERMINATED":
                    if itemstatus.lifecycle_state != "TERMINATING":
                        try:
                            print("Deleting: {}".format(itemstatus.display_name))
                            object.delete_drg(drg_id=itemstatus.id)
                        except:
                            print("error trying to delete: {}".format(itemstatus.display_name))
                    else:
                        print("{} = {}".format(itemstatus.display_name, itemstatus.lifecycle_state))
                count = count + 1
            except:
                print("error deleting {}, probably already deleted".format(item.display_name))
        if count > 0:
            print("Waiting for all Objects to be deleted...")
            time.sleep(WaitRefresh)
        else:
            itemsPresent = False
    print("All Objects deleted!")

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
                        except:
                            print("error trying to delete: {}".format(itemstatus.display_name))
                    else:
                        print("{} = {}".format(itemstatus.display_name, itemstatus.lifecycle_state))
                    count = count + 1
            except:
                print("error deleting {}, probably already deleted".format(item.display_name))
        if count > 0:
            print("Waiting for all Objects to be deleted...")
            time.sleep(WaitRefresh)
        else:
            itemsPresent = False
    print("All Objects deleted!")

def DeleteReservedIPs(config, compartment):
    AllItems = []
    object = oci.core.VirtualNetworkClient(config)

    print("Getting all Reserved IP objects")
    items = oci.pagination.list_call_get_all_results(object.list_public_ips, scope="REGION",compartment_id=compartment.id, lifetime="RESERVED").data

    for item in items:
        if (item.lifecycle_state != "TERMINATED"):
            AllItems.append(item)
        print("- {} - {}".format(item.display_name, item.lifecycle_state))

    itemsPresent = True

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
                        except:
                            print("error trying to delete: {}".format(itemstatus.display_name))
                    else:
                        print("{} = {}".format(itemstatus.display_name, itemstatus.lifecycle_state))
                    count = count + 1
            except:
                print("error deleting {}, probably already deleted".format(item.display_name))
        if count > 0:
            print("Waiting for all Objects to be deleted...")
            time.sleep(WaitRefresh)
        else:
            itemsPresent = False

    print("All Objects deleted!")

def DeleteInternetGateways(config, compartment, vcn):
    AllItems = []
    object = oci.core.VirtualNetworkClient(config)

    print("Getting all Internet Gateway objects")
    items = oci.pagination.list_call_get_all_results(object.list_internet_gateways,compartment_id=compartment.id, vcn_id=vcn.id).data

    for item in items:
        if (item.lifecycle_state != "TERMINATED"):
            AllItems.append(item)
        print("- {} - {}".format(item.display_name, item.lifecycle_state))

    itemsPresent = True

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
                        except:
                            print("error trying to delete: {}".format(itemstatus.display_name))
                    else:
                        print("{} = {}".format(itemstatus.display_name, itemstatus.lifecycle_state))
                    count = count + 1
            except:
                print("error deleting {}, probably already deleted".format(item.display_name))
        if count > 0:
            print("Waiting for all Objects to be deleted...")
            time.sleep(WaitRefresh)
        else:
            itemsPresent = False

    print("All Objects deleted!")

def DeleteServiceGateways(config, compartment, vcn):
    AllItems = []
    object = oci.core.VirtualNetworkClient(config)

    print("Getting all Service Gateway objects")
    items = oci.pagination.list_call_get_all_results(object.list_service_gateways,compartment_id=compartment.id, vcn_id=vcn.id).data

    for item in items:
        if (item.lifecycle_state != "TERMINATED"):
            AllItems.append(item)
        print("- {} - {}".format(item.display_name, item.lifecycle_state))

    itemsPresent = True

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
                        except:
                            print("error trying to delete: {}".format(itemstatus.display_name))
                    else:
                        print("{} = {}".format(itemstatus.display_name, itemstatus.lifecycle_state))
                    count = count + 1
            except:
                print("error deleting {}, probably already deleted".format(item.display_name))
        if count > 0:
            print("Waiting for all Objects to be deleted...")
            time.sleep(WaitRefresh)
        else:
            itemsPresent = False

    print("All Objects deleted!")

def DeleteNATGateways(config, compartment, vcn):
    AllItems = []
    object = oci.core.VirtualNetworkClient(config)

    print("Getting all NAT Gateway objects")
    items = oci.pagination.list_call_get_all_results(object.list_nat_gateways,compartment_id=compartment.id, vcn_id=vcn.id).data

    for item in items:
        if (item.lifecycle_state != "TERMINATED"):
            AllItems.append(item)
        print("- {} - {}".format(item.display_name, item.lifecycle_state))

    itemsPresent = True

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
                        except:
                            print("error trying to delete: {}".format(itemstatus.display_name))
                    else:
                        print("{} = {}".format(itemstatus.display_name, itemstatus.lifecycle_state))
                    count = count + 1
            except:
                print("error deleting {}, probably already deleted".format(item.display_name))
        if count > 0:
            print("Waiting for all Objects to be deleted...")
            time.sleep(WaitRefresh)
        else:
            itemsPresent = False

    print("All Objects deleted!")

def DeleteLocalPeeringGateways(config, compartment, vcn):
    AllItems = []
    object = oci.core.VirtualNetworkClient(config)

    print("Getting all Local Peering Gateways objects")
    items = oci.pagination.list_call_get_all_results(object.list_local_peering_gateways,compartment_id=compartment.id, vcn_id=vcn.id).data

    for item in items:
        if (item.lifecycle_state != "TERMINATED"):
            AllItems.append(item)
        print("- {} - {}".format(item.display_name, item.lifecycle_state))

    itemsPresent = True

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
                        except:
                            print("error trying to delete: {}".format(itemstatus.display_name))
                    else:
                        print("{} = {}".format(itemstatus.display_name, itemstatus.lifecycle_state))
                    count = count + 1
            except:
                print("error deleting {}, probably already deleted".format(item.display_name))
        if count > 0:
            print("Waiting for all Objects to be deleted...")
            time.sleep(WaitRefresh)
        else:
            itemsPresent = False

    print("All Objects deleted!")   

def DeleteDRGs(config, compartment):
    AllItems = []
    object = oci.core.VirtualNetworkClient(config)

    print("Getting all DRG objects")
    items = oci.pagination.list_call_get_all_results(object.list_drgs,compartment_id=compartment.id).data

    for item in items:
        if (item.lifecycle_state != "TERMINATED"):
            AllItems.append(item)
        print("- {} - {}".format(item.display_name, item.lifecycle_state))

    itemsPresent = True

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
                        except:
                            print("error trying to delete: {}".format(itemstatus.display_name))
                    else:
                        print("{} = {}".format(itemstatus.display_name, itemstatus.lifecycle_state))
                    count = count + 1
            except:
                print("error deleting {}, probably already deleted".format(item.display_name))
        if count > 0:
            print("Waiting for all Objects to be deleted...")
            time.sleep(WaitRefresh)
        else:
            itemsPresent = False

    print("All Objects deleted!")
