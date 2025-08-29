import oci
import time


WaitRefresh = 10
MaxIDeleteIteration = 5

##############################################
# DeleteMarketplacePublications
##############################################
def DeleteMarketplacePublications(config, signer, compartments):
    AllItems = []
    object = oci.marketplace.MarketplaceClient(config, signer=signer)

    for compartment in compartments:
        print("Getting all Marketplace Listings", end="\r")
        try:
            items = oci.pagination.list_call_get_all_results(object.list_publications, compartment_id=compartment.details.id, listing_type="COMMUNITY").data
        except Exception as e:
            print("Error getting Marketplace Listings, skipping! - " + str(e))
            items = []

        for item in items:
            if (item.lifecycle_state != "TERMINATED"):
                AllItems.append(item)
            print("- {} - {}".format(item.name, item.lifecycle_state))

        itemsPresent = True
        iteration = 0

        if itemsPresent:
            count = 0
            for item in AllItems:
                try:
                    itemstatus = object.get_publication(publication_id=item.id).data
                    if itemstatus.lifecycle_state != "TERMINATED":
                        if itemstatus.lifecycle_state != "TERMINATING":
                            try:
                                print("Deleting: {}".format(itemstatus.name))
                                object.delete_publication(publication_id=itemstatus.id)
                            except Exception:
                                print("----------> error trying to delete: {}".format(itemstatus.name))
                        else:
                            print("{} = {}".format(itemstatus.name, itemstatus.lifecycle_state))
                        count = count + 1
                except Exception as e:
                    print("error deleting {}, {}".format(item.name, str(e)))
            if count > 0:
                print("Waiting for all Objects to be deleted..." + (" Iteration " + str(iteration) + " of " + str(MaxIDeleteIteration) if iteration > 0 else ""), end="\r")
                time.sleep(WaitRefresh)
                iteration += 1

                if iteration >= MaxIDeleteIteration:
                    print("Some Marketplace Publications not deleted, skipping!")
                    return
            else:
                itemsPresent = False

    print("All Marketplace Publication Objects deleted!")
