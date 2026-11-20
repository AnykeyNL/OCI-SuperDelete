# import only system from os
import argparse
import oci
import os
import shutil
import subprocess
import sys
from datetime import datetime

# Default profile name used by --interactive (browser based session login)
DefaultSessionProfile = "SESSION"


##########################################################################
# define our clear function
##########################################################################
def clear():

    # for windows
    if os.name == 'nt':
        _ = os.system('cls')

    # for mac and linux(here, os.name is 'posix')
    else:
        _ = os.system('clear')


##########################################################################
# Print header centered
##########################################################################
def print_header(name, category):
    options = {0: 95, 1: 85, 2: 60}
    chars = int(options[category])
    print("")
    print('#' * chars)
    print("#" + name.center(chars - 2, " ") + "#")
    print('#' * chars)


##########################################################################
# input_command_line
##########################################################################
def input_command_line(help=False):
    parser = argparse.ArgumentParser(formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=80, width=130))
    parser.add_argument('-x', action='store_true', default=False, dest='interactive_mode', help='Enable interactive mode to confirm each command line option')
    parser.add_argument('-cp', default="", dest='config_profile', help='Config Profile inside the config file')
    parser.add_argument('-ip', action='store_true', default=False, dest='is_instance_principals', help='Use Instance Principals for Authentication')
    parser.add_argument('-dt', action='store_true', default=False, dest='is_delegation_token', help='Use Delegation Token for Authentication')
    parser.add_argument('-st', action='store_true', default=False, dest='is_security_token', help='Use Session (Security Token) Authentication, created with "oci session authenticate"')
    parser.add_argument('-i', '--interactive', nargs='?', const=DefaultSessionProfile, default="", dest='interactive_profile', metavar='PROFILE',
                        help='Interactive browser login: create or reuse a session token via the OCI CLI ("oci session authenticate"). Optional session profile name, default: {}'.format(DefaultSessionProfile))
    parser.add_argument('-log', default="log.txt", dest='log_file', help='output log file')
    parser.add_argument('-force', action='store_true', default=False, dest='force', help='force delete without confirmation')
    parser.add_argument('-debug', action='store_true', default=False, dest='debug', help='Enable debug')
    parser.add_argument('-skip_delete_compartment', action='store_true', default=False, dest='skip_delete_compartment', help='Skip Deleting the compartment at the end')
    parser.add_argument('-delete_self', action='store_true', default=False, dest='delete_self', help='Delete the target compartment after cleaning up its contents')
    parser.add_argument('-sso_user', action='store_true', default=False, dest='sso_user', help='Bypass failure when user not found')
    parser.add_argument("-rg", default="", dest='regions', help="Regions to delete comma separated")
    parser.add_argument("-c", default="", dest='compartment', help="top level compartment to delete: OCID, full path (e.g. /root/prod) or unique name")
    cmd = parser.parse_args()
    # If the user requested help, print help and exit
    if help:
        parser.print_help()
        # It's good practice to exit after printing help
        sys.exit(0)

    # If running in Cloud Shell (OCI_CLI_CLOUD_SHELL=true), default to Delegation Token
    if os.environ.get("OCI_CLI_CLOUD_SHELL", "").lower() == "true":
        print("Running in Cloud Shell, using Delegation Token authentication..")
        cmd.is_delegation_token = True
        cmd.is_instance_principals = False
        cmd.is_security_token = False
        cmd.interactive_profile = ""

    # Interactive browser login: session token authentication using the chosen session profile
    elif cmd.interactive_profile:
        cmd.is_security_token = True
        cmd.is_instance_principals = False
        cmd.is_delegation_token = False
        cmd.config_profile = cmd.interactive_profile

    # If OCI_CLI_AUTH=security_token is set (same variable the OCI CLI uses), default to Session Authentication
    elif os.environ.get("OCI_CLI_AUTH", "").lower() == "security_token" and not (cmd.is_instance_principals or cmd.is_delegation_token):
        cmd.is_security_token = True

    # Check for the interactive mode flag
    if cmd.interactive_mode:
        # Call the new function and return the final, user-confirmed values
        return interactive_mode(cmd)
    
    # Otherwise, return the original command-line arguments

    return cmd

