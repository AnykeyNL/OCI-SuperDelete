#!/usr/bin/env python3
##########################################################################################
# OCI-SuperDelete                                                                        #
#                                                                                        #
# Use with PYTHON3!                                                                      #
##########################################################################################
# Application Command line parameters
#
#   -cp profile    - profile inside the config file
#   -ip            - Use Instance Principals for Authentication
#   -dt            - Use Instance Principals with delegation token for cloud shell
#   -force         - force delete without confirmation
#   -rg            - Regions to delete comma separated
#   -c compartment - top level compartment to delete
#   -debug         - enable debug
#   -skip_delete_compartment - skip delete the compartment at end of the process
#
##########################################################################################
# If you contribute changes, please run flake8 before pushing to Git.
##########################################################################################
# To Do
# Database Tools - Private Endpoints
# Certificates Certificates - move to upper and schedule deletion
# Certificates CA Bundles
# Network Firewall Policies
# Console Dashboard Groups
##########################################################################################


import sys
import time
import oci
import platform
import logging

# import ocimodules
from ocimodules.functions import print_header, input_command_line, create_signer, check_oci_version
from ocimodules.IAM import Login, SubscribedRegions, GetHomeRegion, GetTenantName, DeleteTagNameSpaces, DeleteCompartments, DeleteTagDefaults
from ocimodules.VCN import DeleteVCN
from ocimodules.ObjectStorage import DeleteBuckets
from ocimodules.FunctionsService import DeleteApplications
from ocimodules.kms import DeleteKMSvaults
from ocimodules.Logging import DeleteLogGroups
from ocimodules.APM import DeleteAPM
from ocimodules.AnyDelete import DeleteAny
from ocimodules.BlockVolumeReplication import RemoveReplication
from ocimodules.DatabaseManagement import DisableDatabaseManagement

# Disable OCI CircuitBreaker feature
oci.circuit_breaker.NoCircuitBreakerStrategy()

#################################################
#           Manual Configuration                #
#################################################
# Specify your config file
configfile = "~/.oci/config"  # Linux
# configfile = "\\Users\\username\\.oci\\config"  # Windows

# Specify your config profile
configProfile = "DEFAULT"

# Specify the DEFAULT compartment OCID that you want to delete, Leave Empty for no default
DeleteCompartmentOCID = ""

# Search for resources in regions, this is an Array, so you can specify multiple regions:
# If no regions specified, it will be all subscribed regions.
# regions = ["eu-frankfurt-1", "eu-amsterdam-1"]
# regions = ["uk-london-1"]
regions = []

#################################################
#           Application Configuration           #
#################################################
min_version_required = "2.88.0"
application_version = "24.12.01"
debug = False


#############################################
# MyWriter to redirect output
#############################################
class MyWriter:

    filename = "log.txt"

    def __init__(self, stdout, filename):
        self.stdout = stdout
        self.filename = filename
        self.logfile = open(self.filename, "a", encoding="utf-8")

    def write(self, text):
        self.stdout.write(text)
        self.logfile.write(text)

    def close(self):
        self.stdout.close()
        self.logfile.close()

    def flush(self):
        self.logfile.close()
        self.logfile = open(self.filename, "a", encoding="utf-8")


def CurrentTimeString():
    return time.strftime("%D %H:%M:%S", time.localtime())


##########################################################################
# Main Program
##########################################################################
check_oci_version(min_version_required)

# Check command line
cmd = input_command_line()

# Redirect output to log.txt
logfile = cmd.log_file
writer = MyWriter(sys.stdout, logfile)
sys.stdout = writer

# configfile = cmd.config_file if cmd.config_file else configfile
configProfile = cmd.config_profile if cmd.config_profile else configProfile


debug = cmd.debug if cmd.debug else debug
force = cmd.force
regions = cmd.regions.split(",") if cmd.regions else regions
DeleteCompartmentOCID = cmd.compartment if cmd.compartment else DeleteCompartmentOCID
skip_delete_compartment = cmd.skip_delete_compartment

if DeleteCompartmentOCID == "":
    print("No compartment specified \n")
    input_command_line(help=True)
    sys.exit(2)

