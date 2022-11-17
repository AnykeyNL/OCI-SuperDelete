import oci
import time

WaitRefresh = 15
MaxIDeleteIteration = 20

def DisableDatabaseManagement(config, signer, Compartments):
    db = oci.database.DatabaseClient(config, signer=signer)
    dbm = oci.database_management.DbManagementClient(config, signer=signer)

    for C in Compartments:
        Compartment = C.details
        print("Finding Databases that are managed in {}                   ".format(Compartment.name), end="\r")
        items = dbm.list_managed_databases(compartment_id=Compartment.id).data.items
        if len(items) > 0:
            for i in items:
                if i.deployment_type == "AUTONOMOUS":
                    print("Disabling autonomous database management for: {}                  ".format(i.name))
                    try:
                        result = db.disable_autonomous_database_management(autonomous_database_id=i.id)
                    except oci.exceptions.ServiceError as response:
                            print("error {}-{} trying to disable: {}".format(response.code, response.message,"autonomous database management"))
                if i.deployment_type == "VM" or i.deployment_type == "BM" or i.deployment_type == "EXADATA":
                    print("Disabling database management for: {}                  ".format(i.name))
                    try:
                        result = db.disable_database_management(database_id=i.id)
                    except oci.exceptions.ServiceError as response:
                            print("error {}-{} trying to disable: {}".format(response.code, response.message,"database management"))

            wait = True
            while wait:
                print("Waiting for managements services to be disabled                   ".format(Compartment.name), end="\r")
                items = dbm.list_managed_databases(compartment_id=Compartment.id).data.items
                if len(items) == 0:
                    wait = False
                time.sleep(2)






