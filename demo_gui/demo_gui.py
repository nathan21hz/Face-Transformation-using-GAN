from PyQt5 import QtCore, QtGui, QtWidgets
from Ui_MainWindow import Ui_MainWindow
import sys
import numpy as np
import time
import cv2
import face_detection
from emotion import emotion_detect
from head_pose import head_pose

from test import first_order, array2video

def get_euclidean_distance(feature_1, feature_2):
    feature_1 = np.array(feature_1)
    feature_2 = np.array(feature_2)
    dist = np.sqrt(np.sum(np.square(feature_1 - feature_2)))
    return dist

class QmyWidget(QtWidgets.QMainWindow): 
    def __init__(self, parent=None):
        super().__init__(parent)        #调用父类构造函数，创建窗体
        self.ui=Ui_MainWindow()     #创建UI对象
        self.ui.setupUi(self)       #构造UI界面
        
        self.ui.image_open_pushButton.clicked.connect(self.load_source_image)
        self.ui.gv_open_pushButton.clicked.connect(self.load_drive_video)
        self.ui.generate_pushButton.clicked.connect(self.generate_video)
        
        self.driving_video = {}

        self.gen_thread = GenThread()
        
    
    def load_source_image(self):
        global original_image_vector
        global original_image_rotation
        original_image_rotation = []
        directory = QtWidgets.QFileDialog.getOpenFileNames(self,
              "getOpenFileName","./",
              "PNG File (*.png)") 
        print("source image", directory)
        used_image_dir = directory[0][0]
        a.load_source_image(used_image_dir)
        cv2_original_image = cv2.imread(used_image_dir)
        original_image_vector = face_detection.get_feature_vector(cv2_original_image)
        self.ui.image_lineEdit.setText(used_image_dir)
        
        image_label_list = [
            self.ui.source_image_label,
            self.ui.source_image_label_2,
            self.ui.source_image_label_3, 
            self.ui.source_image_label_4
        ]
        for index, image_dir in enumerate(directory[0]):
            temp_pixmap = QtGui.QPixmap(image_dir).scaled(QtCore.QSize(128, 128))
            image_label_list[index].setPixmap(temp_pixmap)
            cv2_original_image = cv2.imread(image_dir)
            original_image_rotation.append(head_pose.get_ratation(cv2_original_image))
        print(original_image_rotation)
        return
        
    def load_drive_video(self):
        directory = QtWidgets.QFileDialog.getOpenFileName(self,
              "getOpenFileName","./",
              "MP4 File (*.mp4)") 
        print("drive video", directory)
        self.driving_video["dir"] = directory[0]
        if  self.driving_video["dir"] != "":
            self.ui.dv_lineEdit.setText(self.driving_video["dir"])
            a.load_drive_video(self.driving_video["dir"])
            
            driving_video_capture = cv2.VideoCapture()
            driving_video_capture.open(self.driving_video["dir"])
            fps = driving_video_capture.get(cv2.CAP_PROP_FPS)
            self.driving_video["fps"] = fps
            success, frame = driving_video_capture.read()
            if success:
                height, width = frame.shape[:2]
                if frame.ndim == 3:
                    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                elif frame.ndim == 2:
                    rgb = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)

                temp_image = QtGui.QImage(rgb.flatten(), width, height, QtGui.QImage.Format_RGB888)
                temp_pixmap = QtGui.QPixmap.fromImage(temp_image)
                self.ui.driving_video_label.setPixmap(temp_pixmap)
                driving_video_capture.release()
        
    def generate_video(self):
        a.prepare_for_gen()
        
        self.gen_thread.trigger.connect(self.refresh_video)
        self.gen_thread.start()
        
    def refresh_video(self, generated_image, griving_image, fps, dist, emo_dist, best_img, status):
        image_label_list = [
            self.ui.source_image_label,
            self.ui.source_image_label_2,
            self.ui.source_image_label_3, 
            self.ui.source_image_label_4
        ]
        if status == 1:
            self.ui.generated_video_label.setPixmap(generated_image)
            self.ui.driving_video_label.setPixmap(griving_image)
            for ilable in image_label_list:
                ilable.setLineWidth(0)
            image_label_list[best_img].setLineWidth(4)
            if dist<0.6:
                self.ui.fps_label.setText("Generating@FPS:{:.4} Face:{:.3}(same) Exp:{:.3}".format(fps, dist, emo_dist))
            else:
                self.ui.fps_label.setText("Generating@FPS:{:.4} Face:{:.3}(diff) Exp:{:.3}".format(fps, dist, emo_dist))
        else:
            print("finished")
            self.ui.fps_label.setText("Replay@FPS:{} AvgDist:{:.3}".format(fps, dist))


class GenThread(QtCore.QThread):
    trigger = QtCore.pyqtSignal((QtGui.QPixmap, QtGui.QPixmap, float, float, float ,int , int))

    def __int__(self, parent=None):
        # 初始化函数
        super(QtCore.QThread, self).__init__()

    def run(self):
        driving_video_capture = cv2.VideoCapture()
        driving_video_capture.open(a.driving_video_path)
        video_output = []
        curren_frame = 0
        dist_sum = 0
        
        while(curren_frame<a.length):
            start_time = time.time()
            
            frame = a.generate_frame(curren_frame)
            video_output.append(frame)
            temp_image = np.require(frame, np.uint8, 'C')
            temp_image = QtGui.QImage(temp_image, 256, 256, QtGui.QImage.Format_RGB888)
            temp_pixmap = QtGui.QPixmap.fromImage(temp_image)
            
            temp_image.save("./temp/temp.png", "png")
            
            #Face recognition
            emotion_dist = 0
            dist = 0
            #'''
            gen_image = cv2.imread("./temp/temp.png")
            temp_feature = face_detection.get_feature_vector(gen_image)
            dist = face_detection.get_euclidean_distance(original_image_vector, temp_feature)
            #'''
            dist_sum += dist
            
            driving_video_capture.set(cv2.CAP_PROP_POS_FRAMES, curren_frame)
            success, frame = driving_video_capture.read()
            if success:
                height, width = frame.shape[:2]
                if frame.ndim == 3:
                    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                elif frame.ndim == 2:
                    rgb = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)

                dv_image = QtGui.QImage(rgb.flatten(), width, height, QtGui.QImage.Format_RGB888)
                dv_pixmap = QtGui.QPixmap.fromImage(dv_image)
            
            #head pose test
            best_original_img = 0
            '''
            driving_video_rotation = head_pose.get_ratation(frame)
            rotataions = []
            for r in original_image_rotation:
                rotataions.append(head_pose.degree_diff(r, driving_video_rotation))
            #print(rotataions)
            best_original_img = np.argmin(rotataions)
            #'''
            
            #Expression test
            emotion_dist = emotion_detect.get_emotion_distance(frame, gen_image)
            
            end_time = time.time()
            process_time = end_time-start_time
            curren_frame += 3
            self.trigger.emit(temp_pixmap, dv_pixmap, 1/process_time, dist, emotion_dist, best_original_img , 1)
            
        array2video(video_output, round(1/process_time),"1.mp4")
        self.trigger.emit(QtGui.QPixmap(), QtGui.QPixmap(),  round(1/process_time), dist_sum/len(video_output), 0, 0, 0)
    
    
if  __name__ == "__main__":         #用于当前窗体测试
    a = first_order()
    
    original_image_vector = None
    original_image_rotation = []
    
    
    app = QtWidgets.QApplication(sys.argv)    #创建GUI应用程序
    form=QmyWidget()                #创建窗体
    form.show()

    sys.exit(app.exec_())
