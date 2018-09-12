from django.http import StreamingHttpResponse
import cv2
from django.views.decorators import gzip
from darkflow.net.build import TFNet
import time
from rx import subjects
from rx.concurrency import NewThreadScheduler
import face_recognition
from threading import Lock
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Alarm

readyLk = Lock()
resultLk = Lock()
bombLk = Lock()

options_object = {
    "model": "cfg/yolov2-tiny.cfg",
    "load": "bin/yolov2-tiny.weights",
    "labels": "labels_object",
    "threshold": 0.5
}

channel_layer = get_channel_layer()

options_face = {
    "model": "cfg/tiny-yolo-face.cfg",
    "load": "bin/tiny-yolo-face.weights",
    "labels": "labels_face",
    "threshold": 0.5
}

tfnet_object = TFNet(options_object)
tfnet_face = TFNet(options_face)
resultF = ([], [])
ready = True
memo = []
channel_name = ''


def send(frame):
    global ready, resultF
    with readyLk:
        ready = False
    start = time.time()

    objects = tfnet_object.return_predict(frame)
    faces = tfnet_face.return_predict(frame)

    form_faces = list(
        map(
            lambda result: (result['topleft']['x'], result['topleft']['y'], result['bottomright']['x'], result['bottomright']['y']),
            faces))
    encodings = face_recognition.face_encodings(frame, form_faces)

    rec = 0
    for face in encodings:
        matches = face_recognition.compare_faces(memo, face, tolerance=0.35)
        if not any(matches):
            memo.append(face)
            rec += 1

    alarmc = '%d new in %d face' % (rec, len(faces))
    async_to_sync(channel_layer.send)(channel_name, {
        'type': 'send.alarm',
        'info': alarmc
    })
    Alarm.objects.create(content=alarmc)

    print(time.time() - start)
    with resultLk:
        resultF = (faces, objects)
    with readyLk:
        ready = True


obs = subjects.Subject()
obs.observe_on(NewThreadScheduler()).subscribe(on_next=send)


def stream():
    rtmp = "http://ivi.bupt.edu.cn/hls/cctv6hd.m3u8"
    stream = cv2.VideoCapture(rtmp)

    while True:
        frame = stream.read()[1]

        with readyLk:
            if ready:
                obs.on_next(frame)

        with resultLk:
            faces, objects = resultF

        for result in faces:
            drawLabel(frame,
                      result['label'] + '  ' + str(result['confidence']),
                      result['topleft']['x'], result['topleft']['y'],
                      result['bottomright']['x'], result['bottomright']['y'],
                      (5, 255, 5))

        for result in objects:
            drawLabel(frame,
                      result['label'] + '  ' + str(result['confidence']),
                      result['topleft']['x'], result['topleft']['y'],
                      result['bottomright']['x'], result['bottomright']['y'],
                      (255, 255, 5))

        jpeg = cv2.imencode('.jpg', frame)[1]
        bts = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + bts + b'\r\n\r\n')


def drawLabel(img, txt, l, t, r, b, color):
    cv2.putText(img, txt, (l, t + 20), cv2.FONT_HERSHEY_PLAIN, 2, color, 2)
    cv2.rectangle(img, (l, t), (r, b), color, 1)


@gzip.gzip_page
def cam(request):
    return StreamingHttpResponse(
        stream(), content_type="multipart/x-mixed-replace;boundary=frame")