##########################################################################
# Create - Interactive Mode
# Input - cmd object from input_command_line
# Output - new cmd object with user inputs
##########################################################################
def interactive_mode(cmd):
    """
    Prompts the user for each option, using the parsed command-line
    arguments as defaults, and returns a new namespace object.
    """
    print("Interactive Mode Enabled. Press Enter to accept the default value.")

    # Create a dictionary and initialize it with ALL attributes from the original cmd object
    final_options = vars(cmd).copy() # Use .copy() to avoid modifying the original

    # Handle the log file option
    log_file_enabled = input(f"Use a custom log file? (yes/no) [{'yes' if cmd.log_file and cmd.log_file != 'log.txt' else 'no'}]: ")
    if log_file_enabled.lower() == 'yes':
        log_file_name = input(f"Enter custom log file name [{cmd.log_file}]: ")
        final_options['log_file'] = log_file_name or cmd.log_file
    elif log_file_enabled.lower() == 'no':
        final_options['log_file'] = 'log.txt'
    
    # Handle config profile
    config_profile_enabled = input(f"Use a custom config profile? (yes/no) [{'yes' if cmd.config_profile else 'no'}]: ")
    if config_profile_enabled.lower() == 'yes':
        config_profile_name = input(f"Enter custom config profile name [{cmd.config_profile}]: ")
        final_options['config_profile'] = config_profile_name or cmd.config_profile
    elif config_profile_enabled.lower() == 'no':
        final_options['config_profile'] = 'DEFAULT'

    # Handle regions
    regions_enabled = input(f"Specify regions? (yes/no) [{'yes' if cmd.regions else 'no'}]: ")
    if regions_enabled.lower() == 'yes':
        regions_input = input(f"Enter Regions to delete (comma separated) [{cmd.regions}]: ")
        final_options['regions'] = regions_input or cmd.regions
    elif regions_enabled.lower() == 'no':
        final_options['regions'] = ""
    
    # Handle compartment ID
    compartment_enabled_default = 'yes' if cmd.compartment else 'no'
    compartment_enabled_input = input(f"Specify a top-level compartment ID? (yes/no) [{compartment_enabled_default}]: ")
    compartment_enabled = compartment_enabled_input.lower() == 'yes' or (not compartment_enabled_input and compartment_enabled_default == 'yes')

    if compartment_enabled:
        compartment_id_input = input(f"Enter top level compartment ID [{cmd.compartment}]: ")
        final_options['compartment'] = compartment_id_input or cmd.compartment
    else:
        final_options['compartment'] = ""

    # Handle boolean flags explicitly (force, debug, etc.)
    final_options['force'] = input(f"Force delete without confirmation? (yes/no) [{'yes' if cmd.force else 'no'}]: ").lower() == 'yes' or cmd.force
    final_options['debug'] = input(f"Enable debug? (yes/no) [{'yes' if cmd.debug else 'no'}]: ").lower() == 'yes' or cmd.debug
    final_options['skip_delete_compartment'] = input(f"Skip deleting the compartment at the end? (yes/no) [{'yes' if cmd.skip_delete_compartment else 'no'}]: ").lower() == 'yes' or cmd.skip_delete_compartment
    final_options['delete_self'] = input(f"Delete the target compartment after cleanup? (yes/no) [{'yes' if cmd.delete_self else 'no'}]: ").lower() == 'yes' or cmd.delete_self
    final_options['sso_user'] = input(f"Bypass failure when user not found? (yes/no) [{'yes' if cmd.sso_user else 'no'}]: ").lower() == 'yes' or cmd.sso_user

    # Handle authentication methods as a special case to ensure only one is chosen
    auth_method = "user"
    if cmd.is_instance_principals:
        auth_method = "instance"
    elif cmd.is_delegation_token:
        auth_method = "delegation"
    elif cmd.is_security_token:
        auth_method = "session"

    auth_input = input(f"Select authentication method (user/instance/delegation/session) [{auth_method}]: ") or auth_method

    final_options['is_instance_principals'] = auth_input.lower() == 'instance'
    final_options['is_delegation_token'] = auth_input.lower() == 'delegation'
    final_options['is_security_token'] = auth_input.lower() == 'session'
    if final_options['is_security_token']:
        login_input = input(f"Open browser login if the session is missing or expired? (yes/no) [{'yes' if cmd.interactive_profile else 'no'}]: ")
        if login_input.lower() == 'yes' or (not login_input and cmd.interactive_profile):
            # Never use DEFAULT for browser login: it is normally an API key profile
            profile = final_options['config_profile']
            final_options['interactive_profile'] = profile if profile and profile != 'DEFAULT' else DefaultSessionProfile
            final_options['config_profile'] = final_options['interactive_profile']
        else:
            final_options['interactive_profile'] = ""
    else:
        final_options['interactive_profile'] = ""

    # Return a new object with the final values
    return argparse.Namespace(**final_options)


