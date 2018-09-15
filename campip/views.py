from django.http import StreamingHttpResponse, HttpResponse
import cv2
from django.views.decorators import gzip
from darkflow.net.build import TFNet
import time
from rx import subjects
from rx.concurrency import NewThreadScheduler
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Alarm, Region, Cam
from random import randint

options_object = {
    "model": "cfg/yolov2-tiny.cfg",
    "load": "bin/yolov2-tiny.weights",
    "labels": "labels_object",
    "threshold": 0.3
}

channel_layer = get_channel_layer()

tfnet_object = TFNet(options_object)
channel_name = ''
labels = {}
confidences = {}
boxes_track = {}
alarm_delay = {}
flags = {'refresh': True, 'ready_track': True, 'ready_dec': True}

multiTracker = None
resize_rate = 1
framew = 0
frameh = 0
camaddr = None


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

    alarm_delay.clear()
    print(time.time() - start)

    flags['ready_dec'] = True


obs_dec = subjects.Subject()
obs_dec.observe_on(NewThreadScheduler()).subscribe(on_next=detect)


def cover(box1, box2):
    left = max(box1[0], box2[0])
    rignt = min(box1[2], box2[2])
    top = max(box1[1], box2[1])
    bottom = min(box1[3], box2[3])
    if rignt < left or bottom < top:
        return 0
    arb2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
    arbi = (rignt - left) * (bottom - top)
    return arbi / arb2


def ralarm(v):
    alarm_regions = Region.objects.all()
    for i in list(boxes_track):
        if i not in boxes_track:
            continue
        x, y, w, h = boxes_track[i]
        for region in map(
                lambda region: (region.name, region.x * framew / 100, region.y * frameh / 100, region.w * framew / 100, region.h * frameh / 100, region.cover, region.delay),
                alarm_regions):
            box1 = (x, y, x + w, y + h)
            box2 = (region[1], region[2], region[1] + region[3],
                    region[2] + region[4])
            coverf = cover(box2, box1)
            if coverf >= region[5]:
                if i in alarm_delay:
                    print('delay', time.time() - alarm_delay[i][1])
                    if time.time() - alarm_delay[i][1] > region[6]:
                        alarm_delay[i][1] = time.time()
                        alarmc = 'object %s with id %d appears in region %s, cover: %f, existing for %f seconds' % (
                            labels[i], i, region[0], coverf,
                            time.time() - alarm_delay[i][0])
                        async_to_sync(channel_layer.send)(
                            channel_name, {
                                'type': 'send.alarm',
                                'info': alarmc
                            })
                        Alarm.objects.create(content=alarmc)
                else:
                    tm = time.time()
                    alarm_delay[i] = [tm, tm]


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
        if not success or len(boxes_track) == 0:
            flags['refresh'] = True
    flags['ready_track'] = True


obs_track = subjects.Subject()
obs_track.observe_on(NewThreadScheduler()).subscribe(on_next=send)


def stream():
    global resize_rate, framew, frameh, camaddr
    if camaddr is None:
        camaddr = Cam.objects.last().addr
    if camaddr == '0':
        camaddr = 0
    stream = cv2.VideoCapture(camaddr)
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
            if i not in boxes_track:
                continue
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
