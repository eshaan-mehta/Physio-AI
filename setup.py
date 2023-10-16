import cv2 as cv
from ultralytics import YOLO
from torch import backends, cuda

from os import remove
from numpy import arctan2, pi
import matplotlib.pyplot as plt


WINDOW_NAME = "Physiotherapy Exercise Analyst"

#select device for model
if backends.cudnn.is_available():
    device = "cudnn"
if backends.mps.is_available():
    device = "mps" 
if cuda.is_available():
    device = "cuda"
else:
    device = "cpu"
print(device)

capture = cv.VideoCapture(0)
model = YOLO("yolov8s-pose.pt").to(device) #load model to available device

#keypoints numbers
#0 = nose
#1 = left-eye
#2 = right-eye
#3 = left-ear
#4 = right-ear
#5 = left-shoulder
#6 = right-shoulder
#7 = left-elbow
#8 = right-elbow
#9 = left-wrist
#10 = right-wrist
#11 = left-hip
#12 = right-hip
#13 = left-knee
#14 = right-knee
#15 = left-ankle
#16 = right-ankle