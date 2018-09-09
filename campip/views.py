from django.shortcuts import render
from django.http import HttpResponse, StreamingHttpResponse
import numpy as np
import cv2
from django.views.decorators import gzip
from darkflow.net.build import TFNet
import time

options = {"model": "cfg/yolo.cfg", "load": "bin/yolo.weights", "threshold": 0.2}

tfnet = TFNet(options)

def stream():
    rtmp= "http://183.252.176.10/PLTV/88888888/224/3221225922/index.m3u8"
    stream = cv2.VideoCapture(rtmp)
    while True:
        ret,frame = stream.read()
        results = tfnet.return_predict(frame)
        for result in results:
            cv2.rectangle(frame,(result['topleft']['x'],result['topleft']['y']),(result['bottomright']['x'],result['bottomright']['y']),(255,255,0),1)
        ret,jpeg = cv2.imencode('.jpg',frame)
        frame=jpeg.tobytes()
        yield(b'--frame\r\n'
        b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        time.sleep(1)

@gzip.gzip_page
def cam(request):
    return StreamingHttpResponse(stream(),content_type="multipart/x-mixed-replace;boundary=frame")

