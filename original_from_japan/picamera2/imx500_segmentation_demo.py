import argparse
import sys
import time
from typing import Dict

import cv2
import numpy as np

from picamera2 import CompletedRequest, Picamera2
from picamera2.devices import IMX500
from picamera2.devices.imx500 import NetworkIntrinsics

COLOURS = np.loadtxt("assets/colours.txt")


def create_and_draw_masks(request: CompletedRequest):
    """Create masks from the output tensor and draw them on the main output image."""
    masks = create_masks(request)
    draw_masks(masks)


def create_masks(request: CompletedRequest) -> Dict[int, np.ndarray]:
    """Create masks from the output tensor, scaled to the ISP output."""
    res = {}
    np_outputs = imx500.get_outputs(metadata=request.get_metadata())
    input_w, input_h = imx500.get_input_size()
    if np_outputs is None:
        return res
    mask = np_outputs[0]
    found_indices = np.unique(mask)

    for i in found_indices:
        if i == 0:
            continue
        output_shape = [input_h, input_w, 4]
        colour = [(0, 0, 0, 0), COLOURS[int(i)]]
        colour[1][3] = 150  # update the alpha value here, to save setting it later
        overlay = np.array(mask == i, dtype=np.uint8)
        overlay = np.array(colour)[overlay].reshape(output_shape).astype(np.uint8)
        # No need to resize the overlay, it will be stretched to the output window.
        res[i] = overlay
    return res


def draw_masks(masks: Dict[int, np.ndarray]):
    """Draw the masks for this request onto the ISP output."""
    if not masks:
        return
    input_w, input_h = imx500.get_input_size()
    output_shape = [input_h, input_w, 4]
    overlay = np.zeros(output_shape, dtype=np.uint8)
    if masks:
        for v in masks.values():
            overlay += v
        # Set Alphas and overlay
        picam2.set_overlay(overlay)


def get_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, help="Path of the model",
                        default="/usr/share/imx500-models/imx500_network_deeplabv3plus.rpk")
    parser.add_argument("--fps", type=int, help="Frames per second")
    parser.add_argument("--print-intrinsics", action="store_true",
                        help="Print JSON network_intrinsics then exit")
    parser.add_argument("-i","--show-input-tensor", action="store_true", help="show input tensor")
    parser.add_argument("-x", "--input-tensor-scale", type=int, default=1, help="Display input tensor scale(x)")
    parser.add_argument("-n", "--no-preview", action="store_true", help="Preview off")
    parser.add_argument("-e", "--disable-ae", action="store_true", help="Disable Ae")
    parser.add_argument("-w", "--disable-awb", action="store_true", help="Disable Awb")
    return parser.parse_args()


if __name__ == "__main__":
    args = get_args()

    # This must be called before instantiation of Picamera2
    imx500 = IMX500(args.model)
    intrinsics = imx500.network_intrinsics
    if not intrinsics:
        intrinsics = NetworkIntrinsics()
        intrinsics.task = "segmentation"
    elif intrinsics.task != "segmentation":
        print("Network is not a segmentation task", file=sys.stderr)
        exit()

    # Override intrinsics from args
    for key, value in vars(args).items():
        if hasattr(intrinsics, key) and value is not None:
            setattr(intrinsics, key, value)

    # Defaults
    intrinsics.update_with_defaults()

    if args.print_intrinsics:
        print(intrinsics)
        exit()

    picam2 = Picamera2(imx500.camera_num)
    #config = picam2.create_preview_configuration(controls={'FrameRate': intrinsics.inference_rate}, buffer_count=12)
    config = picam2.create_preview_configuration(controls={"FrameRate": intrinsics.inference_rate,\
            "CnnEnableInputTensor": True if args.show_input_tensor else False, \
            "AeEnable": False if args.disable_ae else True, \
            "AwbEnable": False if args.disable_awb else True}, buffer_count=12)
    imx500.show_network_fw_progress_bar()
    #picam2.start(config, show_preview=True)
    picam2.start(config, show_preview=not args.no_preview)
    picam2.pre_callback = create_and_draw_masks

    #show input tensor prepare
    INPUT_TENSOR_SIZE = [0, 0]
    if args.show_input_tensor:
        err=0
        for _ in range(10):
            try:
                t = picam2.capture_metadata()["CnnInputTensorInfo"]
                network_name, width, height, num_channels = imx500._IMX500__get_input_tensor_info(t)
                break
            except KeyError:
                err=-1
        if err == 0:
            INPUT_TENSOR_SIZE = [height*args.input_tensor_scale, width*args.input_tensor_scale]
            cv2.startWindowThread()

    while True:
        #time.sleep(0.5)
        if args.show_input_tensor:
            try:
                input_tensor = picam2.capture_metadata()["CnnInputTensor"]
                if INPUT_TENSOR_SIZE != (0, 0):
                    #NORMAL WINDOW
                    cv2.namedWindow("Input Tensor", cv2.WINDOW_NORMAL)
                    cv2.imshow("Input Tensor",imx500.input_tensor_image(input_tensor))
                    cv2.resizeWindow("Input Tensor", *INPUT_TENSOR_SIZE)
                    #must be wait
                    cv2.waitKey(1)
            except KeyError:
                pass
        else:
            time.sleep(0.5)
