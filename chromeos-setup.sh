#!/bin/bash

# Initial checks
if ( ! test -z {,} ); then echo "Must be ran with \"bash\""; exit 1; fi
if [ -z $(which cgpt) ]; then echo "cgpt needs to be installed first"; exit 1; fi
if [ -z $(which pv) ]; then echo "pv needs to be installed first"; exit 1; fi
if [ $(whoami) != "root" ]; then echo "Please run this script with sudo"; exit 1; fi

# Function to display usage information
usage() {
    echo ""
    echo "claudemods chromeos setup script"
    echo "Usage: chromeos-setup.sh -dst destination"
    echo "-dst (destination), --destination (destination)  Device (e.g., /dev/sda)"
    echo "-h, --help                                      Display this menu"
}

# Function to calculate block size
blocksize() {
    local path="$1"
    if [ -b "${path}" ]; then
        local dev="${path##*/}"
        local sys="/sys/block/${dev}/queue/logical_block_size"
        if [ -e "${sys}" ]; then
            cat "${sys}"
        else
            local part="${path##*/}"
            local block
            block="$(get_block_dev_from_partition_dev "${path}")"
            block="${block##*/}"
            cat "/sys/block/${block}/${part}/queue/logical_block_size"
        fi
    else
        echo 512
    fi
}

# Function to calculate the number of sectors
numsectors() {
    local block_size
    local sectors
    local path="$1"
    if [ -b "${path}" ]; then
        local dev="${path##*/}"
        block_size="$(blocksize "${path}")"
        if [ -e "/sys/block/${dev}/size" ]; then
            sectors="$(cat "/sys/block/${dev}/size")"
        else
            part="${path##*/}"
            block="$(get_block_dev_from_partition_dev "${path}")"
            block="${block##*/}"
            sectors="$(cat "/sys/block/${block}/${part}/size")"
        fi
    else
        local bytes
        bytes="$(ls -nl "${path}" | xargs | cut -d' ' -f5)"
        local rem=$(( bytes % 512 ))
        block_size=512
        sectors=$(( bytes / 512 ))
        if [ "${rem}" -ne 0 ]; then
            sectors=$(( sectors + 1 ))
        fi
    fi
    echo $(( sectors * 512 / block_size ))
}

