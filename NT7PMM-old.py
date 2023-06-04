import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
import time


def get_steam_game_location(game_name):
    steam_root = os.path.expanduser("~/.steam/steam")
    library_folders = [steam_root]

    # Check if the Steam library folders file exists
    library_folders_file = os.path.join(steam_root, "steamapps/libraryfolders.vdf")
    if os.path.isfile(library_folders_file):
        with open(library_folders_file, "r") as f:
            for line in f:
                line = line.strip()
                if line.startswith('"path"'):
                    folder_path = line.split('"')[3].replace("\\\\", "/")
                    library_folders.append(os.path.expanduser(folder_path))

    # Search for the game manifest file
    for library_folder in library_folders:
        manifest_file = os.path.join(library_folder, "steamapps", "appmanifest_{}.acf".format(game_name))
        if os.path.isfile(manifest_file):
            return library_folder

    return None




game_id= "389730"
game_path= get_steam_game_location(game_id)

ENABLED_MODS_PATH = game_path + "/steamapps/common/TEKKEN 7/TekkenGame/Content/Paks/~mods/"
DISABLED_MODS_PATH = os.path.expanduser("~/.config/TekkenModManager/Disabled/")
CSV_PATH = game_path + "/steamapps/common/TEKKEN 7/TekkenGame/Content/ModData/customize_item_data/mods/"
BACKUP_PATH = os.path.expanduser("~/.config/TekkenModManager/Backup/")
CONFIG = os.path.expanduser("~/.config/TekkenModManager/conf")


def clear_screen():
    subprocess.call("clear" if os.name == "posix" else "cls")

def display_mods(directory):
    mods = get_mod_files(directory)
    if not mods:
        print("No mods found.")
        return

    mod_files = []
    csv_files = []

    for mod in mods:
        mod_path = os.path.join(directory, mod)
        if os.path.isfile(mod_path) and mod_path.endswith(".pak"):
            mod_files.append(mod)
        elif os.path.isfile(mod_path) and mod_path.endswith(".csv"):
            csv_files.append(mod)
        elif os.path.isdir(mod_path):
            print(f"{mod} (Folder):")
            subfiles = get_mod_files(mod_path)
            for subfile in subfiles:
                print(f"   - {subfile}")
        else:
            print(f"{mod} (Invalid)")

    if csv_files:
        print("Available CSV Files:")
        for i, csv_file in enumerate(csv_files):
            print(f"{i+1}. {csv_file}")
        print("------------")

    if mod_files:
        print("Available Mod Files:")
        for i, mod_file in enumerate(mod_files):
            print(f"{i+1}. {mod_file}")

    
def get_mods_list(mods_path):
    mods = os.listdir(mods_path)
    return [mod for mod in mods if mod.endswith(".pak")]

def enable_mod():
    clear_screen()
    print("\033[1mEnable a Mod\033[0m")
    print("------------")
    display_mods(DISABLED_MODS_PATH)
    mods = get_mod_files(DISABLED_MODS_PATH)
    if not mods:
        time.sleep(2)
        main_menu()

    selection = input("Enter the mod ID(s) to enable (e.g., 1,2,3 or 1-3): ")
    if not selection:
        main_menu()

    try:
        mod_ids = parse_mod_ids(selection, len(mods))
    except ValueError:
        print("Invalid mod ID(s). Please try again.")
        time.sleep(2)
        main_menu()

    for mod_id in mod_ids:
        mod_name = mods[mod_id - 1]
        mod_path = os.path.join(DISABLED_MODS_PATH, mod_name)

        if os.path.isfile(mod_path) and mod_path.endswith(".pak"):
            enabled_mod_path = os.path.join(ENABLED_MODS_PATH, os.path.dirname(mod_name))
            os.makedirs(enabled_mod_path, exist_ok=True)
            shutil.move(mod_path, os.path.join(enabled_mod_path, os.path.basename(mod_name)))
            print(f"Enabled Mod: {mod_name}")
        elif os.path.isdir(mod_path):
            for root, dirs, files in os.walk(mod_path):
                for file in files:
                    file_src = os.path.join(root, file)
                    file_dest = file_src.replace(DISABLED_MODS_PATH, ENABLED_MODS_PATH, 1)
                    os.makedirs(os.path.dirname(file_dest), exist_ok=True)
                    shutil.move(file_src, file_dest)
                    print(f"Enabled Mod: {os.path.relpath(file_dest, ENABLED_MODS_PATH)}")
            shutil.rmtree(mod_path)
        else:
            print(f"Invalid Mod: {mod_name}")
    create_backup()

    time.sleep(2)
    main_menu()

