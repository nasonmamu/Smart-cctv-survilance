from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QImage, QPixmap
import cv2
from camera import Camera
from middleware.gps import GPS
from models.camera import Camera as CameraModel
from middleware.face_recognition import FaceRecognition
from middleware.motion_detection import MotionDetection
from middleware.alert import Alert
from cloud_storage import CloudStorage
from network_monitor import NetworkMonitor
from flask_login import current_user

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not is_admin():
            print("Access denied.")
            return

        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1280, 720)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.label_video = QtWidgets.QLabel(self.centralwidget)
        self.label_video.setGeometry(QtCore.QRect(20, 10, 1241, 661))
        self.label_video.setFrameShape(QtWidgets.QFrame.Box)
        self.label_video.setScaledContents(True)
        self.label_video.setObjectName("label_video")

        self.label_gps = QtWidgets.QLabel(self.centralwidget)
        self.label_gps.setGeometry(QtCore.QRect(20, 680, 400, 30))
        self.label_gps.setObjectName("label_gps")

        self.label_info = QtWidgets.QLabel(self.centralwidget)
        self.label_info.setGeometry(QtCore.QRect(20, 720, 400, 30))
        self.label_info.setObjectName("label_info")

        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(1120, 680, 141, 34))
        self.pushButton.setStyleSheet("background-color: rgb(139, 139, 139); color: rgb(255, 255, 255); border-color: rgb(255, 255, 255);")
        self.pushButton.setObjectName("pushButton")
        self.pushButton.setText("BACK")

        MainWindow.setCentralWidget(self.centralwidget)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.alert_system = Alert(email_config={
            'from': 'your_email@example.com',
            'to': 'recipient@example.com',
            'smtp_server': 'smtp.example.com',
            'smtp_port': 587,
            'username': 'your_username',
            'password': 'your_password'
        })
        self.camera = Camera(source='rtsp://username:password@ip_address:port/stream_path')
        self.gps = GPS()
        self.face_recognition = FaceRecognition(alert_system=self.alert_system)
        self.motion_detection = MotionDetection(alert_system=self.alert_system)
        self.cloud_storage = CloudStorage(
            aws_access_key='your_aws_access_key',
            aws_secret_key='your_aws_secret_key',
            bucket_name='your_bucket_name'
        )
        self.network_monitor = NetworkMonitor()

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

        self.update_gps()
        self.monitor_network()

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))

    def update_frame(self):
        frame = self.camera.get_frame()
        if frame is not None:
            face_locations, face_names = self.face_recognition.recognize_faces(frame)
            movements = self.motion_detection.detect_motion(frame)

            self.display_face_info(face_locations, face_names)
            self.display_movement_info(movements)

            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            q_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.label_video.setPixmap(QPixmap.fromImage(q_image))

            cv2.imwrite('current_frame.jpg', frame)
            self.cloud_storage.upload_file('current_frame.jpg', 'current_frame.jpg')

    def update_gps(self):
        lat, lon = self.gps.get_coordinates()
        self.label_gps.setText(f"Latitude
