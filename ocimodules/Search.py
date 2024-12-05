import oci


def SearchResources(config, signer, query):
    search = oci.resource_search.ResourceSearchClient(config, signer=signer)

    sdetails = oci.resource_search.models.StructuredSearchDetails()
    sdetails.query = query

    try:
        result = search.search_resources(search_details=sdetails, limit=1000, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY).data
    except oci.exceptions.ServiceError as response:
        print("Error searching resources: {} - {}".format(response.code, response.message))
        result = oci.resource_search.models.ResourceSummaryCollection()
        result.items = []

    return result.items
