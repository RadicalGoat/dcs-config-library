import argparse
import json
import re
import shutil
from pathlib import Path
import helpers_generic
import helpers_dcs

def find_fingerprint_by_hostname(search_path: Path, hostname: str) -> dict:
    """
    Finds the fingerprint JSON in repo/fingerprints/ matching the hostname.

        Args:
            repo_root: Path - The root of the repository
            hostname: str - The target machine's hostname to match in the fingerprints

        Returns:
            dict - The matching fingerprint data
    """
    helpers_generic.print_debug(f"find_fingerprint_by_hostname()")

    if not search_path.exists():
        raise SystemExit(f"Error: Fingerprint path '{search_path}' not found.")

    for file in search_path.glob("*.json"):
        try:
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if data.get("hostname") == hostname:
                    return data
        except (json.JSONDecodeError, KeyError):
            continue
    
    raise SystemExit(f"Error: No fingerprint found for hostname '{hostname}' in {search_path}")




def restore_aircraft_config(aircraft_name: str, hostname: str, fprint_dir: Path, template_root: Path, save_root: str = None):
    """
    Restores joystick configuration for a specific aircraft by matching template files to the hardware fingerprints.

        Args:
            aircraft_name: str - The name of the aircraft module (e.g., "F-16C_50")
            hostname: str - The target machine's hostname to find the correct fingerprint
            fprint_dir: Path - Directory where fingerprint JSON files are stored   
            template_root: Path - Root directory of the joystick templates
            save_root: str (optional) - If provided, the root path of the DCS Saved Games directory to directly place restored configs. If not provided, outputs to current directory for manual staging.
        Returns:
            None - The function performs file operations and prints status messages.
    """
    # Load Fingerprint
    fingerprint = find_fingerprint_by_hostname(fprint_dir, hostname)
    print(f"Using fingerprint for hostname '{hostname}'.")
    print(f"Contains:")
    print(f"machine_guid:{fingerprint.get('machine_guid')}")
    print(f"with {len(fingerprint.get('controllers', []))} controllers.")

    hardware_map = fingerprint.get("controllers", [])

    # Locate Templates
    src_dir = template_root / aircraft_name / "joystick"
    if not src_dir.exists():
        raise SystemExit(f"Error: Template source not found at {src_dir}")

    # Determine Output Location
    if save_root:
        base_output = helpers_dcs.get_input_path(save_root)
        print(f"Targeting DCS Installation: {base_output}")
    else:
        base_output = Path(".")
        print("Targeting local directory for manual staging.")

    output_dir = base_output / aircraft_name / "joystick"
    template_pattern = re.compile(r"^(.*)\s+({__GUID__})_(\d+)\.diff\.lua$")

    if not helpers_generic.NO_ACTION:
        output_dir.mkdir(parents=True, exist_ok=True)

    for t_file in src_dir.glob("*.diff.lua"):
        match = template_pattern.match(t_file.name)
        if not match:
            continue

        ctrl_name = match.group(1).strip()
        instance_id = int(match.group(3))

        # Marriage: Find matching hardware
        target_hw = next(
            (item for item in hardware_map 
             if item['controller_name'] == ctrl_name and item['instance_id'] == instance_id),
            None
        )

        if target_hw:
            real_guid = target_hw['dcs_guid']
            restored_filename = f"{ctrl_name} {real_guid}.diff.lua"
            target_path = output_dir / restored_filename

            # Backup any existing files before overwriting
            if target_path.exists():
                backup_path = target_path.with_suffix(target_path.suffix + ".old")
                if not helpers_generic.NO_ACTION:
                    # Overwrite existing .old if it exists to keep only the most recent backup
                    target_path.replace(backup_path)
                    print(f"  [BACKUP] Existing file renamed to: {backup_path.name}")
                else:
                    print(f"  [DRY RUN] Would rename existing {target_path.name} to .old")

            if not helpers_generic.NO_ACTION:
                shutil.copy2(t_file, target_path)
                print(f"  [RESTORED] {restored_filename}")
            else:
                print(f"  [DRY RUN] Would map {ctrl_name}_{instance_id} to {real_guid}")
        else:
            print(f"  [WARNING] No hardware match for: {ctrl_name} (Instance {instance_id})")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='restoredcs')
    parser.add_argument('aircraft', help='The aircraft module name')
    parser.add_argument('hostname', help='Target machine hostname')
    parser.add_argument('--repofprints', type=str, default=".", help='Fingerprint directory')
    parser.add_argument('--repotemplates', type=str, default=".", help='Templates directory')
    parser.add_argument('--saveroot', type=str, help='DCS Saved Games root')
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--noaction', action='store_true')

    args = parser.parse_args()
    helpers_generic.DEBUG = args.debug
    helpers_generic.NO_ACTION = args.noaction

    restore_aircraft_config(
        args.aircraft, 
        args.hostname, 
        Path(args.repofprints), 
        Path(args.repotemplates),
        args.saveroot
    )