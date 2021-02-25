import imageio
from demo import load_checkpoints, prepare_for_decode, make_animation_frame_decode
from skimage.transform import resize
from skimage import img_as_ubyte
import sys
from test import array2video

filename = sys.argv[1]

# load pretrained network
print("loading pretraind network")
generator, kp_detector = load_checkpoints(config_path='./config/vox-256.yaml', 
                            checkpoint_path='./res/vox-cpk.pth.tar',cpu=False)
print("ok")

# open encoded file
fov_file = open("./encode/{}.foe".format(filename),"rb")
video_output = []
current_frame = 0
while True:
    ref_length_b = fov_file.read(4)
    if not ref_length_b:
        break
    ref_length = int.from_bytes(ref_length_b, "big")
    print("ref length:",ref_length)
    # load source image
    source_image_length_b = fov_file.read(4)
    source_image_length = int.from_bytes(source_image_length_b, "big")
    print("source image length:",source_image_length)
    source_image_b = fov_file.read(source_image_length)
    source_image = imageio.imread(source_image_b,"jpg")
    source_image = resize(source_image, (256, 256))[..., :3]

    source, kp_source = prepare_for_decode(source_image, generator, kp_detector)

    for i in range(ref_length):
        kp_norm_b = fov_file.read(240)
        if not kp_norm_b:
            break
        frame = make_animation_frame_decode(kp_norm_b,source,kp_source, generator, kp_detector)
        video_output.append(frame)
        print(current_frame)
        current_frame += 1
imageio.mimsave('./temp/{}_decode.mp4'.format(filename), video_output, fps=30)

# load 