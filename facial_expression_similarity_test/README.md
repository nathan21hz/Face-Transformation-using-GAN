# Facial expression similarity test

### Method
For each frame in two videos, detect 68 face landmarks. And then calculate the euclidean distance of two corresponding landmarks.

( The trained model of face landmark detection can be got from http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2 )

### Files used in comparison
| File Name | Description |
| --- | --- |
| 01.mp4 | Driving Video |
| 01_copy.mp4 | Copy of Driving Video |
| 02.mp4 | another video containing facial expression|
| 10.png | the first frame of Driving Video |
| 10.mp4 | Generated Video using 10.png |
| 11.png | a random frame of Driving Video |
| 11.mp4 | Generated Video using 11.png |
| 20.png | another face photo |
| 20.mp4 | Generated Video using 20.png |

## Result
| Video1  | Video2  | Average Frame Distance  |  Average Landmark Distance |
| ------------ | ------------ | ------------ | ------------ |
|01.mp4 | 01_copy.mp4 |     0.0 |   0.0 |
|01.mp4 | 02.mp4      | 2763.18 | 40.62 |
|01.mp4 | 10.mp4      |  108.64 |  1.60 |
|01.mp4 | 11.mp4      |  291.04 |  4.28 |
|01.mp4 | 20.mp4      |  383.53 |  5.64 |