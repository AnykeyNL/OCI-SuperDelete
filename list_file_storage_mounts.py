#!/usr/bin/env python3

import json
import oci

def get_file_mounts(comp, ads, identity_client, file_storage_client, error_comparments):
    file_mounts = list()

    for ad in ads:
        try:
            mount_tagets = file_storage_client.list_mount_targets(compartment_id=comp.id,
                availability_domain=ad.name)
            if len(mount_tagets.data) > 0:
                print(f"{ comp.name } - { ad.name } - { mount_tagets.data }")
                file_mounts += mount_tagets.data
        except Exception as e:
            error_comparments.append((comp.id, comp.name, f'{ad.name} access - {e}'))
            print(f"{ comp.name } - { ad.name } - Could not access")
    
    try:
        sub_comps = identity_client.list_compartments(compartment_id=comp.id,
                    lifecycle_state="ACTIVE").data
        
        if len(sub_comps) > 0:
            print(f"{ comp.name } sub_comps - {sub_comps}")
            for sub_comp in sub_comps:
                file_mounts += get_file_mounts(sub_comp, ads, identity_client, file_storage_client, error_comparments)
    except Exception as e:
        print(sub_comps)
        error_comparments.append((comp.id, comp.name, f'sub compartment access - {e}'))
        print(f"{ comp.name } sub_comps - Could not Access")
    
    return file_mounts

config = oci.config.from_file()
identity_client = oci.identity.IdentityClient(config)
file_storage_client = oci.file_storage.FileStorageClient(config)
limits_client = oci.limits.LimitsClient(config)

tenancy_id = "ocid1.tenancy.oc1.."
compartment_id = "ocid1.compartment.oc1.."

availability_domains = identity_client.list_availability_domains(compartment_id=tenancy_id).data

ads = {}
for ad in availability_domains:
    limits = limits_client.get_resource_availability(service_name='filesystem', limit_name='mount-target-count', 
        compartment_id=tenancy_id,
        availability_domain=ad.name)
    ads[ad.name] = {"used": limits.data.used, "available": limits.data.available, "used_mounts" : [] }

compartments = identity_client.list_compartments(compartment_id=compartment_id,
                            lifecycle_state="ACTIVE")

file_mounts = list()
error_comparments = list()
for comp in compartments.data:
    try:
        for ad in availability_domains:
            mount_targets = file_storage_client.list_mount_targets(compartment_id=comp.id,
                availability_domain=ad.name)
            if len(mount_targets.data) > 0:
                print(f"{ comp.id } / { comp.name } - { ad.name } - { mount_targets.data }")
    except Exception as e:
        error_comparments.append((comp.id, comp.name, f'compartment access - {e}'))
        print(f"{ comp.id } / { comp.name } - Could not access")

    file_mounts += get_file_mounts(comp, availability_domains, identity_client, file_storage_client, error_comparments)

print("file_mounts")
print(file_mounts)

for mount in file_mounts:
    ads[mount.availability_domain]['used_mounts'].append(mount)

print("ads")
print(ads)

print("ads_summary")
for ad, ad_dict in ads.items():
    print(f"ad = {ad}, available = {ad_dict['available']}, limits_used = {ad_dict['used']}, reported_used = {len(ad_dict['used_mounts'])}")
    for mount in ad_dict['used_mounts']:
        print(f"id = {mount.id}, comp_id = {mount.compartment_id}, name = {mount.display_name}")

print("errors_summary")
print(error_comparments)