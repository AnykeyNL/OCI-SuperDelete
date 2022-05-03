#!/usr/bin/env python3

import json
import oci

def get_file_mounts(comp, ads, identity_client, file_storage_client):
    file_mounts = list()

    for ad in ads:
        try:
            mount_tagets = file_storage_client.list_mount_targets(compartment_id=comp.id,
                availability_domain=ad.name)
            print(f"{ comp.name } - { ad.name } - { mount_tagets.data }")
            if len(mount_tagets.data) > 0:
                file_mounts += mount_tagets.data
        except Exception as e:
            print(f"{ comp.name } - { ad.name } - Could not access")
    
    try:
        sub_comps = identity_client.list_compartments(compartment_id=comp.id,
                    lifecycle_state="ACTIVE").data
        print(f"{ comp.name } sub_comps - {sub_comps}")
        
        if len(sub_comps) > 0:
            for sub_comp in sub_comps:
                file_mounts += get_file_mounts(sub_comp, ads, identity_client, file_storage_client)
    except Exception as e:
        print(f"{ comp.name } sub_comps - Could not Access")
    
    return file_mounts

config = oci.config.from_file()
identity_client = oci.identity.IdentityClient(config)
file_storage_client = oci.file_storage.FileStorageClient(config)
limits_client = oci.limits.LimitsClient(config)

tenancy_id = "ocid1.tenancy.oc1.."

availability_domains = identity_client.list_availability_domains(compartment_id=tenancy_id).data
print(availability_domains)

for ad in availability_domains:
    limits = limits_client.get_resource_availability(service_name='filesystem', limit_name='mount-target-count', 
        compartment_id=tenancy_id,
        availability_domain=ad.name)
    print(f"root - { ad.name } - available = { limits.data.available }")
