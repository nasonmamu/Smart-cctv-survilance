#!/usr/bin/python3
import sys
from PyQt4 import QtGui, uic, QtCore
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from datetime import datetime
import cv2
import numpy as np
from PIL import Image
import os
import face_recognition

# Define the directory for saving files
directory = "/home/pi/Desktop/"
path = os.path.join(directory, "dataset")
face_detector = cv2.CascadeClassifier(os.path.join(directory, "haarcascade_frontalface_default.xml"))

class DoThreading(QThread):
    def __init__(self, func):
        super().__init__()
        self.func = func

    def __del__(self):
        self.wait()

    def run(self):
        self.func()

class MyWindow(QtGui.QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        self.setupUi()
        self.initialize()

    def setupUi(self):
        try:
            self.close()
        except:
            pass
        super(MyWindow, self).__init__()
        self.process_this_frame = True
        self.face_locations = []
        self.face_encodings = []
        self.face_names = []
        self.faceSamples = []
        self.ids = []
        self.startTraining = False
        self.count = 0
        self.people = 0
        self.listOfPeople = []
        self.isUsing = False
        self.ids = []
        try:
            self.stop_webcamtrainer()
        except:
            pass
        f = open(os.path.join(directory, "DATABASE.txt"), "r")
        self.listOfPeople = [x.strip().split(",")[0] for x in f.readlines()]
        f.close()
        f = open(os.path.join(directory, "ENCODINGS.txt"), "r")
        for x in f.readlines():
            if x.strip():
                self.faceSamples.append(np.array(eval(x.split("=")[1])))
                self.ids.append(int(x.split("=")[0]))
        f.close()
        print(self.listOfPeople)
        self.counter = 1000
        try:
            self.out.release()
        except:
            pass
        self.start_webcam()

    def trainView(self):
        try:
            self.close()
        except:
            pass
        super(MyWindow, self).__init__()
        uic.loadUi(os.path.join(directory, "TrainView.ui"), self)
        self.setFixedSize(self.size())
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.center()
        self.show()
        self.label_success.hide()
        self.pushButton.clicked.connect(self.doTraining)
        self.pushButton_2.clicked.connect(self.__init__)
        self.pushButton_3.clicked.connect(self.reset)
        self.start_webcamtrainer()

    def doTraining(self):
        if self.textEdit.toPlainText().strip():
            self.startTraining = True
            self.people = 0
            self.listOfPeople = []
            f = open(os.path.join(directory, "DATABASE.txt"), "r")
            self.listOfPeople = [x.strip().split(",")[0] for x in f.readlines()]
            self.people = len(self.listOfPeople)
            f.close()
        else:
            self.label_success.setText("SOME FIELDS ARE EMPTY!")
            self.label_success.show()

    def mapView(self):
        try:
            self.close()
        except:
            pass
        super(MyWindow, self).__init__()
        uic.loadUi(os.path.join(directory, "MapView.ui"), self)
        self.setFixedSize(self.size())
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.center()
        self.show()
        self.pushButton.clicked.connect(self.__init__)

    # WEBCAM TRAINER
    def start_webcamtrainer(self):
        self.capturetrain = cv2.VideoCapture(0)
        self.timertrain = QTimer(self)
        self.timertrain.timeout.connect(self.update_frametrainer)
        self.timertrain.start()

    def update_frametrainer(self):
        ret1, self.imagetrain = self.capturetrain.read()
        self.imagetrain = cv2.flip(self.imagetrain, 1)
        self.displayImageTrain(self.imagetrain, "label")

    def stop_webcamtrainer(self):
        self.timertrain.stop()
        self.capturetrain.release()

    def __draw_label(self, img, text, pos, bg_color):
        font_face = cv2.FONT_HERSHEY_DUPLEX
        scale = 1
        color = (255, 255, 255)
        thickness = cv2.FILLED
        margin = 2

        txt_size = cv2.getTextSize(text, font_face, scale, thickness)[0]
        end_x = pos[0] + txt_size[0] + margin
        end_y = pos[1] - txt_size[1] - margin

        cv2.rectangle(img, pos, (end_x, end_y), bg_color, thickness)
        cv2.putText(img, text, pos, font_face, scale, color, 1, cv2.LINE_AA)

    def start_webcam(self):
        video_capture = cv2.VideoCapture(0)
        while True:
            ret, img = video_capture.read()
            img = cv2.flip(img, 1)
            small_frame = cv2.resize(img, (0, 0), fx=0.25, fy=0.25)
            small_frame = small_frame[:, :, ::-1]
            now = datetime.now()
            dt_string = now.strftime("%m-%d-%Y %H.%M.%S")
            self.__draw_label(img, dt_string, (0, 479), (0, 0, 255))
            img1 = img
            self.face_names = []
            if self.listOfPeople and not self.isUsing:
                if self.process_this_frame:
                    self.face_locations = face_recognition.face_locations(small_frame)
                    self.face_encodings = face_recognition.face_encodings(small_frame, self.face_locations)
                    for face_encoding in self.face_encodings:
                        matches = face_recognition.compare_faces(self.faceSamples, face_encoding, 0.4)
                        name = None
                        face_distances = face_recognition.face_distance(self.faceSamples, face_encoding)
                        best_match_index = np.argmin(face_distances)
                        if matches[best_match_index]:
                            name = self.listOfPeople[self.ids[best_match_index] - 1]
                            self.face_names.append(name)
                self.process_this_frame = not self.process_this_frame
                for (top, right, bottom, left), name in zip(self.face_locations, self.face_names):
                    top *= 4
                    right *= 4
                    bottom *= 4
                    left *= 4
                    cv2.rectangle(img, (left, top), (right, bottom), (0, 0, 255), 2)
                    cv2.rectangle(img, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                    font = cv2.FONT_HERSHEY_DUPLEX
                    cv2.putText(img, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
                    if not self.isUsing and name != "unknown":
                        self.counter = 0
                        self.isUsing = True
                        self.dateToday = now.strftime("%m-%d-%Y")
                        self.timeCaught = now.strftime("%H:%M:%S")
                        self.theName = str(name)
                        print(f"CAPTURED {self.theName}")
                        self.__draw_label(img, f"CAPTURED {self.theName}", (0, 22), (0, 0, 255))
                        cv2.imwrite(os.path.join(directory, "captured", f"{self.theName}({dt_string}).jpg"), img1[top:bottom, left:right])
                        self.fourcc = cv2.VideoWriter_fourcc(*"XVID")
                        self.out = cv2.VideoWriter(
                            os.path.join(directory, "recorded", f"{self.theName}({dt_string}).avi"),
                            self.fourcc,
                            10.0,
                            (640, 480)
                        )
                        location = "Basement Entrance"
                        with open(os.path.join(directory, "logs", f"{self.dateToday}.txt"), "a+") as f:
                            f.write(f"{self.timeCaught} {self.theName} was spotted at the {location}\n")
            if cv2.waitKey(1) & 0xFF == ord("t"):
                self.key = "t"
                break
            if cv2.waitKey(1) & 0xFF == ord("m"):
                self.key = "m"
                break
            if cv2.waitKey(1) & 0xFF == ord("q"):
                self.key = "q"
                break
            if self.isUsing:
                self.counter += 1
                print(f"Recording: {self.counter} Frames")
                if self.counter < 100:
                    self.__draw_label(img, f"RECORDING {self.theName.upper()}", (0, 22), (0, 0, 255))
                    self.out.write(img)
                else:
                    self.counter = 0
                    self.out.release()
                    self.isUsing = False
            cv2.namedWindow("SMART CCTV", cv2.WND_PROP_FULLSCREEN)
            cv2.setWindowProperty("SMART CCTV", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            cv2.imshow("SMART CCTV", img)
        video_capture.release()
        cv
