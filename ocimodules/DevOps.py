import oci
import time

WaitRefresh = 15
MaxIDeleteIteration = 20


###########################################
# DeleteDevOpsProjects
###########################################
def DeleteDevOpsProjects(config, Compartments):
    AllItems = []
    object = oci.devops.DevopsClient(config)

    print("Getting all DevOps Project objects")
    for Compartment in Compartments:
        items = oci.pagination.list_call_get_all_results(object.list_projects, compartment_id=Compartment.id).data
        for item in items:
            if (item.lifecycle_state != "DELETED"):
                AllItems.append(item)
                print("- {} - {}".format(item.name, item.lifecycle_state))

    itemsPresent = True
    iteration = 0
    while itemsPresent:
        count = 0
        for item in AllItems:
            try:
                itemstatus = object.get_project(project_id=item.id).data
                if itemstatus.lifecycle_state != "DELETED":
                    if itemstatus.lifecycle_state != "DELETING":
                        try:
                            print("Deleting: {}".format(itemstatus.name))
                            object.delete_project(project_id=itemstatus.id)
                        except oci.exceptions.ServiceError as response:
                            print("error trying to delete: {} - {}".format(itemstatus.name, response.message))
                    else:
                        print("{} = {}".format(itemstatus.name, itemstatus.lifecycle_state))
                    count = count + 1
            except Exception:
                print("error deleting {}, probably already deleted".format(item.name))
        if count > 0:
            print("Waiting for all Objects to be deleted..." + (" Iteration " + str(iteration) + " of " + str(MaxIDeleteIteration) if iteration > 0 else ""))
            time.sleep(WaitRefresh)
            iteration += 1

            if iteration >= MaxIDeleteIteration:
                print("Some DevOps Projects not deleted, skipping!")
                return
        else:
            itemsPresent = False
    print("All DevOps Project Objects deleted!")


###########################################
# DeleteDeployArtifacts
###########################################
def DeleteDeployArtifacts(config, Compartments):
    AllItems = []
    object = oci.devops.DevopsClient(config)

    print("Getting all DeployArtifacts objects")
    for Compartment in Compartments:
        items = oci.pagination.list_call_get_all_results(object.list_deploy_artifacts, compartment_id=Compartment.id).data
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
                itemstatus = object.get_deploy_artifact(deploy_artifact_id=item.id).data
                if itemstatus.lifecycle_state != "DELETED":
                    if itemstatus.lifecycle_state != "DELETING":
                        try:
                            print("Deleting: {}".format(itemstatus.display_name))
                            object.delete_deploy_artifact(deploy_artifact_id=itemstatus.id)
                        except oci.exceptions.ServiceError as response:
                            print("error trying to delete: {} - {}".format(itemstatus.display_name, response.message))
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
                print("Some DeployArtifacts not deleted, skipping!")
                return
        else:
            itemsPresent = False
    print("All DeployArtifacts Objects deleted!")

###########################################
# DeleteDeployEnvironments
###########################################
def DeleteDeployEnvironments(config, Compartments):
    AllItems = []
    object = oci.devops.DevopsClient(config)

    print("Getting all DeployEnvironments objects")
    for Compartment in Compartments:
        items = oci.pagination.list_call_get_all_results(object.list_deploy_environments, compartment_id=Compartment.id).data
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
                itemstatus = object.get_deploy_environment(deploy_environment_id=item.id).data
                if itemstatus.lifecycle_state != "DELETED":
                    if itemstatus.lifecycle_state != "DELETING":
                        try:
                            print("Deleting: {}".format(itemstatus.display_name))
                            object.delete_deploy_environment(deploy_environment_id=itemstatus.id)
                        except oci.exceptions.ServiceError as response:
                            print("error trying to delete: {} - {}".format(itemstatus.display_name, response.message))
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
                print("Some DeployEnvironments not deleted, skipping!")
                return
        else:
            itemsPresent = False
    print("All DeployEnvironments Objects deleted!")

###########################################
# DeleteDeployPipelines
###########################################
def DeleteDeployPipelines(config, Compartments):
    AllItems = []
    object = oci.devops.DevopsClient(config)

    print("Getting all DeployPipelines objects")
    for Compartment in Compartments:
        items = oci.pagination.list_call_get_all_results(object.list_deploy_pipelines, compartment_id=Compartment.id).data
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
                itemstatus = object.get_deploy_pipeline(deploy_pipeline_id=item.id).data
                if itemstatus.lifecycle_state != "DELETED":
                    if itemstatus.lifecycle_state != "DELETING":
                        try:
                            print("Deleting: {}".format(itemstatus.display_name))
                            object.delete_deploy_pipeline(deploy_pipeline_id=itemstatus.id)
                        except oci.exceptions.ServiceError as response:
                            print("error trying to delete: {} - {}".format(itemstatus.display_name, response.message))
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
                print("Some DeployPipelines not deleted, skipping!")
                return
        else:
            itemsPresent = False
    print("All DeployPipelines Objects deleted!")

###########################################
# DeleteDeployStages
###########################################
def DeleteDeployStages(config, Compartments):
    AllItems = []
    object = oci.devops.DevopsClient(config)

    print("Getting all DeployStages objects")
    for Compartment in Compartments:
        items = oci.pagination.list_call_get_all_results(object.list_deploy_stages, compartment_id=Compartment.id).data
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
                itemstatus = object.get_deploy_stage(deploy_stage_id=item.id).data
                if itemstatus.lifecycle_state != "DELETED":
                    if itemstatus.lifecycle_state != "DELETING":
                        try:
                            print("Deleting: {}".format(itemstatus.display_name))
                            object.delete_deploy_stage(deploy_stage_id=itemstatus.id)
                        except oci.exceptions.ServiceError as response:
                            print("error trying to delete: {} - {}".format(itemstatus.display_name, response.message))
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
                print("Some DeployStages not deleted, skipping!")
                return
        else:
            itemsPresent = False
    print("All DeployStages Objects deleted!")