######################################################
# oci config and debug handle
######################################################
config, signer = create_signer(cmd.config_profile, cmd.is_instance_principals, cmd.is_delegation_token)
tenant_id = config['tenancy']

if debug:
    config['log_requests'] = True
    logging.basicConfig()
    logging.getLogger('oci').setLevel(logging.DEBUG)

######################################################
# Loading Compartments
# Add all active compartments,
# exclude the ManagementCompartmentForPaas (as this is locked compartment)
# Add root compartment to processRootCompartment if specified for root compartment objects
######################################################
print("\nLogin check and loading compartments...\n")
compartments = Login(config, signer, DeleteCompartmentOCID)
processCompartments = []
processRootCompartment = []
for compartment in compartments:
    if compartment.details.lifecycle_state == "ACTIVE" and compartment.details.name != "ManagedCompartmentForPaaS":
        processCompartments.append(compartment)
    if compartment.details.id == tenant_id:
        processRootCompartment.append(compartment)

# Check if regions specified if not getting all subscribed regions.
if len(regions) == 0:
    regions = SubscribedRegions(config, signer)

homeregion = GetHomeRegion(config, signer)
tenant_name = GetTenantName(config, signer)

######################################################
# Header Print and Confirmation
######################################################
print_header("OCI-SuperDelete", 0)

print("Date/Time          : " + CurrentTimeString())
print("Command Line       : " + ' '.join(x for x in sys.argv[1:]))
print("App Version        : " + application_version)
print("Machine            : " + platform.node() + " (" + platform.machine() + ")")
print("OCI SDK Version    : " + oci.version.__version__)
print("Python Version     : " + platform.python_version())
print("Config File        : " + configfile)
print("Config Profile     : " + configProfile)
print("Log File           : " + logfile)
print("")
print("Tenant Name        : " + tenant_name)
print("Tenant Id          : " + config['tenancy'])
print("Home Region        : " + homeregion)
print("Regions to Process : " + ','.join(x for x in regions))
print("\nCompartments to Process : \n")
for c in processCompartments:
    print("  " + c.fullpath)


#########################################
# Check confirmation for execution
#########################################
confirm = ""
if force:
    confirm = "yes"
else:
    confirm = input("\ntype yes to delete all contents from these compartments: ")