def create_backup():
    # Check if the enabled mods folder exists
    if not os.path.exists(ENABLED_MODS_PATH):
        print("Enabled mods folder does not exist.")
        return

    # Check if the CSV folder exists
    if not os.path.exists(CSV_PATH):
        print("CSV folder does not exist.")
        return

    # Create the backup folder if it doesn't exist
    os.makedirs(BACKUP_PATH, exist_ok=True)

    # Delete previous backup if it exists
    shutil.rmtree(BACKUP_PATH, ignore_errors=True)

    

    # Copy the enabled mods folder to the backup folder
    shutil.copytree(ENABLED_MODS_PATH, BACKUP_PATH)

    shutil.rmtree(os.path.join(BACKUP_PATH, "CSV/"), ignore_errors=True)

    # Copy the CSV folder to the backup folder
    csv_backup_path = os.path.join(BACKUP_PATH, "CSV/")
    if not os.path.exists(csv_backup_path):
        shutil.copytree(CSV_PATH, csv_backup_path)

    print("Backup created successfully.")



def disable_mod():
    clear_screen()
    print("\033[1mDisable a Mod\033[0m")
    print("------------")
    display_mods(ENABLED_MODS_PATH)
    mods = get_mod_files(ENABLED_MODS_PATH)
    if not mods:
        time.sleep(2)
        main_menu()

    selection = input("Enter the mod ID(s) to disable (e.g., 1,2,3 or 1-3): ")
    if not selection:
        main_menu()

    try:
        mod_ids = parse_mod_ids(selection, len(mods))
    except ValueError:
        print("Invalid mod ID(s). Please try again.")
        time.sleep(2)
        main_menu()

    for mod_id in mod_ids:
        mod_name = mods[mod_id - 1]
        mod_path = os.path.join(ENABLED_MODS_PATH, mod_name)

        if os.path.isfile(mod_path) and mod_path.endswith(".pak"):
            disabled_mod_path = os.path.join(DISABLED_MODS_PATH, os.path.dirname(mod_name))
            os.makedirs(disabled_mod_path, exist_ok=True)
            shutil.move(mod_path, os.path.join(disabled_mod_path, os.path.basename(mod_name)))
            print(f"Disabled Mod: {mod_name}")
        elif os.path.isdir(mod_path):
            for root, dirs, files in os.walk(mod_path):
                for file in files:
                    file_src = os.path.join(root, file)
                    file_dest = file_src.replace(ENABLED_MODS_PATH, DISABLED_MODS_PATH, 1)
                    os.makedirs(os.path.dirname(file_dest), exist_ok=True)
                    shutil.move(file_src, file_dest)
                    print(f"Disabled Mod: {os.path.relpath(file_dest, DISABLED_MODS_PATH)}")
            shutil.rmtree(mod_path)

        else:
            print(f"Invalid Mod: {mod_name}")
    create_backup()

    time.sleep(2)
    main_menu()
    



def add_mod(archive_path=None):
    clear_screen()
    print("\033[1mAdd a Mod\033[0m")
    print("------")

    if archive_path is None:
        archive_path = input("Enter the path to the mod archive: ")

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            extract_mod(archive_path, temp_dir)
            mod_files = get_mod_files(temp_dir)
            if not mod_files:
                print("No mod files found in the archive.")
                time.sleep(1)
                return

            display_mods(temp_dir)

            csv_files = [mod_file for mod_file in mod_files if mod_file.endswith(".csv")]
            csv_selected = []
            if csv_files:
                csv_choice = input("Select the .csv file(s) to move to the CSV folder (e.g., 1,2,3 or 1-3): ")
                if csv_choice:
                    try:
                        csv_ids = parse_mod_ids(csv_choice, len(csv_files))
                        csv_selected = [csv_files[csv_id - 1] for csv_id in csv_ids]
                    except ValueError:
                        print("Invalid .csv file ID(s). Skipping CSV file selection.")

            mod_files = [mod_file for mod_file in mod_files if mod_file.endswith(".pak")]
            mod_selected = []

            mod_choice = input("Select the mod file(s) to add to the Enabled Mods folder (e.g., 1,2,3 or 1-3): ")
            if not mod_choice:
                main_menu()

            try:
                mod_ids = parse_mod_ids(mod_choice, len(mod_files))
            except ValueError:
                print("Invalid mod file ID(s). Please try again.")
                time.sleep(2)
                main_menu()

            for mod_id in mod_ids:
                mod_name = mod_files[mod_id - 1]
                mod_path = os.path.join(temp_dir, mod_name)
                if os.path.isdir(mod_path):
                    sub_mod_files = get_mod_files(mod_path)
                    for sub_mod_file in sub_mod_files:
                        sub_mod_src = os.path.join(mod_path, sub_mod_file)
                        shutil.move(sub_mod_src, ENABLED_MODS_PATH)
                        print(f"Added Mod: {os.path.join(mod_name, sub_mod_file)}")
                else:
                    shutil.move(mod_path, ENABLED_MODS_PATH)
                    print(f"Added Mod: {mod_name}")

            for csv_file in csv_selected:
                csv_path = os.path.join(temp_dir, csv_file)
                shutil.move(csv_path, CSV_PATH)
                print(f"Moved CSV File: {csv_file}")

            print("Cleaning up temporary files...")
            time.sleep(2)
    except (FileNotFoundError, zipfile.BadZipFile):
        print("Failed to extract mod archive.")
        time.sleep(2)
        main_menu()

