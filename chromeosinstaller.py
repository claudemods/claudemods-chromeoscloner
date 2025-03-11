import os
import subprocess

def main():
    # Ask for the location of the .img files
    img_location = input("Enter the location of the .img files: ").strip()
    if not os.path.exists(img_location):
        print(f"Directory {img_location} does not exist.")
        return

    # Ask for the target drive (e.g., /dev/sda)
    target_drive = input("Enter the target drive (e.g., /dev/sda): ").strip()
    if not os.path.exists(target_drive):
        print(f"Device {target_drive} does not exist.")
        return

    # Get a list of .img files in the specified location
    img_files = [f for f in os.listdir(img_location) if f.endswith(".img") and f.startswith("drive")]

    if not img_files:
        print(f"No .img files found in {img_location}.")
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
        img_path = os.path.join(img_location, img_file)
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
