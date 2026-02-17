from pathlib import Path
import helpers_generic

def get_dcs_save_path(override_path: str = None) -> Path:
    """
    Locates the DCS Saved Games folder. 
    Prioritizes override_path if provided.

        Args:
            override_path (str, optional): Override path to use instead of default DCS save path
                Points to folder that contains top level DCS configuration with the expected structure.
                Note that this is not the path to the "Saved Games/DCSxxx" folder itself, but rather the tail of this path.
                This allows the script to be used for any DCS Saved Games folder.

        Returns:
            Path: The path to the DCS saved games directory.
    """
    helpers_generic.print_debug(f"helpers_dcs.get_dcs_save_path(override={override_path})")

    if override_path:
        # Strip trailing quotes or spaces that terminals sometimes inject
        p = Path(override_path.strip(' "')) 
        if p.exists():
            return p
        else:
            print(f"Error: Path {override_path} provided for DCS configuration root folder does not exist.")
            raise SystemExit(1)

    home = Path.home()
    # List of common DCS folder names in Saved Games
    paths = [
        home / "Saved Games" / "DCS",
        home / "Saved Games" / "DCS.openbeta"
    ]
    
    for p in paths:
        if p.exists():
            helpers_generic.print_debug(f"Found DCS path: {p}")
            return p
            
    return None


def get_input_path(save_root: str = None) -> Path:
    """
    Returns the Path to the Config/Input folder.

    Args:
        save_root (str, optional): Override path to use instead of default DCS save path
    
    Returns:
        input_path (Path): The path to the DCS Config/Input directory.
    """
    dcs_path = get_dcs_save_path(save_root)
    if not dcs_path:
        print("Error: Could not locate DCS Saved Games folder.")
        raise SystemExit(1)
        
    input_path = dcs_path / "Config" / "Input"
    return input_path