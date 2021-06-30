import oci
import time

WaitRefresh = 10

def DeleteBlockchain(config, Compartments):
    AllItems = []
    object = oci.blockchain.BlockchainPlatformClient(config)

    print ("Getting all Blockchain objects")
    try:
        for Compartment in Compartments:
            items = oci.pagination.list_call_get_all_results(object.list_blockchain_platforms, compartment_id=Compartment.id).data
            for item in items:
                if (item.lifecycle_state != "DELETED"):
                    AllItems.append(item)
                    print("- {} - {}".format(item.display_name, item.lifecycle_state))

        itemsPresent = True
    except oci.exceptions.ServiceError as response:
        if response.status == 404:
            print ("Ignoring this service, as not available in this region")
        else:
            pritn ("Error getting blockchain service")
        itemsPresent = False


    while itemsPresent:
        count = 0
        for item in AllItems:
            try:
                itemstatus = object.get_blockchain_platform(blockchain_platform_id =item.id).data
                if itemstatus.lifecycle_state != "DELETED":
                    if itemstatus.lifecycle_state != "DELETING":
                        try:
                            print ("Deleting: {}".format(itemstatus.display_name))
                            object.delete_blockchain_platform(blockchain_platform_id=itemstatus.id)
                        except:
                            print ("error trying to delete: {}".format(itemstatus.display_name))
                    else:
                        print("{} = {}".format(itemstatus.display_name, itemstatus.lifecycle_state))
                    count = count + 1
            except:

                print ("-----------------> error deleting {}, probably already deleted: {}.".format(item.display_name, item.lifecycle_state))
        if count > 0 :
            print ("Waiting for all Objects to be deleted...")
            time.sleep(WaitRefresh)
        else:
            itemsPresent = False
    print ("All Objects deleted!")