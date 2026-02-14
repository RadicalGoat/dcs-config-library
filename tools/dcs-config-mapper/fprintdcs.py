import json
import socket
import re
import argparse
import subprocess

from datetime import datetime, UTC
from pathlib import Path

import helpers_generic
import helpers_dcs

# Constants
SCHEMA_VERSION = 1



def get_dcs_controllers(save_root: str = None) -> list:
    """
    Scans DCS config files to find registered joystick devices.
    Tracks multiple instances of the same hardware name.
    
        Args:
            None
        
        Returns:
            controllers (list): A list of dictionaries containing controller metadata
                Each dictionary contains:
                    - controller_name (str): The name of the controller
                    - dcs_guid (str): The DCS GUID associated with the controller

    """
    helpers_generic.print_debug(f"get_dcs_controllers()")

    controllers = []

    dcs_path = helpers_dcs.get_dcs_save_path(override_path=save_root)
    
    if not dcs_path:
        print(f"Error: Path {save_root} does not exist.")
        raise SystemExit(1)

    input_path = dcs_path / "Config" / "Input"
    if not input_path.exists():
        print(f"Error: Path {input_path} does not exist.")
        raise SystemExit(1)

    # Regex to extract "Name" and "{GUID}" from "Name {GUID}.diff.lua"
    # Matches: Joy Name {1234-5678...}
    pattern = re.compile(r"^(.*)\s+({.*})\.diff\.lua$")
    
    # Track how many times we've seen a specific controller name
    # to handle identical hardware devices.
    seen_guids = set()

    # Walk through the Input folder to find joystick subfolders
    # Sort the directories so we process aircraft in a fixed order (A-10 before F-16)
    for joy_dir in sorted(input_path.glob("**/joystick")):        

        # instance_id is per-aircraft
        name_counts = {} 
        
        # Use sorted() to make instance_id assignment deterministic
        # This sort the files so {666} ALWAYS comes before {777}
        for file in sorted(joy_dir.glob("*.diff.lua")):
            match = pattern.match(file.name)
            if match:
                ctrl_name = match.group(1).strip()
                ctrl_guid = match.group(2).strip()

                # Increment the instance count BEFORE the seen_guids check
                # so that the 2nd joystick in a folder is always "Instance 2"
                instance_count = name_counts.get(ctrl_name, 0) + 1
                name_counts[ctrl_name] = instance_count

                if ctrl_guid not in seen_guids:
                    controllers.append({
                        "controller_name": ctrl_name,
                        "dcs_guid": ctrl_guid,
                        "instance_id": instance_count  # Helps DPM-003 match dual-sticks
                    })
                    seen_guids.add(ctrl_guid)

    # We will not hard-exit here if a machine simply has no sticks yet
    if not controllers:
        print(f"Warning: No joystick GUIDs found in path: {input_path}.")

    return controllers





def get_machine_guid() -> str:
    """
    Retrieves the unique Hardware UUID from the BIOS via WMIC.
    This is unique per physical machine, regardless of OS cloning.
    
        Args:
            None
        
        Returns:
            uuid: the unique hardware key of the machine from the motherboard
        
    """
    helpers_generic.print_debug("get_machine_guid()")

    try:
        # Executes the wmic command to get the UUID
        # Note that wmic is deprecated in Windows 10/11, but it is still widely available and works for this purpose.
        cmd = 'wmic csproduct get uuid'
        output = subprocess.check_output(cmd, shell=True).decode()
        
        # The output from the shell typically looks like this (including blank lines):
        #     UUID
        #     12345678-1234-1234-1234-123456789ABC
        #
        #
        # From which we need to extract the UUID value itself.
        # The algorithm for this is:
        #     splitlines() returns a list of lines (including blank lines)
        #     strip() removes whitespace if a line exists - in doing this the blank lines become enpty strings and the if return False so they are filtered out
        #     Finally, the list is stripped again to remove any remaining whitespace.
        # So
        #     Parsing the output returns: ['UUID', 'XXXX-XXXX...'])
        # We then take the second value in the list as the UUID as long as there are at least two lines of output.
        lines = [line.strip() for line in output.splitlines() if line.strip()]
        
        if len(lines) < 2:
            raise ValueError("No UUID returned from WMIC.")
            
        uuid = lines[1]
        print(f"Found Hardware UUID: {uuid}")
        return uuid

    except Exception as e:
        print(f"Error: Failed to retrieve Hardware UUID: {e}")
        raise SystemExit(1)




