import fcntl
import v4l2
import sys

def parse_number(value):
    try:
        return int(value)
    except ValueError:
        try:
            return int(value,16)
        except ValueError:
            raise ValueError(f"wrong value:{value}")

def main():
    try:
        addr=parse_number(sys.argv[1])

        READ_REGISTER_ID=0x00982902
        dev_path='/dev/v4l-subdev2'
        dev=open(dev_path, 'rb+', buffering=0)
        ctrl=v4l2.v4l2_control()
        ctrl.id=READ_REGISTER_ID
    
        ctrl.value=addr
        #set address and read register
        fcntl.ioctl(dev, v4l2.VIDIOC_S_CTRL, ctrl)
        #print(f"ADDRESS:{addr:04x}, VAL(d):{ctrl.value:5}, VAL(h):{ctrl.value:04x}")
        print(f"ADDRESS:{addr:04X}, VAL(d):{ctrl.value:5}, VAL(h):{ctrl.value:04X}")
    
        dev.close()
    except ValueError as e:
        print(e)

if __name__=="__main__":
    main()
