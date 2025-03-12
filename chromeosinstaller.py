import os
import subprocess

# ANSI escape codes for colors
RED = "\033[31m"
TEAL = "\033[36m"
GOLD = "\033[33m"
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
        print(f"{GOLD}Device {target_drive} does not exist.{RESET}")
        return

    # Ask for the location of the recovery image in green
    print(f"{GREEN}Enter the full path to the recovery image: {RESET}", end="")
    recovery_image_path = input().strip()
    if not os.path.exists(recovery_image_path):
        print(f"{GOLD}Recovery image {recovery_image_path} does not exist.{RESET}")
        return

    # Extract the recovery image name from the path
    recovery_image_name = os.path.basename(recovery_image_path)

    # Look for the 'chrome' folder in the current directory
    chrome_folder = os.path.join(os.getcwd(), "chrome")
    if not os.path.exists(chrome_folder):
        print(f"{GOLD}Folder 'chrome' does not exist in the current directory.{RESET}")
        return

    # Run the chromeos-install.sh command (default color)
    chromeos_script = "chromeos-install.sh"
    chromeos_command = f"sudo bash {chromeos_script} -src {recovery_image_path} -dst {target_drive}"

    print(f"Running command: {chromeos_command}")
    try:
        # Run the chromeos-install.sh command and wait for it to finish
        subprocess.run(chromeos_command, shell=True, check=True)
        print("chromeos-install.sh completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error running chromeos-install.sh: {e}")
        return

    # Run partprobe to update the partition table (default color)
    partprobe_command = f"sudo partprobe {target_drive}"
    print(f"Running command: {partprobe_command}")
    try:
        subprocess.run(partprobe_command, shell=True, check=True)
        print("Partition table updated successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error running partprobe: {e}")
        return

    # Get a list of .img files in the 'chrome' folder
    img_files = [f for f in os.listdir(chrome_folder) if f.endswith(".img") and f.startswith("drive")]

    if not img_files:
        print(f"No .img files found in {chrome_folder}.")
        return

    # Install each .img file to the corresponding partition (default color)
    for img_file in img_files:
        # Extract the partition number from the filename (e.g., drive1.img → 1)
        partition_number = img_file.replace("drive", "").replace(".img", "")
        if not partition_number.isdigit():
            print(f"Skipping invalid file: {img_file}")
            continue

        # Construct the target partition (e.g., /dev/sda1)
        target_partition = f"{target_drive}{partition_number}"

        # Construct the dd command
        img_path = os.path.join(chrome_folder, img_file)
        command = f"sudo dd if={img_path} of={target_partition} bs=4M conv=fsync status=progress"

        # Run the command
        print(f"Installing {img_file} to {target_partition}...")
        try:
            subprocess.run(command, shell=True, check=True)
            print(f"Successfully installed {img_file} to {target_partition}.")
        except subprocess.CalledProcessError as e:
            print(f"Error installing {img_file} to {target_partition}: {e}")

if __name__ == "__main__":
    main()
