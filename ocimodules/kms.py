import oci
import time
import datetime

WaitRefresh = 15


##############################################
# DeleteKMSvaults
##############################################
def DeleteKMSvaults(config, signer, Compartments, MovetoCompartmentID):
    try:
        AllItems = []
        object = oci.key_management.KmsVaultClient(config, signer=signer)
        vaultClient = oci.vault.VaultsClient(config, signer=signer)

        print("Getting all KMS Vault objects")
        for C in Compartments:
            Compartment = C.details
            print("Getting vault items for compartment {}".format(C.fullpath), end="\r")
            items = oci.pagination.list_call_get_all_results(object.list_vaults, compartment_id=Compartment.id).data
            for item in items:
                if (item.lifecycle_state != "DELETED"):
                    AllItems.append(item)

            print("Getting secret items for compartment {}".format(C.fullpath), end="\r")
            try:
                secrets = vaultClient.list_secrets(compartment_id=Compartment.id).data
            except oci.exceptions.ServiceError as response:
                print("Error moving secret {} - {}".format(response.code, response.message))
                secrets = []
            except Exception:
                print("error")
                secrets = []

            for secret in secrets:
                try:
                    secretchangedetails = oci.vault.models.ChangeSecretCompartmentDetails()
                    secretchangedetails.compartment_id = MovetoCompartmentID
                    print("Moving secret {} to main/trash compartment".format(secret.secret_name))
                except oci.exceptions.ServiceError as response:
                    print("Error getting secret info {} - {}".format(response.code, response.message))
                try:
                    vaultClient.change_secret_compartment(secret_id=secret.id, change_secret_compartment_details=secretchangedetails, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY)
                except oci.exceptions.ServiceError as response:
                    print("Error moving secret {} - {}".format(response.code, response.message))
                except Exception:
                    print("general error")

        for item in AllItems:
            try:
                itemstatus = object.get_vault(vault_id=item.id).data
                if itemstatus.lifecycle_state != "DELETED":
                    try:
                        kmsmanagement = oci.key_management.KmsManagementClient(config, itemstatus.management_endpoint)
                        keys = kmsmanagement.list_keys(compartment_id=item.compartment_id, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY).data
                        for key in keys:
                            keychangedetails = oci.key_management.models.ChangeKeyCompartmentDetails()
                            keychangedetails.compartment_id = MovetoCompartmentID
                            print("Moving key {} to main/trash compartment".format(key.display_name))
                            kmsmanagement.change_key_compartment(key_id=key.id, change_key_compartment_details=keychangedetails, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY).data

                        print("Moving Vault to main/trash compartment: {}".format(itemstatus.display_name))
                        changedetails = oci.key_management.models.ChangeVaultCompartmentDetails()
                        changedetails.compartment_id = MovetoCompartmentID
                        object.change_vault_compartment(vault_id=itemstatus.id, change_vault_compartment_details=changedetails, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY)

                        itemstatus = object.get_vault(vault_id=item.id).data
                        while itemstatus.lifecycle_state == "UPDATING":
                            print("waiting for vault move to be finished")
                            time.sleep(WaitRefresh)
                            itemstatus = object.get_vault(vault_id=item.id).data

                        print("KMS Vault {} moved to main/trash compartment".format(itemstatus.display_name))
                        deletedetails = oci.key_management.models.ScheduleVaultDeletionDetails()
                        deletedate = datetime.datetime.now() + datetime.timedelta(days=7) + datetime.timedelta(hours=1)
                        deletedate = deletedate.replace(minute=0, second=0, microsecond=0)
                        deletedetails.time_of_deletion = "{}.000Z".format(deletedate.isoformat())
                        itemstatus = object.schedule_vault_deletion(vault_id=item.id, schedule_vault_deletion_details=deletedetails)
                        print("KMS Vault scheduled to be deleted on {}".format(deletedate))

                    except Exception:
                        print("error trying to move: {}".format(itemstatus.display_name))
                else:
                    print("{} = {}".format(itemstatus.display_name, itemstatus.lifecycle_state))
            except Exception:
                print("error moving {}".format(item.display_name))

        print("All KMS Vault objects moved and scheduled for deletion!")

    # Catch Exception if Error
    except Exception as e:
        print(f'\nError in DeleteKMSvaults: {str(e)}')
