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
