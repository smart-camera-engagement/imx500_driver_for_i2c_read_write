import fcntl
import v4l2

READ_REGISTER_ID=0x00982902

WBG_R=0xd804
WBG_GR=0xd806
WBG_GB=0xd808
WBG_B=0xd80a

dev_path='/dev/v4l-subdev2'
dev=open(dev_path, 'rb+', buffering=0)
ctrl=v4l2.v4l2_control()
ctrl.id=READ_REGISTER_ID

gains=[0]*4
while True:
    for i in range(4):
        if i==0:
            ctrl.value=WBG_R
        elif i==1:
            ctrl.value=WBG_GR
        elif i==2:
            ctrl.value=WBG_GB
        else:
            ctrl.value=WBG_B
        #set address and read register
        fcntl.ioctl(dev, v4l2.VIDIOC_S_CTRL, ctrl)
        gains[i]=ctrl.value
    #print("R:",gains[0]/256,",GR:",gains[1]/256,",GB:",gains[2]/256,",B:",gains[3]/256)
    print(f"R={gains[0]/256:.3f}, GR={gains[1]/256:.3f}, GB={gains[2]/256:.3f}, B={gains[3]/256:.3f}")

dev.close()