def get_hostname() -> str:
    """
    Retreives the machine hostname
    
        Args:
            None

        Returns:
            <str> The machine hostname value
    """
    helpers_generic.print_debug(f"get_hostname()")

    hostname = socket.gethostname()

    if len(hostname) == 0:
        print(f"Error: No machine hostname found.")
        raise SystemExit(1)

    return hostname




def build_machine_record(save_root: str = None) -> dict:
    """
    Builds a machine record dictionary containing metadata about the current machine.
    
        Args:
            None

        Returns:
            dict: A dictionary containing the machine record data
    """
    helpers_generic.print_debug(f"build_machine_record()")

    return {
        "schema_version": SCHEMA_VERSION,
        "machine_guid": get_machine_guid(),
        "hostname": get_hostname(),
        "last_seen": datetime.now(UTC).isoformat(timespec="seconds"),
        "controllers": get_dcs_controllers(save_root=save_root)
    }




def build_machine_fingerprint(save_root: str = None,dest_dir: Path = Path(".")):
    """
    Builds a machine fingerprint record containing metadata about the current machine.
    
        Args:
            save_root (str): The root path name where DCS saved games are stored.
            dest_dir (Path): The destination directory where the machine fingerprint file will be written.
                Accepts and optional destination directory to make testing easier.

        Returns:
            output_path (Path): The path to the written machine fingerprint file
    """
    helpers_generic.print_debug(f"build_machine_fingerprint()")

    record = build_machine_record(save_root=save_root)
    dest_dir.mkdir(parents=True, exist_ok=True)

    output_path = dest_dir / f"{record['hostname']}_{record['machine_guid']}.json"

    output_path.write_text(
        json.dumps(record, indent=2),
        encoding="utf-8"
    )
    return output_path # Returning the path makes assertions easier



def get_command_line_args():
    """  
    Parses command line arguments using argparse.  
    
    Sets the global flags DEBUG and NO_ACTION and returns the config file name.  
        Args:
            None
    
        Returns:
            args: The parsed command line arguments
    """  
    helpers_generic.print_debug(f"get_command_line_args()")

    parser = argparse.ArgumentParser(  
        description="A program to builds a fingerprint record containing metadata about the current DCS installation.",  
        # 'prog' is used in the help message, like 'update-site'  
        prog='fprintdcs' 
    )  

    # Optional flag arguments (store_true means it defaults to False)  

    # allows non-standard DCS install locations to be specified
    parser.add_argument(  
        '--saveroot',  
        type=str,  
        help='The root path name where DCS saved games are stored.'  
    )  

    # Checks for '--debug' and setting the global DEBUG.  
    parser.add_argument(  
        '--debug',  
        action='store_true',  
        help='Enables debug.'  
    )  

    # Checks for '--noaction' and setting the global NO_ACTION.  
    parser.add_argument(  
        '--noaction',  
        action='store_true',  
        help='Dry run with no actions performed.'  
    )  
    
    # Note: argparse automatically handles the '--help' argument (and '-h') and exits after displaying it.  

    # If invalid arguments argparse will print an error and exit (sys.exit(2)).  
    # If no arguments are provided, it will print an error about the missing 'config_file' and exit.  
    args = parser.parse_args()  

    # Process the parsed arguments and set globals/print messages  

    # Set the globals based on the parsed values  
    # As these were store_true by default, they will be disabled if no arguments are  
    helpers_generic.DEBUG = args.debug  
    helpers_generic.NO_ACTION = args.noaction  
    
    # Print messages as in your original code  
    if helpers_generic.DEBUG: 
        print("DEBUG: ON:")  
        
    helpers_generic.NO_ACTION and print("No Actions selected: Actions will NOT be performed")  

    # Return the defined args 
    return args




if __name__ == "__main__":

    # When run directly, it uses the default current directory
    args = get_command_line_args()

    helpers_generic.print_debug(f"__main__")

    try:
        path = build_machine_fingerprint(save_root=args.saveroot)
        print(f"Wrote machine record to: {path.resolve()}")

    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")