def extract_mod(archive_path, destination):
    if archive_path.endswith(".zip"):
        with zipfile.ZipFile(archive_path, "r") as zip_ref:
            zip_ref.extractall(destination)
    elif archive_path.endswith(".pak"):
        shutil.copy(archive_path, destination)    
    elif archive_path.endswith(".rar"):
        unrar_command = ["unrar", "x", archive_path, destination]
        subprocess.run(unrar_command, check=True)
    elif archive_path.endswith(".7z"):
        subprocess.run(["7z", "x", archive_path, f"-o{destination}"], check=True)
    else:
        raise ValueError("Unsupported archive format.")

def get_mod_files(directory):
    mod_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            mod_files.append(os.path.relpath(os.path.join(root, file), directory))
    return mod_files


def parse_mod_ids(selection, num_mods):
    mod_ids = set()

    # Split the selection string by comma to get individual selections
    individual_selections = selection.split(",")

    for individual_selection in individual_selections:
        # Check if the selection is a range
        if "-" in individual_selection:
            range_parts = individual_selection.split("-")
            if len(range_parts) != 2:
                raise ValueError("Invalid range format.")

            start_id = int(range_parts[0].strip())
            end_id = int(range_parts[1].strip())

            if start_id < 1 or start_id > num_mods or end_id < 1 or end_id > num_mods or start_id > end_id:
                raise ValueError("Invalid mod ID(s) in the range.")

            # Add IDs in the range to the set of mod IDs
            mod_ids.update(range(start_id, end_id + 1))
        else:
            # Individual mod ID
            mod_id = int(individual_selection.strip())
            if mod_id < 1 or mod_id > num_mods:
                raise ValueError("Invalid mod ID(s).")

            # Add the mod ID to the set of mod IDs
            mod_ids.add(mod_id)

    return mod_ids

def load_mods_from_backup():
    clear_screen()
    print("Load Mods from Backup")

    # Check if the backup folder exists
    if not os.path.exists(BACKUP_PATH):
        print("Backup folder does not exist.")
        time.sleep(2)
        main_menu()

    # Delete the current enabled mods folder if it exists
    if os.path.exists(ENABLED_MODS_PATH):
        shutil.rmtree(ENABLED_MODS_PATH)

    if os.path.exists(CSV_PATH):
        shutil.rmtree(CSV_PATH)
    
    shutil.copytree(os.path.join(BACKUP_PATH, "CSV"), CSV_PATH)
    # Copy the backup folder to the enabled mods folder
    shutil.copytree(BACKUP_PATH, ENABLED_MODS_PATH)
    print("Mods loaded from backup successfully.")

    time.sleep(2)
    main_menu()

first_run = True

def launch_tekken():
    clear_screen()
    print("Launching Tekken 7")
    time.sleep(2)
    command = "steam steam://run/389730 &"
    subprocess.run(command, shell=True)
    main_menu()
    


def main_menu():
    global first_run
    if len(sys.argv) > 1 and first_run:
        file_path = sys.argv[1]
        add_mod(file_path)
        first_run = False
        

    clear_screen()
    print("Tekken 7 primitive mod manager")
    print("------------------------")
    print("1. Enable a Mod")
    print("2. Disable a Mod")
    print("3. Add a Mod")
    print("4. Load Mods from Backup")
    print("5. Create Backup")
    print("6. Launch Tekken")
    print("7. Exit")

    selection = input("Enter your choice (1-7): ")



    if selection == "1":
        enable_mod()
    elif selection == "2":
        disable_mod()
    elif selection == "3":
        add_mod()
    elif selection == "4":
        load_mods_from_backup()
        sys.exit()
    elif selection == "5":
        create_backup()
    elif selection == "6":
        launch_tekken()
    elif selection == "7":
        clear_screen()
        print("Goodbye!")
    else:
        print("Invalid choice. Please try again.")
        time.sleep(2)
        main_menu()


if __name__ == "__main__":
    main_menu()
