from django.shortcuts import render
from django.http import HttpResponse, StreamingHttpResponse
import numpy as np
import cv2
from django.views.decorators import gzip
from darkflow.net.build import TFNet
import time
from multiprocessing import Queue
from rx import subjects
from rx.concurrency import NewThreadScheduler
from threading import Thread,Lock
readyLk =Lock()
resultLk =Lock()
bombLk =Lock()

options = {
    "model": "cfg/yolov2-tiny.cfg",
    "load": "bin/yolov2-tiny.weights",
    "threshold": 0.3
}

tfnet = TFNet(options)

resultF = []

queue_che= Queue()

ready=True

bomb=False

def bomber():
    global bomb
    bomb=False
    time.sleep(0)
    with bombLk:
        bomb=True

def delayT():
    return lambda:time.sleep(0)

def send(frame):
    global ready,resultF
    with readyLk:
        ready=False

    thread = Thread(target = delayT())
    thread.start()

    start=time.time()
    results = tfnet.return_predict(frame)
    print(time.time()-start)
    with resultLk:
        resultF=results

    thread.join()

    with readyLk:
        ready=True


obs = subjects.Subject()
obs.observe_on(NewThreadScheduler()).subscribe(on_next=send)


def stream():
    rtmp = "http://183.251.61.207/PLTV/88888888/224/3221225925/index.m3u8"
    stream = cv2.VideoCapture(rtmp)
    thread = Thread(target = bomber)
    thread.start()
    flag=True
    while False:
        ret,frame=stream.read()
        if flag:
            obs.on_next(frame)
            flag=False
        queue_che.put(frame)
        with bombLk:
            if bomb:
                break

    while True:
        ret,fm0=stream.read()
        queue_che.put(fm0)
        frame=queue_che.get()

        with readyLk:
            if ready:
                obs.on_next(fm0)

        with resultLk:
            results=resultF
        for result in results:
            cv2.putText(frame,result['label']+'  '+str(result['confidence']),(result['topleft']['x'], result['topleft']['y']), cv2.FONT_HERSHEY_PLAIN, 2, (255,255,0), 2);

            cv2.rectangle(
                frame, (result['topleft']['x'], result['topleft']['y']),
                (result['bottomright']['x'], result['bottomright']['y']),
                (255, 255, 0), 1)

        ret, jpeg = cv2.imencode('.jpg', frame)
        bts = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + bts + b'\r\n\r\n')


@gzip.gzip_page
def cam(request):
    return StreamingHttpResponse(
        stream(), content_type="multipart/x-mixed-replace;boundary=frame")