##########################################################################
# Create signer for Authentication
# Input - config_profile, is_instance_principals, is_delegation_token, is_security_token
#         interactive: create/reuse the session token via the OCI CLI before using it (implies is_security_token)
#         region: region to create the interactive session in (optional, CLI prompts if empty)
# Output - config and signer objects
##########################################################################
def create_signer(config_profile, is_instance_principals, is_delegation_token, is_security_token=False, interactive=False, region=""):

    if interactive:
        is_security_token = True
        ensure_interactive_session(config_profile, region)

    # if instance principals authentications
    if is_instance_principals:
        try:
            signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
            config = {'region': signer.region, 'tenancy': signer.tenancy_id}
            return config, signer

        except Exception as e:
            print("Error obtaining instance principals certificate, aborting: {}".format(e))
            sys.exit(-1)

    # -----------------------------
    # Delegation Token
    # -----------------------------
    elif is_delegation_token:

        try:
            # check if env variables OCI_CONFIG_FILE, OCI_CONFIG_PROFILE exist and use them
            env_config_file = os.environ.get('OCI_CONFIG_FILE')
            env_config_section = os.environ.get('OCI_CONFIG_PROFILE')

            # check if file exist
            if env_config_file is None or env_config_section is None:
                print("*** OCI_CONFIG_FILE and OCI_CONFIG_PROFILE env variables not found, abort. ***")
                print("")
                sys.exit(-1)

            config = oci.config.from_file(env_config_file, env_config_section)
            delegation_token_location = config["delegation_token_file"]

            with open(delegation_token_location, 'r') as delegation_token_file:
                delegation_token = delegation_token_file.read().strip()
                # get signer from delegation token
                signer = oci.auth.signers.InstancePrincipalsDelegationTokenSigner(delegation_token=delegation_token)

                return config, signer

        except KeyError:
            print("* Key Error obtaining delegation_token_file from config profile, aborting")
            sys.exit(-1)

        except Exception as e:
            print("Error obtaining delegation token authentication, aborting: {}".format(e))
            sys.exit(-1)

    # -----------------------------
    # Session / Security Token authentication
    # Profile created with: oci session authenticate [--profile-name NAME]
    # The profile contains security_token_file, key_file, tenancy and region (no user/fingerprint).
    # https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/clitoken.htm
    # -----------------------------
    elif is_security_token:
        try:
            config = oci.config.from_file(
                oci.config.DEFAULT_LOCATION,
                (config_profile if config_profile else oci.config.DEFAULT_PROFILE)
            )
            token_file = config["security_token_file"]
            with open(os.path.expanduser(token_file), 'r') as f:
                token = f.read().strip()

            private_key = oci.signer.load_private_key_from_file(
                config["key_file"],
                pass_phrase=oci.config.get_config_value_or_default(config, "pass_phrase")
            )

            # Check the token has not expired before making any API call
            token_container = oci.auth.security_token_container.SecurityTokenContainer(None, token)
            if not token_container.valid():
                print("The session token in profile '{}' has expired.".format(config_profile))
                print("Refresh it with:  oci session refresh --profile {}".format(config_profile))
                print("or re-authenticate: oci session authenticate --profile-name {}".format(config_profile))
                sys.exit(-1)

            # Session profiles have no 'user' key; the user OCID is the 'sub' claim of the token
            if "user" not in config and token_container.get_jwt().get("sub"):
                config["user"] = token_container.get_jwt()["sub"]

            signer = oci.auth.signers.SecurityTokenSigner(token, private_key)
            return config, signer

        except (oci.exceptions.ConfigFileNotFound, oci.exceptions.ProfileNotFound, FileNotFoundError):
            command = "oci session authenticate"
            if config_profile and config_profile != oci.config.DEFAULT_PROFILE:
                command += " --profile-name {}".format(config_profile)
            print("No session token found. Please run '{}' to get a session token".format(command))
            sys.exit(-1)

        except KeyError as e:
            print("Profile '{}' is missing key {} - is this a session profile created with 'oci session authenticate'? aborting".format(config_profile, e))
            sys.exit(-1)

        except Exception as e:
            print("Error obtaining session token authentication, aborting: {}".format(e))
            sys.exit(-1)

    # -----------------------------
    # config file authentication
    # -----------------------------
    else:
        try:
            config = oci.config.from_file(
                oci.config.DEFAULT_LOCATION,
                (config_profile if config_profile else oci.config.DEFAULT_PROFILE)
            )
            oci.config.validate_config(config)
            signer = oci.signer.Signer(
                tenancy=config["tenancy"],
                user=config["user"],
                fingerprint=config["fingerprint"],
                private_key_file_location=config.get("key_file"),
                pass_phrase=oci.config.get_config_value_or_default(config, "pass_phrase"),
                private_key_content=config.get("key_content")
            )
        except oci.exceptions.ConfigFileNotFound:
            print("No config file found at {}. Please run 'oci setup config', or use -i for a browser login".format(oci.config.DEFAULT_LOCATION))
            sys.exit(-1)

        except Exception as e:
            print("Error obtaining authentication, did you configure config file? aborting: {}".format(e))
            sys.exit(-1)

        return config, signer


