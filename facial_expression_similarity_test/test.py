import dlib         
import math 
import cv2
import numpy as np  

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('./shape_predictor_68_face_landmarks.dat')
facerec = dlib.face_recognition_model_v1("./dlib_face_recognition_resnet_model_v1.dat")


def get_euclidean_distance(feature_1, feature_2):
    feature_1 = np.array(feature_1)
    feature_2 = np.array(feature_2)
    dist = np.sqrt(np.sum(np.square(feature_1 - feature_2)))
    return dist

def cal_face_difference(image1,image2):
    img1_gray = cv2.cvtColor(image1, cv2.COLOR_RGB2GRAY)
    img2_gray = cv2.cvtColor(image2, cv2.COLOR_RGB2GRAY)

    faces1 = detector(img1_gray, 0)
    faces2 = detector(img2_gray, 0)

    points1 = predictor(image1, faces1[0])
    points2 = predictor(image2, faces2[0])

    feature1 = facerec.compute_face_descriptor(image1, points1)
    feature2 = facerec.compute_face_descriptor(image2, points2)

    dist = get_euclidean_distance(feature1,feature2)
    return dist


video1 = cv2.VideoCapture('01.mp4')
video2 = cv2.VideoCapture('01_copy.mp4')

frame_count = 0
total_frame_diff = 0

while True:
    ret1, frame1 = video1.read()
    ret2, frame2 = video2.read()
    if ret1 is False or ret2 is False:
        break
    print(frame_count)
    frame_count += 1
    total_frame_diff += cal_face_difference(frame1,frame2)
print("Average",total_frame_diff/frame_count)


'''
01.mp4 - Driving Video
01_copy.mp4 - Copy of Driving Video - 0

02.mp4 - another video containing facial expression - 0.8356

10.png - the first frame of Driving Video - 0.2417
10.mp4 - Generated Video using 10.png

11.png - a random frame of Driving Video
11.mp4 - Generated Video using 11.png - 0.2876

20.png - another face photo
20.mp4 - Generated Video using 20.png - 0.8387


http://dlib.net/face_recognition.py.html
'''