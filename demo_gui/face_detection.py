import dlib
import cv2
import numpy as np  

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('./res/shape_predictor_68_face_landmarks.dat')
facerec = dlib.face_recognition_model_v1("./res/dlib_face_recognition_resnet_model_v1.dat")
print("face detection module ready")

def get_euclidean_distance(feature_1, feature_2):
    feature_1 = np.array(feature_1)
    feature_2 = np.array(feature_2)
    dist = np.sqrt(np.sum(np.square(feature_1 - feature_2)))
    return dist

def get_feature_vector(image):
    image_gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    faces = detector(image_gray, 0)
    points = predictor(image, faces[0])
    feature = facerec.compute_face_descriptor(image, points)
    return feature

def get_feature_vector_data(image):
    image_gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    faces = detector(image_gray, 0)
    points = predictor(image, faces[0])
    feature = facerec.compute_face_descriptor(image, points)
    return feature

def cal_AKD(image1,image2):
    image1_gray = cv2.cvtColor(image1, cv2.COLOR_RGB2GRAY)
    image2_gray = cv2.cvtColor(image2, cv2.COLOR_RGB2GRAY)
    face1 = detector(image1_gray, 1)[0]
    face2 = detector(image2_gray, 1)[0]
    points1 = np.matrix([[p.x, p.y] for p in predictor(image1, face1).parts()])
    points2 = np.matrix([[p.x, p.y] for p in predictor(image2, face2).parts()])
    #points1 =np.matrix([[p.x, p.y] for p in predictor(img_rd, faces[i]).parts()])
    #print (points1[0].top())
    kd = np.linalg.norm(points1-points2,axis=1)
    akd = np.average(kd)
    return akd

if __name__ == "__main__":
    img1 = cv2.imread("./res/10.png")
    img2 = cv2.imread("./res/102.png")
    a = cal_AKD(img1,img2)
    print(a)
