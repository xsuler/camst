from django.http import StreamingHttpResponse, HttpResponse
import cv2
from django.views.decorators import gzip
from darkflow.net.build import TFNet
import time
from rx import subjects
from rx.concurrency import NewThreadScheduler
# import face_recognition
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Alarm, Region
from random import randint

# config alarm
# clean project
# install script
# doc

options_object = {
    "model": "cfg/yolov2-tiny.cfg",
    "load": "bin/yolov2-tiny.weights",
    "labels": "labels_object",
    "threshold": 0.3
}

channel_layer = get_channel_layer()

# options_face = {
#     "model": "cfg/tiny-yolo-face.cfg",
#     "load": "bin/tiny-yolo-face.weights",
#     "labels": "labels_face",
#     "threshold": 0.5
# }

tfnet_object = TFNet(options_object)
# tfnet_face = TFNet(options_face)
channel_name = ''
labels = {}
confidences = {}
boxes_track = {}
flags = {'refresh': True, 'ready_track': True, 'ready_dec': True}

multiTracker = None
resize_rate = 1
framew = 0
frameh = 0

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
    global labels, confidences, remain_record, multiTracker
    flags['ready_dec'] = False
    start = time.time()
    remain_record = time.time()
    small = cv2.resize(frame, (0, 0), fx=resize_rate, fy=resize_rate)
    result_detect = tfnet_object.return_predict(frame)
    multiTracker = cv2.MultiTracker_create()
    for i, result in enumerate(result_detect):
        # tracker = cv2.TrackerCSRT_create()
        box = (result['topleft']['x'] * resize_rate,
               result['topleft']['y'] * resize_rate,
               result['bottomright']['x'] * resize_rate -
               result['topleft']['x'] * resize_rate,
               result['bottomright']['y'] * resize_rate -
               result['topleft']['y'] * resize_rate)
        tracker = cv2.TrackerKCF_create()
        labels[i] = result['label']
        confidences[i] = result['confidence']
        multiTracker.add(tracker, small, box)

    print(time.time() - start)

    flags['ready_dec'] = True


obs_dec = subjects.Subject()
obs_dec.observe_on(NewThreadScheduler()).subscribe(on_next=detect)


def ralarm(v):
    alarm_regions = Region.objects.all()
    for i in list(boxes_track):
        if i not in boxes_track:
            continue
        x, y, w, h = boxes_track[i]
        for region in map(
                lambda region: (region.name, region.x * framew / 100, region.y * frameh / 100, region.w * framew / 100, region.h * frameh / 100),
                alarm_regions):
            if inbox(x, y, region) or inbox(x + w, y, region) or inbox(
                    x, y + h, region) or inbox(x + w, y + h, region):
                alarmc = 'object %s with id %d appears in region %s : %s' % (
                    labels[i], i, region[0],
                    (region[1], region[2], region[1] + region[3],
                     region[2] + region[4]))
                async_to_sync(channel_layer.send)(channel_name, {
                    'type': 'send.alarm',
                    'info': alarmc
                })
                Alarm.objects.create(content=alarmc)


def inbox(x, y, region):
    nm, bx, by, bw, bh = region
    return bx < x < bx + bw and by < y < by + bh


obs_alarm = subjects.Subject()
obs_alarm.observe_on(NewThreadScheduler()).subscribe(on_next=ralarm)


def send(frame):
    global boxes_track, flags
    flags['ready_track'] = False

    small = cv2.resize(frame, (0, 0), fx=resize_rate, fy=resize_rate)

    if flags['refresh'] and flags['ready_dec']:
        obs_dec.on_next(frame)
        flags['refresh'] = False
    else:
        success = True
        if multiTracker is not None:
            success, boxes = multiTracker.update(small)
            boxes_track = dict(enumerate(boxes))
            obs_alarm.on_next(None)
        if not success:
            flags['refresh'] = True
    flags['ready_track'] = True


obs_track = subjects.Subject()
obs_track.observe_on(NewThreadScheduler()).subscribe(on_next=send)


def stream():
    global resize_rate, framew, frameh
    rtmp = "http://ivi.bupt.edu.cn/hls/cctv5phd.m3u8"
    # rtmp='http://153.156.230.207:8084/-wvhttp-01-/GetOneShot?image_size=640x480&frame_count=1000000000'
    # rtmp='rtsp://admin:admin@59.66.68.38:554/cam/realmonitor?channel=1&subtype=0'
    stream = cv2.VideoCapture(rtmp)
    frame = stream.read()[1]
    while frame is None:
        frame = stream.read()[1]
    resize_rate = 800 / frame.shape[1]
    framew = frame.shape[1]
    frameh = frame.shape[0]

    print('resize_rate: %f' % resize_rate)
    while True:
        frame = stream.read()[1]
        while frame is None:
            frame = stream.read()[1]
        if flags['ready_track']:
            obs_track.on_next(frame)
        alarm_regions = Region.objects.all()

        for name, x, y, w, h in map(
                lambda region: (region.name, region.x * framew / 100, region.y * frameh / 100, region.w * framew / 100, region.h * frameh / 100),
                alarm_regions):
            drawLabel(frame, 'alarm region: %s' % name, x, y, x + w, y + h,
                      (255, 255, 255), 4)

        for i in list(boxes_track):
            box = boxes_track[i]
            drawLabel(
                frame, 'id: ' + str(i) + ' ' + labels[i] + str(confidences[i]),
                box[0] / resize_rate, box[1] / resize_rate,
                box[0] / resize_rate + box[2] / resize_rate,
                box[1] / resize_rate + box[3] / resize_rate, (255, 255, 5), 2)

        jpeg = cv2.imencode('.jpg', frame)[1]
        bts = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + bts + b'\r\n\r\n')


def drawLabel(img, txt, l, t, r, b, color, px):
    l, t, r, b = (int(l), int(t), int(r), int(b))
    cv2.putText(img, txt, (l, t + 20), cv2.FONT_HERSHEY_PLAIN, 2, color, 2)
    cv2.rectangle(img, (l, t), (r, b), color, px)


@gzip.gzip_page
def cam(request):
    return StreamingHttpResponse(
        stream(), content_type="multipart/x-mixed-replace;boundary=frame")


def refresh(request):
    global flags
    flags['refresh'] = True
    return HttpResponse('ok')
