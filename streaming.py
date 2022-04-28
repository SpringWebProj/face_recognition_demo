import base64
import threading
import cv2
from django.contrib import messages
from django.shortcuts import render, redirect

from django.views.decorators import gzip
from django.http import StreamingHttpResponse

import face_recognition
import camera
import os
import numpy as np


class VideoCamera(object):
    def __init__(self):
        print("===== open video =====")
        self.check = False

        self.camera = camera.VideoCamera()
        self.known_face_encodings = []
        self.known_face_names = []
        dirname = 'knowns'
        files = os.listdir(dirname)
        for filename in files:
            name, ext = os.path.splitext(filename)
            if ext == '.jpg':
                self.known_face_names.append(name)
                pathname = os.path.join(dirname, filename)
                img = face_recognition.load_image_file(pathname)
                face_encoding = face_recognition.face_encodings(img)[0]
                self.known_face_encodings.append(face_encoding)
        self.face_locations = []
        self.face_encodings = []
        self.face_names = []
        self.process_this_frame = True

    def __del__(self):
        del self.camera

    def get_frame(self):
        frame = self.camera.get_frame()

        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        rgb_small_frame = small_frame[:, :, ::-1]

        if self.process_this_frame:
            self.face_locations = face_recognition.face_locations(rgb_small_frame)
            self.face_encodings = face_recognition.face_encodings(rgb_small_frame, self.face_locations)

            self.face_names = []
            for face_encoding in self.face_encodings:
                distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
                min_value = min(distances)

                name = "Unknown"
                if min_value < 0.6:
                    index = np.argmin(distances)
                    name = self.known_face_names[index]
                self.face_names.append(name)

        self.process_this_frame = not self.process_this_frame

        self.check = False

        for (top, right, bottom, left), name in zip(self.face_locations, self.face_names):
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

            self.check = True

        return frame

    def get_jpg_bytes(self):
        frame = self.get_frame()
        ret, jpg = cv2.imencode('.jpg', frame)
        return jpg.tobytes()

    def update(self):
        while True:
            (self.grabbed, self.frame) = self.camera.get_frame()

cc = False
def gen(camera):
    global cc
    while True:
        if camera.check:
            cc = send_ch(camera.check)
        jpg_bytes = camera.get_jpg_bytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpg_bytes + b'\r\n\r\n')


@gzip.gzip_page
def livefe(request):
    try:
        cam = VideoCamera()
        return StreamingHttpResponse(gen(cam), content_type="multipart/x-mixed-replace;boundary=frame")
    except:
        pass


def monitor(request):
    check = cc
    print(check)
    if check:
        messages.add_message(
            request,
            messages.SUCCESS,
            '인식 성공'
        )
    return render(request, 'monitor.html')  # render template


def send_ch(check):
    return check
def test(request):
    return render(request, 'test.html')

    # if request.method == 'GET':
    #     print('GET')
    # elif request.method == 'POST':
    #     username = request.POST['username']
    #     imgData = request.POST['imgData']
    #     # with open('knowns/' + username + '.jpg', 'wb') as ff:
    #     #     ff.write(base64.b64decode(imgData[22:]))
    #     # path = 'knowns/' + username + '.jpg'
    #     print('POST')
    #     data = {
    #         'username': username,
    #         'imgData': imgData
    #         # 'path': path
    #     }
    #     return render(request, 'test.html', data)

