import imageio
from skimage.transform import resize
from demo import make_animation, prepare_for_gen, make_animation_frame
from skimage import img_as_ubyte
import warnings
import os
warnings.filterwarnings("ignore")

def get_filename(file_dir):
    base = os.path.basename(file_dir)
    filename = os.path.splitext(base)[0]
    return filename

class first_order():
    def __init__(self, parent=None):
        self.source_image = None
        self.source_image_path = ""
        self.driving_video = []
        self.encode_video = []
        self.driving_video_path = ""
        self.fps = 0
        self.generator = None
        self.kp_detector = None
        self.source = None
        self.driving = None
        self.kp_source = None
        self.kp_driving_initial = None
        self.length = 0
        self.encode = False
        self.encoded_file = None
        
        
        self.load_pretrained_network()
        print("ready")
        
    def load_source_image(self, path=""):
        print("loading image")
        self.source_image_path = path
        self.source_image = imageio.imread(path)
        self.source_image = resize(self.source_image, (256, 256))[..., :3]
        print(type(self.source_image))
        print("ok")
        
    def load_drive_video(self, path=""):
        print("loading driving video")
        self.driving_video_path = path
        reader = imageio.get_reader(path)
        self.fps = reader.get_meta_data()['fps']
        self.driving_video = []
        
        try:
            for im in reader:
                self.driving_video.append(im)
        except RuntimeError:
            pass
        reader.close()
        self.length = len(self.driving_video)
        self.driving_video = [resize(frame, (256, 256))[..., :3] for frame in self.driving_video]
        print("ok")

    def load_encode_video(self, path=""):
        print("loading video")
        self.driving_video_path = path
        reader = imageio.get_reader(path)
        self.fps = reader.get_meta_data()['fps']
        self.encode_video = []
        
        try:
            for im in reader:
                self.encode_video.append(im)
        except RuntimeError:
            pass
        reader.close()
        self.length = len(self.encode_video)
        self.encode_video = [resize(frame, (256, 256))[..., :3] for frame in self.encode_video]
        print("ok")

    def set_encode_seg(self,offset=0,length=30):
        print("cut segment")
        self.driving_video = self.encode_video[offset:offset+length]
        self.source_image = self.driving_video[0]
        self.add_reference_frame(length,self.source_image)
        pass
        
    def load_pretrained_network(self, path=""):
        print("loading pretraind network")
        from demo import load_checkpoints
        self.generator, self.kp_detector = load_checkpoints(config_path='./config/vox-256.yaml', 
                                    checkpoint_path='./res/vox-cpk.pth.tar',cpu=False)
        print("ok")
        
    def generate(self, filename):
        print("generating")
        predictions = make_animation(
            self.source_image, 
            self.driving_video, 
            self.generator, 
            self.kp_detector, 
            relative=True,
            cpu=False
        )
        print("saving")
        #save resulting video
        imageio.mimsave('./temp/'+filename, [img_as_ubyte(frame) for frame in predictions], fps=self.fps)
    
    def prepare_for_gen(self):
        self.source, self.driving, self.kp_source, self.kp_driving_initial = prepare_for_gen(self.source_image, 
            self.driving_video, 
            self.generator, 
            self.kp_detector
        )

    def prepare_for_encode(self):
        filename = get_filename(self.driving_video_path)
        self.encoded_file = open("./encode/{}.foe".format(filename),"wb")
        self.encode = True

    def add_reference_frame(self,ref_length,frame):
        self.encoded_file.write(ref_length.to_bytes(4,"big"))
        jpg_b = imageio.imwrite("<bytes>",frame,format="jpg")
        source_image_size = len(jpg_b)
        print(source_image_size)
        self.encoded_file.write(source_image_size.to_bytes(4,"big"))
        self.encoded_file.write(jpg_b)
        return True

    def generate_frame(self, frame_idx):
        frame,kp_norm_b = make_animation_frame(frame_idx, self.source, self.driving, self.kp_source, self.kp_driving_initial, self.generator,  self.kp_detector)
        if not self.encode:
            return frame
        else:
            self.encoded_file.write(kp_norm_b)
            return frame


        
def array2video(video, fps, filename):
    imageio.mimsave('./temp/'+filename, video, fps=fps)
