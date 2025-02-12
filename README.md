# IMX500 driver patch for enabling I2C read/write

## Pre Conditions
 
- RaspberryPi5 64 bit kernel
- Kernel source tree is already cloned.
    - Reference : https://www.raspberrypi.com/documentation/computers/linux_kernel.html#building

## Build Steps

1. Move to kernel code tree

    ```bash
    cd <kernel clone dir>/kernel
    ```

2. Copy build scripts and patch

    ```bash
    cp imx500_driver_for_i2c_read_write/src/* .
    ```

3. Apply patch

    ```bash
    git apply imx500_c_i2c_enable.patch
    ```

4. Build

    ```bash
    ./update_kernel.sh
    ./build_kernel.sh
    ```

5. Reboot

    ```bash
    sudo reboot
    ```

## Check v4l2-ctl

- Check if imx500_read_register and imx500_register_io are listed.

    ```bash
    v4l2-ctl -d /dev/v4l-subdev2 --list-ctrls | grep imx500
    ```

    ```bash
    imx500_inference_windows 0x00982900 (u32)    : min=0 max=4032 step=1 default=0 dims=[4] flags=has-payload, execute-on-write
    imx500_network_firmware_file_fd 0x00982901 (int)    : min=-1 max=2147483647 step=1 default=-1 value=0 flags=write-only, execute-on-write
    imx500_read_register 0x00982902 (int)    : min=0 max=65535 step=1 default=53314 value=53314 flags=execute-on-write
    imx500_register_io 0x00982903 (u32)    : min=0 max=4294967295 step=1 default=0 dims=[3] flags=has-payload
    ```

## Reference

- https://www.raspberrypi.com/documentation/computers/linux_kernel.html#building
