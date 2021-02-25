import numpy as np
from tensorflow.keras.models import load_model as load_model
import cv2

model = load_model("./res/model_v6_23.hdf5")
print("emotion detect ready")

def normalization(data):
    _range = np.max(data) - np.min(data)
    return (data - np.min(data)) / _range

def get_emotion_vector(face_image):
    face_image = cv2.resize(face_image, (48,48))
    face_image = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)
    face_image = np.reshape(face_image, [1, face_image.shape[0], face_image.shape[1], 1])
    predict_result = normalization(model.predict(face_image))
    return predict_result[0]

def get_emotion_distance(image1,image2):
    vector1 = get_emotion_vector(image1)
    vector2 = get_emotion_vector(image2)
    return np.linalg.norm(vector1-vector2)
    
if  __name__ == "__main__":
    image_a = cv2.imread("./res/10.png")
    image_b = cv2.imread("./res/test.png")
    print(get_emotion_distance(image_a,image_b))
