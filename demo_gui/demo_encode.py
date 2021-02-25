import sys
import os
import time
import cv2
import numpy as np
from test import first_order, array2video
import csv

from PyQt5 import QtGui

from skimage.measure import compare_psnr
from skimage.measure import compare_ssim
from face_detection import cal_AKD

def get_filename(file_dir):
    base = os.path.basename(file_dir)
    filename = os.path.splitext(base)[0]
    return filename

def encode_aio(encode_video_dir):
    driving_video_filename = get_filename(driving_video_dir)

    a = first_order()
    a.load_encode_video(driving_video_dir)
    a.prepare_for_encode()

    driving_video_capture = cv2.VideoCapture()
    driving_video_capture.open(driving_video_dir)

    video_output = []
    curren_frame = 0
    psnr_sum = 0
    ssim_sum = 0
    frame_count = 0

    csvfile = open('./data/encode_{}.csv'.format(driving_video_filename), 'w', newline='')
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(["frame", "PSNR", "SSIM","AKD"])

    while(curren_frame<a.length):
        if(curren_frame%GAP == 0):
            a.set_encode_seg(curren_frame,GAP)
            a.prepare_for_gen()
        start_time = time.time()
        frame_g = a.generate_frame(curren_frame%GAP)
        video_output.append(frame_g)
        temp_image = np.require(frame_g, np.uint8, 'C')
        temp_image = QtGui.QImage(temp_image, 256, 256, QtGui.QImage.Format_RGB888)
        temp_image.save("./temp/temp.png", "png")
        gen_image = cv2.imread("./temp/temp.png")
        driving_video_capture.set(cv2.CAP_PROP_POS_FRAMES, curren_frame)
        success, frame = driving_video_capture.read()
        if success:
            psnr = compare_psnr(frame, gen_image)
            ssim = compare_ssim(frame, gen_image, multichannel=True)
            try:
                akd = cal_AKD(frame,gen_image)
            except:
                akd = 0.0
            psnr_sum += psnr
            ssim_sum += ssim
            status_text = "PSNR:{:.3} SSIM:{:.3}".format(psnr, ssim)
            csvwriter.writerow([curren_frame, psnr, ssim,akd])
            end_time = time.time()
            process_time = end_time-start_time
            curren_frame += 1
            frame_count += 1
            print("{} F/R:{:.3} PSNR:{:.3} SSIM:{:.3} AKD:{:.3}".format(curren_frame,1/process_time,psnr,ssim,akd))
    array2video(video_output, 30,"encode_{}.mp4".format(driving_video_filename))
    csvfile.close()
    print("encode {} finished".format(driving_video_filename))

#source_image_dir = sys.argv[1]
#driving_video_dir = sys.argv[2]
#generate_aio(source_image_dir,driving_video_dir)

filename = sys.argv[1]
GAP = int(sys.argv[2])
driving_video_dir = ".\\res\\{}.mp4".format(filename)
encode_aio(driving_video_dir)

