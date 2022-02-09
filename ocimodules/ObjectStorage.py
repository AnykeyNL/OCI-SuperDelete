import oci

MaxErrorIteration = 20


###########################################
# DeleteBuckets
###########################################
def DeleteBuckets(config, signer, Compartments):
    AllBuckets = []
    object = oci.object_storage.ObjectStorageClient(config, signer=signer)

    ns = object.get_namespace().data

    print("Getting all buckets for: {}".format(ns))

    for C in Compartments:
        Compartment = C.details
        items = object.list_buckets(namespace_name=ns, compartment_id=Compartment.id).data
        if len(items) > 0:
            AllBuckets.append(items)

    for buckets in AllBuckets:
        for bucket in buckets:
            DeleteRetentionRules(config, signer, bucket)
            AbortMultipartupload(config, signer, bucket)
            DeleteReplication(config, signer, bucket)
            DeletePreauthenticated(config, signer, bucket)
            DeleteObjects(config, signer, bucket)
            DeleteObjectVersions(config, signer, bucket)

    for buckets in AllBuckets:
        for bucket in buckets:
            print("Delete bucket: {}".format(bucket.name))
            try:
                object.delete_bucket(namespace_name=bucket.namespace, bucket_name=bucket.name)
            except Exception as er:
                print("error deleting bucket : {}".format(bucket.name) + " - " + str(er))

    print("All buckets deleted!")

###########################################
# Delete Retention Rules
###########################################
def DeleteRetentionRules(config, signer, bucket):
    object = oci.object_storage.ObjectStorageClient(config, signer=signer)
    print("Deleting retention rules in bucket: {}".format(bucket.name))
    more = True

    iteration = 0
    while more:
        result = oci.pagination.list_call_get_all_results(object.list_retention_rules, namespace_name=bucket.namespace, bucket_name=bucket.name)

        items = result.data
        if len(items) == 0:
            more = False
        else:
            for item in items:
                print("Deleting {}:{}".format(bucket.name, item.display_name))
                try:
                    object.delete_retention_rule(namespace_name=bucket.namespace, bucket_name=bucket.name, retention_rule_id=item.id)
                except Exception as e:
                    print("error deleting retention rule : {} - {}".format(item.display_name, str(e)))
                    iteration += 1
                    if iteration >= MaxErrorIteration:
                        print("Some retention rules not deleted, skipping!")
                        return
    print("All retention rules deleted!")


###########################################
# DeleteObjects
###########################################
def DeleteObjects(config, signer, bucket):
    objectlimit = 20
    object = oci.object_storage.ObjectStorageClient(config, signer=signer)
    print("Deleting objects in bucket: {}".format(bucket.name))
    more = True

    iteration = 0
    while more:
        result = object.list_objects(namespace_name=bucket.namespace, bucket_name=bucket.name, limit=objectlimit)
        items = result.data.objects
        if len(items) == 0:
            more = False
        else:
            for item in items:
                print("Deleting {}:{}".format(bucket.name, item.name))
                try:
                    object.delete_object(namespace_name=bucket.namespace, bucket_name=bucket.name, object_name=item.name)
                except Exception as e:
                    print("error deleting object : {} - {}".format(item.name, str(e)))
                    iteration += 1
                    if iteration >= MaxErrorIteration:
                        print("Some Objects not deleted, skipping!")
                        return
    print("All Objects deleted!")


###########################################
# DeleteObjectVersions
###########################################
def DeleteObjectVersions(config, signer, bucket):
    objectlimit = 20
    object = oci.object_storage.ObjectStorageClient(config, signer=signer)
    print("Deleting objects in bucket: {}".format(bucket.name))
    more = True

    iteration = 0
    while more:
        result = object.list_object_versions(namespace_name=bucket.namespace, bucket_name=bucket.name, limit=objectlimit)
        items = result.data.items
        if len(items) == 0:
            more = False
        else:
            for item in items:
                print("Deleting {}:{}:{}".format(bucket.name, item.name, item.version_id))
                try:
                    object.delete_object(namespace_name=bucket.namespace, bucket_name=bucket.name, object_name=item.name, version_id=item.version_id)
                except Exception as e:
                    print("error deleting object : {} - {}".format(item.name, str(e)))
                    iteration += 1
                    if iteration >= MaxErrorIteration:
                        print("Some Objects not deleted, skipping!")
                        return
    print("All Objects Version deleted!")


###########################################
# DeleteReplication
###########################################
def DeleteReplication(config, signer, bucket):
    objectlimit = 20
    object = oci.object_storage.ObjectStorageClient(config, signer=signer)
    print("Deleting replications in bucket: {}".format(bucket.name))
    more = True

    while more:
        result = object.list_replication_policies(namespace_name=bucket.namespace, bucket_name=bucket.name, limit=objectlimit)
        items = result.data
        for item in items:
            print("Deleting {}:{}".format(bucket.name, item.name))
            object.delete_replication_policy(namespace_name=bucket.namespace, bucket_name=bucket.name, replication_id=item.id)

        if len(items) == objectlimit:
            more = True
        else:
            more = False
    print("All replications deleted!")


###########################################
# DeletePreauthenticated
###########################################
def DeletePreauthenticated(config, signer, bucket):
    objectlimit = 20
    object = oci.object_storage.ObjectStorageClient(config, signer=signer)
    print("Aborts an in-progress multipart upload and deletes all parts that have been uploaded in bucket: {}".format(bucket.name))
    more = True

    while more:
        result = object.list_preauthenticated_requests(namespace_name=bucket.namespace, bucket_name=bucket.name, limit=objectlimit)
        items = result.data
        for item in items:
            print("Deleting {}:{}".format(bucket.name, item.name))
            object.delete_preauthenticated_request(namespace_name=bucket.namespace, bucket_name=bucket.name, par_id=item.id)

        if len(items) == objectlimit:
            more = True
        else:
            more = False
    print("All Preauthenticated deleted!")


###########################################
# AbortMultipartupload
###########################################
def AbortMultipartupload(config, signer, bucket):
    objectlimit = 20
    object = oci.object_storage.ObjectStorageClient(config, signer=signer)
    print("Deleting Preauthenticated in bucket: {}".format(bucket.name))
    more = True

    while more:
        result = object.list_multipart_uploads(namespace_name=bucket.namespace, bucket_name=bucket.name, limit=objectlimit)
        items = result.data
        for item in items:
            print("Deleting {}:{}".format(bucket.name, item.object))
            object.abort_multipart_upload(namespace_name=bucket.namespace, bucket_name=bucket.name, object_name=item.object, upload_id=item.upload_id)

        if len(items) == objectlimit:
            more = True
        else:
            more = False
    print("All multipartupload deleted!")
