from PyQt5 import QtCore, QtGui, QtWidgets
from Ui_MainWindow import Ui_MainWindow
import Videobox
import sys
import numpy as np
import time

from test import first_order, array2video


class QmyWidget(QtWidgets.QMainWindow): 
    def __init__(self, parent=None):
        super().__init__(parent)        #调用父类构造函数，创建窗体
        self.ui=Ui_MainWindow()     #创建UI对象
        self.ui.setupUi(self)       #构造UI界面
        
        self.ui.image_open_pushButton.clicked.connect(self.load_source_image)
        self.ui.gv_open_pushButton.clicked.connect(self.load_drive_video)
        self.ui.generate_pushButton.clicked.connect(self.generate_video)
        
        self.dv_box = Videobox.VideoBox("")
        self.gv_box = Videobox.VideoBox("")
        
        self.ui.verticalLayout_3.insertWidget(0, self.dv_box, 4)
        self.ui.horizontalLayout_4.insertWidget(0, self.gv_box)
        
        self.gen_thread = GenThread()
        

    
    def load_source_image(self):
        directory = QtWidgets.QFileDialog.getOpenFileName(self,
              "getOpenFileName","./",
              "PNG File (*.png)") 
        print("source image", directory)
        temp_pixmap = QtGui.QPixmap(directory[0])
        self.ui.source_image_label.setPixmap(temp_pixmap)
        self.ui.image_lineEdit.setText(directory[0])
        
        a.load_source_image(directory[0])
        
        return
        
    def load_drive_video(self):
        directory = QtWidgets.QFileDialog.getOpenFileName(self,
              "getOpenFileName","./",
              "MP4 File (*.mp4)") 
        print("drive video", directory)
        self.dv_box.set_video(directory[0])
        self.dv_box.play()
        self.ui.dv_lineEdit.setText(directory[0])
        
        a.load_drive_video(directory[0])
        
        
    def generate_video(self):
        self.dv_box.reset()
        self.gv_box.reset()
        '''
        a.generate("1.mp4")
        self.gv_box.set_video("./temp/1.mp4")
        self.gv_box.play()
        self.dv_box.play()
        '''
        a.prepare_for_gen()
        
        self.gen_thread.trigger.connect(self.refresh_video)
        self.gen_thread.start()
        self.dv_box.play()
        
    def refresh_video(self, image, fps, status):
        if status == 1:
            self.gv_box.pictureLabel.setPixmap(image)
            self.ui.fps_label.setText("Generating@FPS:{:.4}".format(fps))
        else:
            print("finished")
            self.ui.fps_label.setText("Replay@FPS:{}".format(fps))
            self.gv_box.set_video("./temp/1.mp4")
            self.gv_box.play()

class GenThread(QtCore.QThread):
    trigger = QtCore.pyqtSignal((QtGui.QPixmap, float , int))

    def __int__(self, parent=None):
        # 初始化函数
        super(GenThread, self).__init__()

    def run(self):
        video_output = []
        curren_frame = 0
        time_per_frame = 1/a.fps
        while(curren_frame<a.length):
            start_time = time.time()
            
            frame = a.generate_frame(curren_frame)
            video_output.append(frame)
            temp_image = np.require(frame, np.uint8, 'C')
            temp_image = QtGui.QImage(temp_image, 256, 256, QtGui.QImage.Format_RGB888)
            temp_pixmap = QtGui.QPixmap.fromImage(temp_image)
            
            end_time = time.time()
            process_time = end_time-start_time
            frame_jumped = int(process_time/time_per_frame)
            curren_frame += frame_jumped
            self.trigger.emit(temp_pixmap, 1/process_time , 1)
            
        array2video(video_output, int(1/process_time),"1.mp4")
        self.trigger.emit(QtGui.QPixmap(), int(1/process_time), 0)
        
    
    
if  __name__ == "__main__":         #用于当前窗体测试
    a = first_order()
    
    app = QtWidgets.QApplication(sys.argv)    #创建GUI应用程序
    form=QmyWidget()                #创建窗体
    form.show()

    sys.exit(app.exec_())
