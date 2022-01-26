import oci
import time

WaitRefresh = 15


##############################################
# DeleteAPM
##############################################
def DeleteAPM(config, compartments):
    object = oci.apm_control_plane.ApmDomainClient(config)

    print("Getting all Application Performanance Monitoring objects")
    for C in compartments:
        Compartment = C.details
        AllItems = []

        items = oci.pagination.list_call_get_all_results(object.list_apm_domains, compartment_id=Compartment.id).data
        for item in items:
            if (item.lifecycle_state != "TERMINATED"):
                AllItems.append(item)
                print("- {} - {}".format(item.display_name, item.lifecycle_state))

        for item in AllItems:

            if not item.is_free_tier:
                print("----[ Deleting components of APM Domain: {} ]---".format(item.display_name))
                DeleteSyntheticMonitoring(config, Compartment, item)
                DeleteSyntheticScripts(config, Compartment, item)

            print("---[ Deleting APM Domain ]----")
            deleted = False
            if not deleted:
                try:
                    print("Deleting: {}".format(item.display_name))
                    object.delete_apm_domain(apm_domain_id=item.id)
                    deleted = True
                except Exception:
                    print("error trying to delete: {}".format(items.display_name))
                    time.sleep(5)


##############################################
# DeleteSyntheticMonitoring
##############################################
def DeleteSyntheticMonitoring(config, compartment, apmDomain):
    AllItems = []
    object = oci.apm_synthetics.ApmSyntheticClient(config)

    print("Getting APM Synthetic Monitoring for {}".format(apmDomain.display_name))
    items = oci.pagination.list_call_get_all_results(object.list_monitors, apm_domain_id=apmDomain.id).data
    for item in items:
        if (item.lifecycle_state != "TERMINATED"):
            AllItems.append(item)
        print("- {} - {}".format(item.display_name, item.lifecycle_state))

    itemsPresent = True

    while itemsPresent:
        count = 0
        for item in AllItems:
            try:
                itemstatus = object.get_monitor(apm_domain_id=apmDomain.id, monitor_id=item.id).data
                if itemstatus.lifecycle_state != "TERMINATED":
                    if itemstatus.lifecycle_state != "TERMINATING":
                        try:
                            print("Deleting: {}".format(itemstatus.display_name))
                            object.get_monitor(apm_domain_id=apmDomain.id, monitor_id=item.id)
                        except Exception:
                            print("error trying to delete: {}".format(itemstatus.display_name))
                    else:
                        print("{} = {}".format(itemstatus.display_name, itemstatus.lifecycle_state))
                    count = count + 1
            except Exception:
                print("error deleting {}, probably already deleted".format(item.display_name))
        if count > 0:
            print("Waiting for all Objects to be deleted...")
            time.sleep(WaitRefresh)
        else:
            itemsPresent = False
    print("All APM SyntheticMonitoring Objects deleted!")


##############################################
# DeleteSyntheticScripts
##############################################
def DeleteSyntheticScripts(config, compartment, apmDomain):
    AllItems = []
    object = oci.apm_synthetics.ApmSyntheticClient(config)

    print("Getting APM Synthetic Scripts for {}".format(apmDomain.display_name))
    items = oci.pagination.list_call_get_all_results(object.list_scripts, apm_domain_id=apmDomain.id).data
    for item in items:
        if (item.lifecycle_state != "TERMINATED"):
            AllItems.append(item)
        print("- {} - {}".format(item.display_name, item.lifecycle_state))

    itemsPresent = True

    while itemsPresent:
        count = 0
        for item in AllItems:
            try:
                itemstatus = object.get_script(apm_domain_id=apmDomain.id, script_id=item.id).data
                if itemstatus.lifecycle_state != "TERMINATED":
                    if itemstatus.lifecycle_state != "TERMINATING":
                        try:
                            print("Deleting: {}".format(itemstatus.display_name))
                            object.delete_script(apm_domain_id=apmDomain.id, script_id=item.id)
                        except Exception:
                            print("error trying to delete: {}".format(itemstatus.display_name))
                    else:
                        print("{} = {}".format(itemstatus.display_name, itemstatus.lifecycle_state))
                    count = count + 1
            except Exception:
                print("error deleting {}, probably already deleted".format(item.display_name))
        if count > 0:
            print("Waiting for all Objects to be deleted...")
            time.sleep(WaitRefresh)
        else:
            itemsPresent = False
    print("All APM SyntheticScripts Objects deleted!")