##########################################################################
# Session profile helpers (interactive browser login)
##########################################################################
def session_profile_status(profile):
    """
    Inspect a profile in ~/.oci/config.
    Returns (status, expiry) where status is one of:
      "missing"     - profile does not exist
      "not_session" - profile exists but is a regular API key profile (no security_token_file)
      "expired"     - session profile whose token has expired (or token file is unreadable)
      "valid"       - session profile with a valid token
    expiry is a datetime (local time) for session profiles, else None.
    """
    try:
        config = oci.config.from_file(oci.config.DEFAULT_LOCATION, profile)
    except (oci.exceptions.ConfigFileNotFound, oci.exceptions.ProfileNotFound):
        return "missing", None

    if "security_token_file" not in config:
        return "not_session", None

    try:
        with open(os.path.expanduser(config["security_token_file"]), 'r') as f:
            token = f.read().strip()
        container = oci.auth.security_token_container.SecurityTokenContainer(None, token)
        expiry = datetime.fromtimestamp(container.get_jwt()["exp"])
        return ("valid" if container.valid() else "expired"), expiry
    except Exception:
        return "expired", None


def ensure_interactive_session(profile, region=""):
    """
    Make sure a valid session token exists for `profile`, using the OCI CLI:
      - reuse it if still valid
      - try 'oci session refresh' if expired (works up to 24h after login)
      - otherwise run 'oci session authenticate' (opens a browser for login)
    Refuses to touch a profile that is not a session profile. Exits on failure.
    """
    oci_cli = shutil.which("oci")
    if oci_cli is None:
        print("Interactive login requires the OCI CLI ('oci' not found in PATH).")
        print("Install it: https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/cliinstall.htm  (or: pip install oci-cli)")
        sys.exit(-1)

    status, expiry = session_profile_status(profile)

    if status == "not_session":
        print("Profile '{}' exists in {} but is not a session profile - refusing to overwrite it.".format(profile, oci.config.DEFAULT_LOCATION))
        print("Choose another session profile name, e.g.:  --interactive MYSESSION")
        sys.exit(-1)

    if status == "valid":
        print("Reusing session profile '{}' (token valid until {:%Y-%m-%d %H:%M:%S})".format(profile, expiry))
        return

    if status == "expired":
        print("Session profile '{}' has expired, trying to refresh..".format(profile))
        result = subprocess.run([oci_cli, "session", "refresh", "--profile", profile])
        status, expiry = session_profile_status(profile)
        if result.returncode == 0 and status == "valid":
            print("Session refreshed (token valid until {:%Y-%m-%d %H:%M:%S})".format(expiry))
            return
        print("Refresh not possible, a new browser login is required.")

    print("Starting browser login for session profile '{}'..".format(profile))
    command = [oci_cli, "session", "authenticate", "--profile-name", profile]
    if region:
        command += ["--region", region]
    result = subprocess.run(command)
    if result.returncode != 0:
        print("'oci session authenticate' failed (exit code {}), aborting".format(result.returncode))
        sys.exit(-1)

    status, expiry = session_profile_status(profile)
    if status != "valid":
        print("Session profile '{}' is still not usable after login (status: {}), aborting".format(profile, status))
        sys.exit(-1)
    print("Session created (token valid until {:%Y-%m-%d %H:%M:%S})".format(expiry))


##########################################################################
# Checking SDK Version
# Minimum version requirements for OCI SDK
##########################################################################
def check_oci_version(min_oci_version_required):
    outdated = False

    for i, rl in zip(oci.__version__.split("."), min_oci_version_required.split(".")):
        if int(i) > int(rl):
            break
        if int(i) < int(rl):
            outdated = True
            break

    if outdated:
        print("Your version of the OCI SDK is out-of-date. Please first upgrade your OCI SDK Library bu running the command:")
        print("OCI SDK Version : {}".format(oci.__version__))
        print("Min SDK required: {}".format(min_oci_version_required))
        print("pip install --upgrade oci")
        quit()
