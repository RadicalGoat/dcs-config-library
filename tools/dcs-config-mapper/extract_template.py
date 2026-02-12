import argparse
import re
import shutil
from pathlib import Path
import helpers_generic 
import helpers_dcs


def extract_aircraft_config(aircraft_name: str, save_root: str, output_location: Path):
    """
    Copies .diff.lua files from DCS Saved Game to the target location
        Replacing GUIDs with placeholders.

        Args:
            aircraft_name: str - The DCS aircraft name (e.g., "FA-18C_hornet")
            save_root: str - Optional override for DCS saved games path
            output_location: Path - The target location where templates will be saved

        Returns:
            None
    """
    helpers_generic.print_debug(f"extract_aircraft_config()")

    # Verify Output Location exists
    if not output_location.exists():
        raise SystemExit(f"Error: Target path '{output_location}' does not exist.")

    # Locate Source using the new helper
    input_path = helpers_dcs.get_input_path(save_root)
    src_dir = input_path / aircraft_name / "joystick"
    
    if not src_dir.exists():
        print(f"Error: No joystick folder for '{aircraft_name}' at {src_dir}")
        return

    # Define Destination (Current Folder or --repotemplates)
    dest_dir = output_location / aircraft_name / "joystick"
    
    # Regex for Sanitization
    pattern = re.compile(r"^(.*)\s+({.*})\.diff\.lua$")

    helpers_generic.print_debug(f"Source: {src_dir}")
    helpers_generic.print_debug(f"Target: {dest_dir}")

    # Ensure the specific aircraft subfolder exists
    if not helpers_generic.NO_ACTION:
        dest_dir.mkdir(parents=True, exist_ok=True)

    # Track how many of each controller we've seen in this specific aircraft folder
    template_counts = {}

    # sorted() ensures that the instance assignment matches the 
    # deterministic logic used in the machine fingerprint (alphabetical by GUID)
    found_files = sorted(src_dir.glob("*.diff.lua"))
    
    if not found_files:
        print(f"No .diff.lua files found in {src_dir}")
        return

    for file in found_files:
        match = pattern.match(file.name)
        if match:
            ctrl_name = match.group(1).strip()
            
            # Increment the instance ID for this controller type
            instance_id = template_counts.get(ctrl_name, 0) + 1
            template_counts[ctrl_name] = instance_id

            # New Filename: Name {__GUID__}_ID.diff.lua
            # This ID acts as the "key" that will be used to look up the right controller in the fingerprint
            clean_name = f"{ctrl_name} {{__GUID__}}_{instance_id}.diff.lua"
            target_path = dest_dir / clean_name

            if not helpers_generic.NO_ACTION:
                shutil.copy2(file, target_path)
                print(f"  [EXTRACTED] {clean_name}")
            else:
                print(f"  [DRY RUN] Would extract: {clean_name}")




if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='extract_template')
    parser.add_argument('aircraft', type=str, help='The DCS aircraft module name (e.g., FA-18C_hornet)')
    
    parser.add_argument('--saveroot', type=str, 
                        help='Override DCS saved games path')
    
    parser.add_argument('--repotemplates', type=str, default=".", 
                        help='Target directory for extracted templates (Defaults to current folder)')
    
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--noaction', action='store_true', help='Dry run: see what would happen')

    args = parser.parse_args()
    helpers_generic.DEBUG = args.debug
    helpers_generic.NO_ACTION = args.noaction

    extract_aircraft_config(args.aircraft, args.saveroot, Path(args.repotemplates))