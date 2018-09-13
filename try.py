import multiprocessing as mp
import cv2


def queue_img_put(q, rtsp):
    cap = cv2.VideoCapture(0)
    while True:
        is_opened, frame = cap.read()
        q.put(frame) if is_opened else None
        q.get() if q.qsize() > 1 else None


def queue_img_get(q):
    cv2.namedWindow("window_name", flags=cv2.WINDOW_FREERATIO)
    while True:
        frame = q.get()
        cv2.imshow("window_name", frame)
        cv2.waitKey(1)


def run():  # single camera
    rtsp = "rtsp://admin:admin@59.66.68.38:554/cam/realmonitor?channel=1&subtype=0"

    mp.set_start_method(method='spawn')  # init
    queue = mp.Queue(maxsize=2)
    processes = [mp.Process(target=queue_img_put, args=(queue, rtsp,)),
                 mp.Process(target=queue_img_get, args=(queue,))]

    [setattr(process, "daemon", True) for process in processes]  # process.daemon = True
    [process.start() for process in processes]
    [process.join() for process in processes]


if __name__ == '__main__':
    run()