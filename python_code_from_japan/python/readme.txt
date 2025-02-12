How To Use

1. start rpicam or picamera2

1,1.rpicam
$ rpicam-hello -t 0 --post-process-file  /usr/share/rpi-camera-assets/imx500_mobilenet_ssd.json

1.2.picamera2
$ python imx500_classification_demo.py --model /usr/share/imx500-models/imx500_network_efficientnet_bo.rpk -i -n

2. imx500_read_register
usage: imx500_reg_io.py [-h] [-a ADDRESS] [-b BIT_WIDTH] [-m MASK] [-d DATA]
                        [-w] [-n NUMBER_OF_BYTES] [-i INPUT_FILE]
                        [-o OUTPUT_FILE] [-l]
options:
  -h, --help            
        show this help message and exit
  -a ADDRESS, --address ADDRESS address
        default=0 ex)0xd080
  -b BIT_WIDTH, --bit-width BIT_WIDTH
        bit width 8/16/32 ,default=8
  -m MASK, --mask MASK
        mask, default=NoMask ex)0x00ff
  -d DATA, --data DATA
        write data, default=0 ex)123 or 0xcf
  -w, --write
        enable write, default=False
  -n NUMBER_OF_BYTES, --number-of-bytes NUMBER_OF_BYTES
        read bytes, default=1, max=2048
  -i INPUT_FILE, --input-file INPUT_FILE
        input file name <32bit,big-endian>
  -o OUTPUT_FILE, --output-file OUTPUT_FILE
        output file name <32bit,big-endian>
  -l, --little-endian
        print little endian like

examples:
1.read the register value of the address
$ python imx500_reg_io.py -a 0xd000

2.read the register value of the address in 16-bit width
$ python imx500_reg_io.py -a 0xd000 -b 16

3.read the register values of the sequential addresses in 32-bit width
$ python imx500_reg_io.py -a 0xd000 -n 12 -b 32
```
4.write the register value of the address
$ python imx500_reg_io.py -a 0xd000 -d 0x10 -w

5.write the register value of the address with the mask value
$ python imx500_reg_io.py -a 0xd000 -d 0x0f -m 0x02 -w


EOF