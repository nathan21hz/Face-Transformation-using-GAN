import dlib         
import math 
import cv2          

# Dlib 检测器和预测器
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('./shape_predictor_68_face_landmarks.dat')

def cal_face_difference(image1,image2):
    img1_gray = cv2.cvtColor(image1, cv2.COLOR_RGB2GRAY)
    img2_gray = cv2.cvtColor(image2, cv2.COLOR_RGB2GRAY)

    faces1 = detector(img1_gray, 0)
    faces2 = detector(img2_gray, 0)

    points1 = predictor(image1, faces1[0]).parts()
    points2 = predictor(image2, faces2[0]).parts()

    DISTANCE_ERROR = 0

    for i in range(len(points1)):
        dist = math.sqrt((points1[i].x-points2[i].x)**2 + (points1[i].y-points2[i].y)**2)
        DISTANCE_ERROR += dist
    #print(DISTANCE_ERROR)
    return DISTANCE_ERROR, DISTANCE_ERROR/len(points1)


img1_rd = cv2.imread("test.png")

img2_rd = cv2.imread("test.png")

video1 = cv2.VideoCapture('01.mp4')
video2 = cv2.VideoCapture('11.mp4')

frame_count = 0
total_frame_diff = 0
total_point_diff = 0

while True:
    ret1, frame1 = video1.read()
    ret2, frame2 = video2.read()
    if ret1 is False or ret2 is False:
        break
    a, b = cal_face_difference(frame1,frame2)
    total_frame_diff += a
    total_point_diff += b
    frame_count += 1
print("Average Frame Diff",total_frame_diff/frame_count,"\n","Average Point Diff",total_point_diff/frame_count)


'''
01.mp4 - Driving Video
01_copy.mp4 - Copy of Driving Video

02.mp4 - another video containing facial expression

10.png - the first frame of Driving Video
10.mp4 - Generated Video using 10.png

11.png - a random frame of Driving Video
11.mp4 - Generated Video using 11.png

20.png - another face photo
20.mp4 - Generated Video using 20.png

Video1  Video2         Frame     Point

01.mp4  01_copy.mp4      0.0       0.0
01.mp4  02.mp4       2763.18     40.62
01.mp4  10.mp4        108.64      1.60
01.mp4  11.mp4        291.04      4.28
01.mp4  20.mp4        383.53      5.64

'''