if confirm == "yes":

    ######################################################
    # Loop on Regions
    ######################################################
    for region in regions:

        print_header("Deleting resources in region " + region, 0)
        config["region"] = region

        print_header("Moving and Scheduling KMS Vaults for deletion at " + CurrentTimeString() + "@ " + region, 1)
        print("Moving to {}: ".format(DeleteCompartmentOCID))
        DeleteKMSvaults(config, signer, processCompartments, config['tenancy'])

        print_header("Deleting DevOps Projects at " + CurrentTimeString() + "@ " + region, 1)
        elements = ["deploy_stage", "deploy_artifact", "deploy_environment", "deploy_pipeline", "build_pipeline"]
        for element in elements:
            DeleteAny(config, signer, processCompartments, "devops.DevopsClient", element)
        DeleteAny(config, signer, processCompartments, "devops.DevopsClient", "repository", ObjectNameVar="name")
        DeleteAny(config, signer, processCompartments, "devops.DevopsClient", "project", ObjectNameVar="name")

        print_header("Deleting Oracle Cloud VMware solution at " + CurrentTimeString() + "@ " + region, 1)
        DeleteAny(config, signer, processCompartments, "ocvp.SddcClient", "sddc")

        print_header("Deleting Database Migrations at " + CurrentTimeString() + "@ " + region, 1)
        elements = ["migration", "connection"]
        for element in elements:
            DeleteAny(config, signer, processCompartments, "database_migration.DatabaseMigrationClient", element)

        print_header("Deleting Migrations at " + CurrentTimeString() + "@ " + region, 1)
        DeleteAny(config, signer, processCompartments, "cloud_migrations.MigrationClient", "migration_plan")
        DeleteAny(config, signer, processCompartments, "cloud_migrations.MigrationClient", "migration")
        DeleteAny(config, signer, processCompartments, "cloud_migrations.MigrationClient", "replication_schedule")
        DeleteAny(config, signer, processCompartments, "cloud_bridge.OcbAgentSvcClient", "environment")
        DeleteAny(config, signer, processCompartments, "cloud_bridge.OcbAgentSvcClient", "agent_dependency")
        DeleteAny(config, signer, processCompartments, "cloud_bridge.DiscoveryClient", "asset_source")
        DeleteAny(config, signer, processCompartments, "cloud_bridge.DiscoveryClient", "discovery_schedule")
        DeleteAny(config, signer, processCompartments, "cloud_bridge.InventoryClient", "asset")
        DeleteAny(config, signer, processCompartments, "cloud_bridge.InventoryClient", "inventory")

        print_header("Deleting GoldenGate at " + CurrentTimeString() + "@ " + region, 1)
        elements = ["database_registration", "deployment", "deployment_backup"]
        for element in elements:
            DeleteAny(config, signer, processCompartments, "golden_gate.GoldenGateClient", element)

        print_header("Deleting Vulnerability Scanning Services at " + CurrentTimeString() + "@ " + region, 1)
        elements = ["host_agent_scan_result", "host_port_scan_result", "host_cis_benchmark_scan_result", "container_scan_result"]
        for element in elements:
            DeleteAny(config, signer, processCompartments, "vulnerability_scanning.VulnerabilityScanningClient", element, DelState="", DelingSate="")
        DeleteAny(config, signer, processCompartments, "vulnerability_scanning.VulnerabilityScanningClient", "host_scan_target")
        DeleteAny(config, signer, processCompartments, "vulnerability_scanning.VulnerabilityScanningClient", "container_scan_target")
        elements = ["host_scan_recipe", "container_scan_recipe"]
        for element in elements:
            DeleteAny(config, signer, processCompartments, "vulnerability_scanning.VulnerabilityScanningClient", element, DelState="", DelingSate="")

        print_header("Deleting Bastion Services at " + CurrentTimeString() + "@ " + region, 1)
        DeleteAny(config, signer, processCompartments, "bastion.BastionClient", "bastion", ObjectNameVar="name")

        print_header("Deleting Web Application Firewall at " + CurrentTimeString() + "@ " + region, 1)
        DeleteAny(config, signer, processCompartments, "waf.WafClient", "web_app_firewall")
        DeleteAny(config, signer, processCompartments, "waf.WafClient", "web_app_firewall_policy")

        if region == homeregion:
            print_header("Deleting Edge Services at " + CurrentTimeString() + "@ " + region, 1)
            DeleteAny(config, signer, processCompartments, "waas.WaasClient", "waas_policy")
            DeleteAny(config, signer, processCompartments, "healthchecks.HealthChecksClient", "http_monitor", ServiceID="monitor_id", DelState="", DelingSate="")
            DeleteAny(config, signer, processCompartments, "healthchecks.HealthChecksClient", "ping_monitor", ServiceID="monitor_id", DelState="", DelingSate="")
            DeleteAny(config, signer, processCompartments, "dns.DnsClient", "steering_policy_attachment")
            DeleteAny(config, signer, processCompartments, "dns.DnsClient", "steering_policy")
            DeleteAny(config, signer, processCompartments, "dns.DnsClient", "zone", ObjectNameVar="name", ServiceID="zone_name_or_id", Extra=", scope=\"PRIVATE\"", Filter="protected")
            DeleteAny(config, signer, processCompartments, "dns.DnsClient", "view", Extra=", scope=\"PRIVATE\"", Filter="protected")

        print_header("Deleting Object Storage at " + CurrentTimeString() + "@ " + region, 1)
        DeleteBuckets(config, signer, processCompartments)

        print_header("Deleting Cloud Guard Servcies at " + CurrentTimeString() + "@ " + region, 1)
        DeleteAny(config, signer, processCompartments, "cloud_guard.CloudGuardClient", "target")
        DeleteAny(config, signer, processCompartments, "cloud_guard.CloudGuardClient", "detector_recipe")
        DeleteAny(config, signer, processCompartments, "cloud_guard.CloudGuardClient", "responder_recipe")
        DeleteAny(config, signer, processCompartments, "cloud_guard.CloudGuardClient", "managed_list")

        print_header("Deleting Email Service at " + CurrentTimeString() + "@ " + region, 1)
        DeleteAny(config, signer, processCompartments, "email.EmailClient", "sender", ObjectNameVar="email_address")
        if processRootCompartment:
            DeleteAny(config, signer, processRootCompartment, "email.EmailClient", "suppression", ObjectNameVar="email_address", DelState="", DelingSate="")
        DeleteAny(config, signer, processCompartments, "email.EmailClient", "email_domain", ObjectNameVar="name")

        print_header("Deleting OKE Clusters at " + CurrentTimeString() + "@ " + region, 1)
        DeleteAny(config, signer, processCompartments, "container_engine.ContainerEngineClient", "cluster", ObjectNameVar="name")

        print_header("Deleting Repositories at " + CurrentTimeString() + "@ " + region, 1)
        DeleteAny(config, signer, processCompartments, "artifacts.ArtifactsClient", "container_repository", ServiceID="repository_id")
        DeleteAny(config, signer, processCompartments, "artifacts.ArtifactsClient", "repository")

        print_header("Deleting Auto Scaling Configurations at " + CurrentTimeString() + "@ " + region, 1)
        DeleteAny(config, signer, processCompartments, "autoscaling.AutoScalingClient", "auto_scaling_configuration", DelState="", DelingSate="")

        # DISABLED as service is EOF (https://docs.oracle.com/en-us/iaas/os-management/home.htm)
        # print_header("Deleting OS Management services at " + CurrentTimeString() + "@ " + region, 1)
        # DeleteAny(config, signer, processCompartments, "os_management.OsManagementClient", "managed_instance_group")
        # DeleteAny(config, signer, processCompartments, "os_management.OsManagementClient", "scheduled_job")
        # DeleteAny(config, signer, processCompartments, "os_management.OsManagementClient", "software_source")

        print_header("Deleting Compute Instances at " + CurrentTimeString() + "@ " + region, 1)
        DeleteAny(config, signer, processCompartments, "core.ComputeManagementClient", "instance_pool", DeleteCommand="terminate_instance_pool", DelState="TERMINATED", DelingSate="TERMINATING")
        DeleteAny(config, signer, processCompartments, "core.ComputeManagementClient", "instance_configuration", DelState="", DelingSate="")
        DeleteAny(config, signer, processCompartments, "core.ComputeClient", "instance", DeleteCommand="terminate_instance", DelState="TERMINATED", DelingSate="TERMINATING")
        DeleteAny(config, signer, processCompartments, "core.ComputeClient", "image")
        DeleteAny(config, signer, processCompartments, "core.ComputeClient", "dedicated_vm_host")

        print_header("Deleting Management Agents at " + CurrentTimeString() + "@ " + region, 1)
        DeleteAny(config, signer, processCompartments, "management_agent.ManagementAgentClient", "management_agent")
        DeleteAny(config, signer, processCompartments, "management_agent.ManagementAgentClient", "management_agent_install_key")

        print_header("Deleting Visual Builder Components at " + CurrentTimeString() + "@ " + region, 1)
        DeleteAny(config, signer, processCompartments, "visual_builder.VbInstanceClient", "vb_instance")

        print_header("Deleting DataScience Components at " + CurrentTimeString() + "@ " + region, 1)
        DeleteAny(config, signer, processCompartments, "data_science.DataScienceClient", "notebook_session")
        DeleteAny(config, signer, processCompartments, "data_science.DataScienceClient", "model_deployment")
        DeleteAny(config, signer, processCompartments, "data_science.DataScienceClient", "model")
        DeleteAny(config, signer, processCompartments, "data_science.DataScienceClient", "project")

        print_header("Deleting Application Functions at " + CurrentTimeString() + "@ " + region, 1)
        DeleteApplications(config, signer, processCompartments)

        print_header("Deleting API Gateway Service at " + CurrentTimeString() + "@ " + region, 1)
        DeleteAny(config, signer, processCompartments, "apigateway.DeploymentClient", "deployment")
        DeleteAny(config, signer, processCompartments, "apigateway.GatewayClient", "gateway")
        DeleteAny(config, signer, processCompartments, "apigateway.ApiGatewayClient", "api")
        DeleteAny(config, signer, processCompartments, "apigateway.ApiGatewayClient", "certificate")

        print_header("Deleting Datasafe services at " + CurrentTimeString() + "@ " + region, 1)
        DeleteAny(config, signer, processCompartments, "data_safe.DataSafeClient", "user_assessment", DelState="Succeeded")
        DeleteAny(config, signer, processCompartments, "data_safe.DataSafeClient", "security_assessment")
        DeleteAny(config, signer, processCompartments, "data_safe.DataSafeClient", "target_database")
        DeleteAny(config, signer, processCompartments, "data_safe.DataSafeClient", "on_prem_connector")
        DeleteAny(config, signer, processCompartments, "data_safe.DataSafeClient", "data_safe_private_endpoint")

        print_header("Deleting Database Management services at " + CurrentTimeString() + "@ " + region, 1)
        DisableDatabaseManagement(config, signer, processCompartments)
        DeleteAny(config, signer, processCompartments, "database_management.DbManagementClient", "db_management_private_endpoint", ObjectNameVar="name")
        DeleteAny(config, signer, processCompartments, "database_management.DbManagementClient", "managed_database_group", ObjectNameVar="name", DelState="", DelingSate="")

        print_header("Deleting Log Analytics services at " + CurrentTimeString() + "@ " + region, 1)
        DeleteAny(config, signer, processCompartments, "log_analytics.LogAnalyticsClient", "log_analytics_entity", ObjectNameVar="name", Extra=", namespace_name=\"{}\"".format(tenant_name))
        DeleteAny(config, signer, processCompartments, "log_analytics.LogAnalyticsClient", "log_analytics_log_group", Extra=", namespace_name=\"{}\"".format(tenant_name), DelState="", DelingSate="")
        DeleteAny(config, signer, processCompartments, "log_analytics.LogAnalyticsClient", "log_analytics_em_bridge", Extra=", namespace_name=\"{}\"".format(tenant_name))

        print_header("Deleting Data Catalog services at " + CurrentTimeString() + "@ " + region, 1)
        DeleteAny(config, signer, processCompartments, "data_catalog.DataCatalogClient", "catalog")
        DeleteAny(config, signer, processCompartments, "data_catalog.DataCatalogClient", "catalog_private_endpoint")
        DeleteAny(config, signer, processCompartments, "data_catalog.DataCatalogClient", "metastore")

        print_header("Deleting Data Integratation services at " + CurrentTimeString() + "@ " + region, 1)
        DeleteAny(config, signer, processCompartments, "data_integration.DataIntegrationClient", "workspace")

        print_header("Deleting Oracle Databases at " + CurrentTimeString() + "@ " + region, 1)
        DeleteAny(config, signer, processCompartments, "database.DatabaseClient", "db_system", DeleteCommand="terminate_db_system", DelState="TERMINATED", DelingSate="TERMINATING")
        DeleteAny(config, signer, processCompartments, "database.DatabaseClient", "backup")
        DeleteAny(config, signer, processCompartments, "database.DatabaseClient", "autonomous_database", DelState="TERMINATED", DelingSate="TERMINATING")

        print_header("Deleting MySQL Database Instances at " + CurrentTimeString() + "@ " + region, 1)
        DeleteAny(config, signer, processCompartments, "mysql.DbSystemClient", "db_system")


        print_header("Deleting PostgreSQL Database Instances at " + CurrentTimeString() + "@ " + region, 1)
        DeleteAny(config, signer, processCompartments, "psql.PostgresqlClient", "db_system")
        print_header("Deleting PostgreSQL Database Backups at " + CurrentTimeString() + "@ " + region, 1)
        DeleteAny(config, signer, processCompartments, "psql.PostgresqlClient", "backup")


        print_header("Deleting Nosql tables at " + CurrentTimeString() + "@ " + region, 1)
        DeleteAny(config, signer, processCompartments, "nosql.NosqlClient", "table", ServiceID="table_name_or_id")

        print_header("Deleting Digital Assistants at " + CurrentTimeString() + "@ " + region, 1)
        DeleteAny(config, signer, processCompartments, "oda.OdaClient", "oda_instance")

        print_header("Deleting Analytics at " + CurrentTimeString() + "@ " + region, 1)
        DeleteAny(config, signer, processCompartments, "analytics.AnalyticsClient", "analytics_instance", ObjectNameVar="name")
        DeleteAny(config, signer, processCompartments, "streaming.StreamAdminClient", "stream", ObjectNameVar="name")
        DeleteAny(config, signer, processCompartments, "streaming.StreamAdminClient", "stream_pool", ObjectNameVar="name")
        DeleteAny(config, signer, processCompartments, "streaming.StreamAdminClient", "connect_harness", ObjectNameVar="name")
        DeleteAny(config, signer, processCompartments, "sch.ServiceConnectorClient", "service_connector")

        print_header("Deleting Integration at " + CurrentTimeString() + "@ " + region, 1)
        DeleteAny(config, signer, processCompartments, "integration.IntegrationInstanceClient", "integration_instance")

        print_header("Deleting Blockchain at " + CurrentTimeString() + "@ " + region, 1)
        DeleteAny(config, signer, processCompartments, "blockchain.BlockchainPlatformClient", "blockchain_platform")

        print_header("Deleting Resource Manager Stacks at " + CurrentTimeString() + "@ " + region, 1)
        DeleteAny(config, signer, processCompartments, "resource_manager.ResourceManagerClient", "stack")
        DeleteAny(config, signer, processCompartments, "resource_manager.ResourceManagerClient", "configuration_source_provider")

        print_header("Deleting Anomaly Detection Services at " + CurrentTimeString() + "@ " + region, 1)
        DeleteAny(config, signer, processCompartments, "ai_anomaly_detection.AnomalyDetectionClient", "data_asset")
        DeleteAny(config, signer, processCompartments, "ai_anomaly_detection.AnomalyDetectionClient", "model")
        DeleteAny(config, signer, processCompartments, "ai_anomaly_detection.AnomalyDetectionClient", "project")

        print_header("Deleting Data Flow Services at " + CurrentTimeString() + "@ " + region, 1)
        DeleteAny(config, signer, processCompartments, "data_flow.DataFlowClient", "private_endpoint")
        DeleteAny(config, signer, processCompartments, "data_flow.DataFlowClient", "application")
        DeleteAny(config, signer, processCompartments, "data_flow.DataFlowClient", "run", DelState="SUCCEEDED")

        print_header("Deleting Block Volumes at " + CurrentTimeString() + "@ " + region, 1)
        RemoveReplication(config, signer, processCompartments)
        DeleteAny(config, signer, processCompartments, "core.BlockstorageClient", "volume_group", DelState="TERMINATED", DelingSate="TERMINATING")
        DeleteAny(config, signer, processCompartments, "core.BlockstorageClient", "volume_group_backup", DelState="TERMINATED", DelingSate="TERMINATING")
        DeleteAny(config, signer, processCompartments, "core.BlockstorageClient", "volume", DelState="TERMINATED", DelingSate="TERMINATING", PerAD=True)
        DeleteAny(config, signer, processCompartments, "core.BlockstorageClient", "volume_backup", DelState="TERMINATED", DelingSate="TERMINATING")
        DeleteAny(config, signer, processCompartments, "core.BlockstorageClient", "boot_volume", DelState="TERMINATED", DelingSate="TERMINATING", PerAD=True)
        DeleteAny(config, signer, processCompartments, "core.BlockstorageClient", "boot_volume_backup", DelState="TERMINATED", DelingSate="TERMINATING")
        DeleteAny(config, signer, processCompartments, "core.BlockstorageClient", "volume_backup_policy", DelState="", ServiceID="policy_id")

        print_header("Deleting FileSystem and Mount Targets at " + CurrentTimeString() + "@ " + region, 1)
        DeleteAny(config, signer, processCompartments, "file_storage.FileStorageClient", "mount_target", PerAD=True)
        DeleteAny(config, signer, processCompartments, "file_storage.FileStorageClient", "file_system", PerAD=True)

        print_header("Deleting VCNs at " + CurrentTimeString() + "@ " + region, 1)
        DeleteVCN(config, signer, processCompartments)
        DeleteAny(config, signer, processCompartments, "core.VirtualNetworkClient", "local_peering_gateway", DelState="TERMINATED", DelingSate="TERMINATING")
        DeleteAny(config, signer, processCompartments, "core.VirtualNetworkClient", "remote_peering_connection", DelState="TERMINATED", DelingSate="TERMINATING")
        DeleteAny(config, signer, processCompartments, "core.VirtualNetworkClient", "drg", DelState="TERMINATED", DelingSate="TERMINATING")

        print_header("Deleting Alarms at " + CurrentTimeString() + "@ " + region, 1)
        DeleteAny(config, signer, processCompartments, "monitoring.MonitoringClient", "alarm")

        print_header("Deleting Notifications at " + CurrentTimeString() + "@ " + region, 1)
        DeleteAny(config, signer, processCompartments, "ons.NotificationControlPlaneClient", "topic", ObjectNameVar="name", ServiceID="topic_id", ReturnServiceID="topic_id")

        print_header("Deleting Events at " + CurrentTimeString() + "@ " + region, 1)
        DeleteAny(config, signer, processCompartments, "events.EventsClient", "rule")

        print_header("Deleting OpenSearch Backups at " + CurrentTimeString() + "@ " + region, 1)
        DeleteAny(config, signer, processCompartments, "opensearch.OpensearchClusterBackupClient", "opensearch_cluster_backup")  
             
        print_header("Deleting OpenSearch Cluster at " + CurrentTimeString() + "@ " + region, 1)
        DeleteAny(config, signer, processCompartments, "opensearch.OpensearchClusterClient", "opensearch_cluster")

        print_header("Deleting OCI Cache(Redis)  at " + CurrentTimeString() + "@ " + region, 1)
        DeleteAny(config, signer, processCompartments, "redis.RedisClusterClient", "redis_cluster")

        #TO DO : Delete Gen AI Endpoints and Custom Models
        print_header("Deleting Generative AI Dedicated Cluster at " + CurrentTimeString() + "@ " + region, 1)
        DeleteAny(config, signer, processCompartments, "generative_ai.GenerativeAiClient", "dedicated_ai_cluster")

        print_header("Deleting AI Language Endpoints at " + CurrentTimeString() + "@ " + region, 1)
        DeleteAny(config, signer, processCompartments, "ai_language.AIServiceLanguageClient", "endpoint")

        print_header("Deleting AI Language Models at " + CurrentTimeString() + "@ " + region, 1)
        DeleteAny(config, signer, processCompartments, "ai_language.AIServiceLanguageClient", "model")

        print_header("Deleting AI Language Projects at " + CurrentTimeString() + "@ " + region, 1)
        DeleteAny(config, signer, processCompartments, "ai_language.AIServiceLanguageClient", "project")

        if region == homeregion:
            print_header("Deleting Policies at " + CurrentTimeString() + "@ " + region, 1)
            DeleteAny(config, signer, processCompartments, "identity.IdentityClient", "policy", ObjectNameVar="name")
            DeleteAny(config, signer, processCompartments, "identity.IdentityClient", "dynamic_group", ObjectNameVar="name")

        print_header("Deleting Log Groups at " + CurrentTimeString() + "@ " + region, 1)
        DeleteLogGroups(config, signer, processCompartments)

        print_header("Deleting Application Performance Monitoring at " + CurrentTimeString() + "@ " + region, 1)
        DeleteAPM(config, signer, processCompartments)

        # delete tags and namespace only if home region
        if region == homeregion:
            print_header("Deleting Tag Namespaces at " + CurrentTimeString() + "@ " + region, 1)
            DeleteTagDefaults(config, signer, processCompartments)
            DeleteTagNameSpaces(config, signer, processCompartments)

    if not skip_delete_compartment:
        print_header("Deleting Compartments at " + CurrentTimeString() + "@ " + region, 1)
        config["region"] = homeregion
        DeleteCompartments(config, signer, processCompartments, DeleteCompartmentOCID)
    else:
        print("Skipping deletion of the compartments as specified at " + CurrentTimeString() + "@ " + region, 1)

else:
    print("ok, doing nothing")
