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
    teal_text = f"{TEAL}ClaudeMods ChromeOS Installer v1.01{RESET}"

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

    # Look for the 'chromeos-backup.squashfs' file in the current directory
    squashfs_file = os.path.join(os.getcwd(), "chromeos-backup.squashfs")
    if not os.path.exists(squashfs_file):
        print(f"SquashFS file 'chromeos-backup.squashfs' does not exist in the current directory.")
        return

    # Create a temporary directory to mount the SquashFS file
    mount_point = "/mnt/chromeos-backup"
    os.makedirs(mount_point, exist_ok=True)

    # Mount the SquashFS file
    try:
        subprocess.run(f"sudo mount -t squashfs {squashfs_file} {mount_point}", shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to mount {squashfs_file}: {e}")
        os.rmdir(mount_point)
        return

    # Run the chromeos-install.sh command
    chromeos_script = "chromeos-install.sh"
    chromeos_command = f"sudo bash {chromeos_script} -src {recovery_image_path} -dst {target_drive}"

    try:
        # Run the chromeos-install.sh command and wait for it to finish
        print(f"{GOLD}")  # Set terminal text color to gold for command output
        subprocess.run(chromeos_command, shell=True, check=True)
        print(f"{RESET}", end="")  # Reset terminal text color
    except subprocess.CalledProcessError as e:
        print(f"{RESET}Error running chromeos-install.sh: {e}")
        subprocess.run(f"sudo umount {mount_point}", shell=True)
        os.rmdir(mount_point)
        return

    # Run partprobe to update the partition table
    partprobe_command = f"sudo partprobe {target_drive}"
    try:
        print(f"{GOLD}")  # Set terminal text color to gold for command output
        subprocess.run(partprobe_command, shell=True, check=True)
        print(f"{RESET}", end="")  # Reset terminal text color
        # Print "Partition table updated successfully." in green
        print(f"{GREEN}Partition table updated successfully.{RESET}")
    except subprocess.CalledProcessError as e:
        print(f"{RESET}Error running partprobe: {e}")
        subprocess.run(f"sudo umount {mount_point}", shell=True)
        os.rmdir(mount_point)
        return

    # Get a list of .img files in the mounted SquashFS directory
    img_files = [f for f in os.listdir(mount_point) if f.endswith(".img") and f.startswith("drive")]

    if not img_files:
        print(f"No .img files found in {mount_point}.")
        subprocess.run(f"sudo umount {mount_point}", shell=True)
        os.rmdir(mount_point)
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

        # Print "Drive [number] started" in green
        print(f"{GREEN}Drive {partition_number} Installation Started{RESET}")

        # Construct the dd command
        img_path = os.path.join(mount_point, img_file)
        command = f"sudo dd if={img_path} of={target_partition} bs=4M conv=fsync status=progress"

        # Run the command
        print(f"{GOLD}")  # Set terminal text color to gold for command output
        try:
            subprocess.run(command, shell=True, check=True)
            print(f"{RESET}", end="")  # Reset terminal text color
            # Print "Drive [number] finished" in green
            print(f"{GREEN}Drive {partition_number} Installation Finished{RESET}")
        except subprocess.CalledProcessError as e:
            print(f"{RESET}Error installing {img_file} to {target_partition}: {e}")

    # Unmount the SquashFS file
    subprocess.run(f"sudo umount {mount_point}", shell=True)

    # Remove the temporary mount point
    os.rmdir(mount_point)

    # Print final completion messages in green
    print(f"{GREEN}Your ChromeOS/ChromiumOs Backup Install is Complete{RESET}")
    print(f"{GREEN}You Can Now Reboot Into ChromeOS/ChromiumOS{RESET}")

if __name__ == "__main__":
    main()