# Function to write the base partition table
write_base_table() {
    local target="$1"
    local blocks
    block_size=$(blocksize "${target}")
    numsecs=$(numsectors "${target}")
    local curr=32768
    if [ $(( 0 & (block_size - 1) )) -gt 0 ]; then
        echo "Primary Entry Array padding is not block aligned." >&2
        exit 1
    fi
    cgpt create -p $(( 0 / block_size )) "${target}" 2> /dev/null
    blocks=$(( 8388608 / block_size ))
    if [ $(( 8388608 % block_size )) -gt 0 ]; then
       : $(( blocks += 1 ))
    fi
    cgpt add -i 11 -b $(( curr / block_size )) -s ${blocks} -t firmware     -l "RWFW" "${target}"
    : $(( curr += blocks * block_size ))
    blocks=$(( 1 / block_size ))
    if [ $(( 1 % block_size )) -gt 0 ]; then
       : $(( blocks += 1 ))
    fi
    cgpt add -i 6 -b $(( curr / block_size )) -s ${blocks} -t kernel     -l "KERN-C" "${target}"
    : $(( curr += blocks * block_size ))
    if [ $(( curr % 4096 )) -gt 0 ]; then
      : $(( curr += 4096 - curr % 4096 ))
    fi
    blocks=$(( 1073741824 / block_size ))
    if [ $(( 1073741824 % block_size )) -gt 0 ]; then
       : $(( blocks += 1 ))
    fi
    cgpt add -i 7 -b $(( curr / block_size )) -s ${blocks} -t rootfs     -l "ROOT-C" "${target}"
    : $(( curr += blocks * block_size ))
    blocks=$(( 1 / block_size ))
    if [ $(( 1 % block_size )) -gt 0 ]; then
       : $(( blocks += 1 ))
    fi
    cgpt add -i 9 -b $(( curr / block_size )) -s ${blocks} -t reserved     -l "reserved" "${target}"
    : $(( curr += blocks * block_size ))
    blocks=$(( 1 / block_size ))
    if [ $(( 1 % block_size )) -gt 0 ]; then
       : $(( blocks += 1 ))
    fi
    cgpt add -i 10 -b $(( curr / block_size )) -s ${blocks} -t reserved     -l "reserved" "${target}"
    : $(( curr += blocks * block_size ))
    blocks=$(( 2062336 / block_size ))
    if [ $(( 2062336 % block_size )) -gt 0 ]; then
       : $(( blocks += 1 ))
    fi
    : $(( curr += blocks * block_size ))
    blocks=$(( 67108864 / block_size ))
    if [ $(( 67108864 % block_size )) -gt 0 ]; then
       : $(( blocks += 1 ))
    fi
    cgpt add -i 2 -b $(( curr / block_size )) -s ${blocks} -t kernel     -l "KERN-A" "${target}"
    : $(( curr += blocks * block_size ))
    blocks=$(( 67108864 / block_size ))
    if [ $(( 67108864 % block_size )) -gt 0 ]; then
       : $(( blocks += 1 ))
    fi
    cgpt add -i 4 -b $(( curr / block_size )) -s ${blocks} -t kernel     -l "KERN-B" "${target}"
    : $(( curr += blocks * block_size ))
    if [ $(( curr % 4096 )) -gt 0 ]; then
      : $(( curr += 4096 - curr % 4096 ))
    fi
    blocks=$(( 16777216 / block_size ))
    if [ $(( 16777216 % block_size )) -gt 0 ]; then
       : $(( blocks += 1 ))
    fi
    cgpt add -i 8 -b $(( curr / block_size )) -s ${blocks} -t data     -l "OEM" "${target}"
    : $(( curr += blocks * block_size ))
    blocks=$(( 67108864 / block_size ))
    if [ $(( 67108864 % block_size )) -gt 0 ]; then
       : $(( blocks += 1 ))
    fi
    : $(( curr += blocks * block_size ))
    blocks=$(( 67108864 / block_size ))
    if [ $(( 67108864 % block_size )) -gt 0 ]; then
       : $(( blocks += 1 ))
    fi
    cgpt add -i 12 -b $(( curr / block_size )) -s ${blocks} -t efi     -l "EFI-SYSTEM" "${target}"
    : $(( curr += blocks * block_size ))
    if [ $(( curr % 4096 )) -gt 0 ]; then
      : $(( curr += 4096 - curr % 4096 ))
    fi
    blocks=$(( 4294967296 / block_size ))
    if [ $(( 4294967296 % block_size )) -gt 0 ]; then
       : $(( blocks += 1 ))
    fi
    cgpt add -i 5 -b $(( curr / block_size )) -s ${blocks} -t rootfs     -l "ROOT-B" "${target}"
    : $(( curr += blocks * block_size ))
    if [ $(( curr % 4096 )) -gt 0 ]; then
      : $(( curr += 4096 - curr % 4096 ))
    fi
    blocks=$(( 4294967296 / block_size ))
    if [ $(( 4294967296 % block_size )) -gt 0 ]; then
       : $(( blocks += 1 ))
    fi
    cgpt add -i 3 -b $(( curr / block_size )) -s ${blocks} -t rootfs     -l "ROOT-A" "${target}"
    : $(( curr += blocks * block_size ))
    if [ $(( curr % 4096 )) -gt 0 ]; then
      : $(( curr += 4096 - curr % 4096 ))
    fi
    blocks=$(( numsecs - (curr + 24576) / block_size ))
    cgpt add -i 1 -b $(( curr / block_size )) -s ${blocks} -t data     -l "STATE" "${target}"
    cgpt add -i 2 -S 0 -T 15 -P 15 "${target}"
    cgpt add -i 4 -S 0 -T 15 -P 0 "${target}"
    cgpt add -i 6 -S 0 -T 15 -P 0 "${target}"
    cgpt boot -p -i 12 "${target}"
    cgpt add -i 12 -B 0 "${target}"
    cgpt show "${target}"
}

# Function to check arguments
check_args() {
    if [ -z "$destination" ]; then
        echo "The destination parameter must be provided."
        usage
        exit 1
    fi
}

# Main script execution
if [ $# -eq 0 ]; then
    echo "No arguments provided. Use -h for help."
    exit 1
fi

while [ $# -gt 0 ]; do
    case "$1" in
        -dst | --destination)
            shift
            if [ -z "${1##/dev/*}" ]; then
                destination="$1"
            else
                echo "Invalid destination. Please provide a valid device (e.g., /dev/sda)."
                exit 1
            fi
            ;;
        -h | --help)
            usage
            exit 0
            ;;
        *)
            echo "$1 argument is not valid"
            usage
            exit 1
    esac
    shift
done

# Validate arguments
check_args

# Confirm drive selection
echo "You have selected $destination for partition setup."
read -p "All data on $destination will be lost. Are you sure? (type yes to continue): " confirm
if [ -z "$confirm" ] || [ "$confirm" != "yes" ]; then
    echo "Operation canceled."
    exit 1
fi

# Unmount all partitions on the drive
umount "$destination"* > /dev/null 2>&1

# Write the partition table
echo "Setting up partition table on $destination..."
write_base_table "$destination"

echo "Partition setup completed successfully."
