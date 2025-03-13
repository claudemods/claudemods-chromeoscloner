import os
import subprocess

# ANSI escape codes for colors
RED = "\033[31m"
TEAL = "\033[36m"
GOLD = "\033[1;33m"
GREEN = "\033[32m"
RESET = "\033[0m"

def print_colored_ascii():
    # Red ASCII art
    red_ascii = f"""{RED}
░█████╗░██╗░░░░░░█████╗░██╗░░░██╗██████╗░███████╗███╗░░░███╗░█████╗░██████╗░░██████╗
██╔══██╗██║░░░░░██╔══██╗██║░░░██║██╔══██╗██╔════╝████╗░████║██╔══██╗██╔══██╗██╔════╝
██║░░╚═╝██║░░░░░███████║██║░░░██║██║░░██║█████╗░░██╔████╔██║██║░░██║██║░░██║╚█████╗░
██║░░██╗██║░░░░░██╔══██║██║░░░██║██║░░██║██╔══╝░░██║╚██╔╝██║██║░░██║██║░░██║░╚═══██╗
╚█████╔╝███████╗██║░░██║╚██████╔╝██████╔╝███████╗██║░╚═╝░██║╚█████╔╝██████╔╝██████╔╝
░╚════╝░╚══════╝╚═╝░░░░░░╚═════╝░╚═════╝░╚══════╝╚═╝░░░░░╚═╝░╚════╝░╚═════╝░╚═════╝░
{RESET}"""

    # Teal custom text
    teal_text = f"{TEAL}ClaudeMods ChromeOS Installer v1.0{RESET}"

    # Print the ASCII art and text
    print(red_ascii)
    print(teal_text)
    print()

def main():
    print_colored_ascii()

    # Ask for the target drive (e.g., /dev/sda) in green
    print(f"{GREEN}Enter the target drive (e.g., /dev/sda): {RESET}", end="")
    target_drive = input().strip()
    if not os.path.exists(target_drive):
        print(f"Device {target_drive} does not exist.")
        return

    # Ask for the file name of the .bin recovery image in green
    print(f"{GREEN}Enter the file name of the .bin recovery image (e.g., recovery.bin): {RESET}", end="")
    recovery_image_name = input().strip()
    recovery_image_path = recovery_image_name  # Assume the file is in the current directory
    if not os.path.exists(recovery_image_path):
        print(f"Recovery image {recovery_image_path} does not exist in the current directory.")
        return

    # Look for the 'chromeos-backup' folder in the current directory
    chromeos_backup_folder = os.path.join(os.getcwd(), "chromeos-backup")
    if not os.path.exists(chromeos_backup_folder):
        print(f"Folder 'chromeos-backup' does not exist in the current directory.")
        return

    # Run the chromeos-install.sh command
    chromeos_script = "chromeos-install.sh"
    chromeos_command = f"sudo bash {chromeos_script} -src {recovery_image_path} -dst {target_drive}"

    try:
        # Run the chromeos-install.sh command and wait for it to finish
        print(f"{GOLD}")  # Set terminal text color to gold for command output
        subprocess.run(chromeos_command, shell=True, check=True)
        print(f"{RESET}", end="")  # Reset terminal text color
        print("ChromeOS installation completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"{RESET}Error running chromeos-install.sh: {e}")
        return

    # Run partprobe to update the partition table
    partprobe_command = f"sudo partprobe {target_drive}"
    try:
        print(f"{GOLD}")  # Set terminal text color to gold for command output
        subprocess.run(partprobe_command, shell=True, check=True)
        print(f"{RESET}", end="")  # Reset terminal text color
        print("Partition table updated successfully.")
    except subprocess.CalledProcessError as e:
        print(f"{RESET}Error running partprobe: {e}")
        return

    # Get a list of .img files in the 'chromeos-backup' folder
    img_files = [f for f in os.listdir(chromeos_backup_folder) if f.endswith(".img") and f.startswith("drive")]

    if not img_files:
        print(f"No .img files found in {chromeos_backup_folder}.")
        return

    # Install each .img file to the corresponding partition
    for img_file in img_files:
        # Extract the partition number from the filename (e.g., drive1.img → 1)
        partition_number = img_file.replace("drive", "").replace(".img", "")
        if not partition_number.isdigit():
            print(f"Skipping invalid file: {img_file}")
            continue

        # Construct the target partition (e.g., /dev/sda1)
        target_partition = f"{target_drive}{partition_number}"

        # Construct the dd command
        img_path = os.path.join(chromeos_backup_folder, img_file)
        command = f"sudo dd if={img_path} of={target_partition} bs=4M conv=fsync status=progress"

        # Run the command
        print(f"{GOLD}")  # Set terminal text color to gold for command output
        try:
            subprocess.run(command, shell=True, check=True)
            print(f"{RESET}", end="")  # Reset terminal text color
            print(f"Successfully installed {img_file} to {target_partition}.")
        except subprocess.CalledProcessError as e:
            print(f"{RESET}Error installing {img_file} to {target_partition}: {e}")

if __name__ == "__main__":
    main()
