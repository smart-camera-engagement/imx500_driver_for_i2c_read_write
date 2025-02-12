#
# IMX500 sensor register io script
# 2024/11/20
#
import os
import argparse
import fcntl
import v4l2
import sys
import ctypes

def hex_type(val):
    try:
        if val.startswith('0x') or val.startswith('0X'):
            return int(val, 16)
        else:
            return int(val)
    except ValueError:
        raise argparse.ArgumentTypeError(f"{val} is not hex or int value.")

def set_limit(data, max, min):
    if data > max:
        data = max
    if data < min:
        data = min
    return data

def print_data(ctrl, args, fp=None):
    c=ctrl.controls
    r=c[0].p_u32
    addr=r[0]&0x0000ffff
    bitw=r[0]>>16 & 0xff
    rw=r[0]>>24 & 0x1
    if args.little_endian:
        if bitw==16:
            data=(r[1]>>8&0x00ff)|(r[1]<<8&0xff00)
        elif bitw==32:
            data=(r[1]>>24&0x000000ff)|(r[1]>>8&0x0000ff00)|(r[1]<<8&0x00ff0000)|(r[1]<<24&0xff000000)
        else:
            data=r[1]
    else:
        data=r[1]
    mask=r[2]
    h='R' if rw ==0 else 'W'
    if fp:
        fp.write(f"{addr:08x}, {data:08x}\n")
    if bitw==8:
        print(f"{h}: address(h): {addr:08x}, data(h): {data:02x}, data(d): {data:3d}, bit width: {bitw:2d}")
    elif bitw==16:
        print(f"{h}: address(h): {addr:08x}, data(h): {data:04x}, data(d): {data:5d}, bit width: {bitw:2d}")
    else:
        print(f"{h}: address(h): {addr:08x}, data(h): {data:08x}, data(d): {data:10d}, bit width: {bitw:2d}")

def read_file(args):
    with open(args.input_file, "r") as fp:
        lines=fp.readlines()
        addrs=[]
        vals=[]
        for line in lines:
            items = line.split(", ")
            addrs.append(int(items[0], 16))
            vals.append(int(items[1], 16))
        dat_list=list(zip(addrs, vals))
    return dat_list

def print_args(args, verbose=False):
    if verbose:
        print('address', hex(args.address))
        print('bit-width', args.bit_width)
        print('mask', hex(args.mask))
        print('data', hex(args.data))
        print('write', args.write)
        print('number-of-bytes', args.number_of_bytes)
        print('input-file', args.input_file)
        print('output-file', args.output_file)
        print('little-endian', args.little_endian)

def check_args(args):
    args.address=set_limit(args.address, 0xffff, 0x0000)
    # width=8,16,32
    args.bit_width=set_limit((args.bit_width//8)*8, 32, 8)
    args.mask=set_limit(args.mask, 0xffffffff, 0x00000000)
    args.data=set_limit(args.data, 0xffffffff, 0x00000000)
    # min=1,2,4 max=2048 bytes
    args.number_of_bytes=set_limit(args.number_of_bytes, 2048, args.bit_width//8)
    # output format is 32bit, big-endian fixed
    if args.output_file != "":
            args.bit_width=32
            args.mask=0
            args.little_endian=False
    # input exists?
    if args.input_file != "":
        if not os.path.isfile(args.input_file):
            print("file ",args.input_file," not not found.")
            sys.exit(1)
        args.bit_width=32
        args.mask=0
        args.little_endian=False
    return args

def get_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--address', type=hex_type, default=0, help='address, default=0 ex)0xd080')
    parser.add_argument('-b', '--bit-width', type=int, default=8, help='bit width 8/16/32 ,default=8')
    parser.add_argument('-m', '--mask', type=hex_type, default=0, help='mask, default=NoMask ex)0x00ff')
    parser.add_argument('-d', '--data', type=hex_type, default=0, help='write data, default=0 ex)123 or 0xcf')
    parser.add_argument('-w', '--write', action="store_true", help='enable write, default=False')
    parser.add_argument('-n', '--number-of-bytes', type=int, default=1, help='read bytes, default=1, max=2048')
    parser.add_argument('-i', '--input-file', type=str, default="", help='input file name <32bit,big-endian>')
    parser.add_argument('-o', '--output-file', type=str, default="", help='output file name <32bit,big-endian>')
    parser.add_argument('-l', '--little-endian', action="store_true", help='print little endian like')
    return parser.parse_args()

def set_params(args, ID):
    # r[0] addresss[0:15], bit_width[23:16], r(0)/w(1)[24] 
    # r[1] data[0:31]
    # r[2] mask[0:31]
    r = (ctypes.c_uint32 * 3)()
    w = 1 if args.write else 0
    r[0] = args.address | args.bit_width<<16 |  w<<24
    r[1] = args.data
    r[2] = args.mask
    #c
    c = (v4l2.v4l2_ext_control * 1)()
    c[0].p_u32 = r
    c[0].id = ID
    c[0].size = 16
    #ctrl
    ctrl=v4l2.v4l2_ext_controls()
    ctrl.count = 1
    ctrl.controls = c
    return ctrl

def main():
    # args
    args = get_args()
    check_args(args)
    print_args(args)

    # read file
    data_list=[]
    if args.input_file != "":
        data_list=read_file(args)
        args.address=data_list[0][0]
        args.data=data_list[0][1]
        args.number_of_bytes=len(data_list)*(args.bit_width//8)

    # set parameter
    REGISTER_IO_ID=0x00982903
    ctrl=set_params(args, REGISTER_IO_ID)

    #open device
    dev_path='/dev/v4l-subdev2'
    try:
        dev=open(dev_path, 'rb+', buffering=0)
    except OSError as e:
        print(f"Error :{e}")
        sys.exit(1)

    #open write file
    if args.output_file != "":
        fp=open(args.output_file, mode="w")
    else:
        fp=None
    #read/write
    try:
        i=0
        while i<args.number_of_bytes//(args.bit_width//8):
            # imx500 io
            fcntl.ioctl(dev, v4l2.VIDIOC_S_EXT_CTRLS, ctrl)
            print_data(ctrl, args, fp)
            # address increment
            i=i+1
            if args.input_file != "":
                # from file
                if i < len(data_list):
                    args.address=data_list[i][0]
                    args.data=data_list[i][1]
            else:
                # count up
                args.address=args.address+(args.bit_width//8)
            # set ctrl
            ctrl=set_params(args, REGISTER_IO_ID)
    except OSError as e:
        print(f"Error :{e}")
        sys.exit(1)
    finally:
        # close file
        if fp:
            fp.close()
        #close device
        dev.close()

if __name__=="__main__":
    main()