import os
import subprocess

def main():
    # Ask for the target drive (e.g., /dev/sda)
    target_drive = input("Enter the target drive (e.g., /dev/sda): ").strip()
    if not os.path.exists(target_drive):
        print(f"Device {target_drive} does not exist.")
        return

    # Look for the 'chrome' folder in the current directory
    chrome_folder = os.path.join(os.getcwd(), "chrome")
    if not os.path.exists(chrome_folder):
        print(f"Folder 'chrome' does not exist in the current directory.")
        return

    # Run the chromeos-install.sh command
    chromeos_script = "chromeos-install.sh"
    chromeos_src = "/home/apex/Downloads/brunch_r132_stable_20250208/chromeos_16151.47.0_zork_recovery_stable-channel_ZorkMPKeys-v12.bin"
    chromeos_command = f"sudo bash {chromeos_script} -src {chromeos_src} -dst {target_drive}"

    print(f"Running command: {chromeos_command}")
    try:
        # Run the chromeos-install.sh command and wait for it to finish
        subprocess.run(chromeos_command, shell=True, check=True)
        print("chromeos-install.sh completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error running chromeos-install.sh: {e}")
        return

    # Run partprobe to update the partition table
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
