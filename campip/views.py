from django.http import StreamingHttpResponse, HttpResponse
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

options_object = {
    "model": "cfg/yolov2.cfg",
    "load": "bin/yolov2.weights",
    "labels": "labels_object",
    "threshold": 0.5
}

channel_layer = get_channel_layer()

# options_face = {
#     "model": "cfg/tiny-yolo-face.cfg",
#     "load": "bin/tiny-yolo-face.weights",
#     "labels": "labels_face",
#     "threshold": 0.5
# }

readyLk = Lock()
readydecLk = Lock()
resultLk = Lock()
refreshLk = Lock()
tfnet_object = TFNet(options_object)
# tfnet_face = TFNet(options_face)
boxes_track = {}
ready = True
ready_dec = True
memo = []
channel_name = ''
trackers = {}
labels = {}
confidences = {}
refreshFlag = True
resize_rate = 1
unique_id = 0

# objects = tfnet_object.return_predict(frame)

# faces=[]

# form_faces = list(
#     map(
#         lambda result: (result['topleft']['x'], result['topleft']['y'], result['bottomright']['x'], result['bottomright']['y']),
#         faces))
# encodings = face_recognition.face_encodings(frame, form_faces)

# rec = 0
# for face in encodings:
#     matches = face_recognition.compare_faces(memo, face, tolerance=0.5)
#     if not any(matches):
#         memo.append(face)
#         rec += 1

# alarmc = '%d new in %d face' % (rec, len(faces))
# async_to_sync(channel_layer.send)(channel_name, {
#     'type': 'send.alarm',
#     'info': alarmc
# })
# Alarm.objects.create(content=alarmc)


def detect(frame):
    global labels, confidences, trackers, ready_dec, remain_record, unique_id
    start = time.time()
    with readydecLk:
        ready_dec = False
    remain_record = time.time()
    small = cv2.resize(frame, (0, 0), fx=resize_rate, fy=resize_rate)
    result_detect = tfnet_object.return_predict(frame)

    for result in result_detect:
        # tracker = cv2.TrackerCSRT_create()
        box=(result['topleft']['x'] * resize_rate, result['topleft']['y'] * resize_rate, result['bottomright']['x'] * resize_rate - result['topleft']['x'] * resize_rate, result['bottomright']['y'] * resize_rate - result['topleft']['y'] * resize_rate)
        tracker = cv2.TrackerKCF_create()
        tracker.init(small, box)
        trackers[unique_id] = tracker
        labels[unique_id]=result['label']
        confidences[unique_id]=result['confidence']
        unique_id += 1
    print(time.time() - start)
    with readydecLk:
        ready_dec = True


obs_dec = subjects.Subject()
obs_dec.observe_on(NewThreadScheduler()).subscribe(on_next=detect)

remain_tolarence = 2
remain_record = 0


def send(frame):
    global ready, refreshFlag, boxes_track
    with readyLk:
        ready = False

    small = cv2.resize(frame, (0, 0), fx=resize_rate, fy=resize_rate)

    with refreshLk:
        if refreshFlag:
            with readydecLk:
                if ready_dec:
                    obs_dec.on_next(frame)
                    refreshFlag = False
        else:
            success = True

            with resultLk:
                for i, tracker in trackers.copy().items():
                    success, box = tracker.update(small)
                    if not success:
                        del trackers[i]
                        del boxes_track[i]
                        del labels[i]
                        del confidences[i]
                    else:
                        boxes_track[i] = box

                # remain=time.time() - remain_record
                # if remain > remain_tolarence:
                #     alarmc = '%d new in %d face' % (rec, len(faces))
                #     async_to_sync(channel_layer.send)(channel_name, {
                #         'type': 'send.alarm',
                #         'info': alarmc
                #     })
                #     Alarm.objects.create(content=alarmc)

    with readyLk:
        ready = True


obs_track = subjects.Subject()
obs_track.observe_on(NewThreadScheduler()).subscribe(on_next=send)


def stream():
    global resize_rate
    rtmp = "http://ivi.bupt.edu.cn/hls/cctv5phd.m3u8"
    # rtmp='http://153.156.230.207:8084/-wvhttp-01-/GetOneShot?image_size=640x480&frame_count=1000000000'
    # rtmp='rtsp://admin:admin@59.66.68.38:554/cam/realmonitor?channel=1&subtype=0'
    print(0)
    stream = cv2.VideoCapture(rtmp)
    frame = stream.read()[1]
    resize_rate = 800 / frame.shape[1]
    print('resize_rate: %f' % resize_rate)
    print(0)
    while True:
        frame = stream.read()[1]
        print(0)

        # with readyLk:
            # if ready:
                # obs_track.on_next(frame)

        with resultLk:
            boxes = boxes_track

        for i, box in boxes.items():
            drawLabel(
                frame,
                'id: ' + str(i) + ' ' + labels[i] + str(confidences[i]),
                int(box[0] / resize_rate), int(box[1] / resize_rate),
                int(box[0] / resize_rate + box[2] / resize_rate),
                int(box[1] / resize_rate + box[3] / resize_rate),
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


def refresh(request):
    global refreshFlag
    with refreshLk:
        refreshFlag = True
    return HttpResponse('ok')
