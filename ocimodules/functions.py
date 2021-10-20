# import only system from os
from os import system, name
import argparse
import oci


##########################################################################
# define our clear function
##########################################################################
def clear():

    # for windows
    if name == 'nt':
        _ = system('cls')

    # for mac and linux(here, os.name is 'posix')
    else:
        _ = system('clear')


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
    parser.add_argument('-cf', default="", dest='config_file', help='OCI CLI Config file')
    parser.add_argument('-cp', default="", dest='config_profile', help='Config Profile inside the config file')
    parser.add_argument('-force', action='store_true', default=False, dest='force', help='force delete without confirmation')
    parser.add_argument('-debug', action='store_true', default=False, dest='debug', help='Enable debug')
    parser.add_argument('-skip_delete_compartment', action='store_true', default=False, dest='skip_delete_compartment', help='Skip Deleting the compartment at the end')
    parser.add_argument("-rg", default="", dest='regions', help="Regions to delete comma separated")
    parser.add_argument("-c", default="", dest='compartment', help="top level compartment id to delete")
    cmd = parser.parse_args()
    if help:
        parser.print_help()

    return cmd


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
