import numpy
import cv2
from head_pose import head_pose
from tqdm import tqdm

def get_seg_list(video_dir,threshold=15):
    driving_video_capture = cv2.VideoCapture()
    driving_video_capture.open(video_dir)
    seg_list = []
    current_seg_length = 0
    last_pose = None
    frame_count = int(driving_video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
    print("Analysing",frame_count,"frames")
    for i in tqdm(range(frame_count)):
        success, frame = driving_video_capture.read()
        if success:
            try:
                curr_pose = head_pose.get_rotation(frame)
            except:
                curr_pose = None
                print("face detection error")
            if last_pose == None:
                current_seg_length += 1
                last_pose = curr_pose
            elif curr_pose == None or head_pose.degree_diff(curr_pose,last_pose)>threshold:
                seg_list.append(current_seg_length)
                current_seg_length = 1
                last_pose = curr_pose
            else:
                current_seg_length += 1
                last_pose = curr_pose
    seg_list.append(current_seg_length)
    return seg_list

if __name__=="__main__":
    a = get_seg_list("./res/test02.mp4",20)
    print(a)