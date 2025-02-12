import fcntl
import v4l2

READ_REGISTER_ID=0x00982902

ID_ADR=(0xd040, 0xd042, 0xd044, 0xd046, 0xd048, 0xd04a, 0xd04c, 0xd04e)

dev_path='/dev/v4l-subdev2'
dev=open(dev_path, 'rb+', buffering=0)
ctrl=v4l2.v4l2_control()
ctrl.id=READ_REGISTER_ID

ids=[0]*8
for i in range(8):
    ctrl.value=ID_ADR[i]
    #set address and read register
    fcntl.ioctl(dev, v4l2.VIDIOC_S_CTRL, ctrl)
    ids[i]=ctrl.value
#print(f"{ids[7]:04x}{ids[6]:04x}{ids[5]:04x}{ids[4]:04x}{ids[3]:04x}{ids[2]:04x}{ids[1]:04x}{ids[0]:04x}")
print(f"{ids[0]:04X}{ids[1]:04X}{ids[2]:04X}{ids[3]:04X}{ids[4]:04X}{ids[5]:04X}{ids[6]:04X}{ids[7]:04X}")

dev.close()
