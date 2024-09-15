import face_recognition
import cv2
import pickle
import dlib
import datetime
import numpy as np
from sklearn.metrics import mean_squared_error as mse
from skimage.metrics import structural_similarity as ssim
import math

# Helper functions
def face_distance_to_conf(face_distance, face_match_threshold=0.6):
    if face_distance > face_match_threshold:
        range = (1.0 - face_match_threshold)
        linear_val = (1.0 - face_distance) / (range * 2.0)
        return linear_val
    else:
        range = face_match_threshold
        linear_val = 1.0 - (face_distance / (range * 2.0))
        return linear_val + ((1.0 - linear_val) * math.pow((linear_val - 0.5) * 2, 0.2))

def predict(X_img, knn_clf=None, model_path=None, distance_threshold=0.45):
    if knn_clf is None and model_path is None:
        raise Exception("Must supply knn classifier either through knn_clf or model_path")
    if knn_clf is None:
        with open(model_path, 'rb') as f:
            knn_clf = pickle.load(f)
    X_face_locations = face_recognition.face_locations(X_img, number_of_times_to_upsample=0)
    if len(X_face_locations) == 0:
       return []
    faces_encodings = face_recognition.face_encodings(X_img, known_face_locations=X_face_locations)
    closest_distances = knn_clf.kneighbors(faces_encodings, n_neighbors=1)
    are_matches = [closest_distances[0][i][0] <= distance_threshold for i in range(len(X_face_locations))]
    return [(pred, loc) if rec else ("UNKNOWN", loc) for pred, loc, rec in zip(knn_clf.predict(faces_encodings), X_face_locations, are_matches)]

# Load known faces
def load_known_faces():
    known_face_encodings = []
    known_face_names = []

    for name in ["vinni", "shan", "deep", "madam"]:
        image_path = f"/home/dikshit/Files/final_app/app/known/{name}.jpg"
        image = face_recognition.load_image_file(image_path)
        encoding = face_recognition.face_encodings(image)[0]
        known_face_encodings.append(encoding)
        known_face_names.append(name)

    return known_face_encodings, known_face_names

# Initialize video capture
video1 = cv2.VideoCapture(0)
video2 = cv2.VideoCapture(1)

# Load the trained KNN model
knn_model_path = "trained_knn_model.clf"
knn_clf = None  # Load your KNN model if available

# Track faces across multiple cameras
def track(img1, l1, name1, img2, l2, name2):
    tracker1 = dlib.correlation_tracker()
    tracker1.start_track(img1, dlib.rectangle(*l1[0]))

    tracker2 = dlib.correlation_tracker()
    tracker2.start_track(img2, dlib.rectangle(*l2[0]))

    while True:
        ret, img1 = video1.read()
        ret, img2 = video2.read()

        if not ret:
            break

        tracker1.update(img1)
        tracker2.update(img2)

        rect1 = tracker1.get_position()
        rect2 = tracker2.get_position()

        pt11 = (int(rect1.left()), int(rect1.top()))
        pt21 = (int(rect1.right()), int(rect1.bottom()))

        pt12 = (int(rect2.left()), int(rect2.top()))
        pt22 = (int(rect2.right()), int(rect2.bottom()))

        cv2.rectangle(img1, pt11, pt21, (255, 255, 255), 3)
        cv2.rectangle(img2, pt12, pt22, (255, 255, 255), 3)

        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(img1, name1, (int(rect1.left()) + 6, int(rect1.bottom()) - 6), font, 1.0, (0, 0, 255), 1)
        cv2.putText(img2, name2, (int(rect2.left()) + 6, int(rect2.bottom()) - 6), font, 1.0, (0, 0, 255), 1)

        cv2.imshow("Image1", img1)
        cv2.imshow("Image2", img2)

        if cv2.waitKey(1) == 27:
            break

# Face recognition and accuracy calculation
def main():
    known_face_encodings, known_face_names = load_known_faces()
    acclist = []

    while True:
        ret, frame1 = video1.read()
        ret, frame2 = video2.read()

        if not ret:
            break

        rgb_frame1 = frame1[:, :, ::-1]
        rgb_frame2 = frame2[:, :, ::-1]

        predictions1 = predict(rgb_frame1, knn_clf=knn_clf, model_path=knn_model_path)
        predictions2 = predict(rgb_frame2, knn_clf=knn_clf, model_path=knn_model_path)

        l1 = []
        for name1, (top, right, bottom, left) in predictions1:
            l1.append([(top, right, bottom, left)])
            cv2.rectangle(frame1, (left, top), (right, bottom), (0, 0, 255), 2)
            cv2.rectangle(frame1, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame1, name1, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

        l2 = []
        for name2, (top, right, bottom, left) in predictions2:
            l2.append([(top, right, bottom, left)])
            cv2.rectangle(frame2, (left, top), (right, bottom), (0, 0, 255), 2)
            cv2.rectangle(frame2, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame2, name2, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

        if len(predictions1) > 0 and len(predictions2) > 0:
            name1, (top1, right1, bottom1, left1) = predictions1[0]
            name2, (top2, right2, bottom2, left2) = predictions2[0]
            track(frame1, l1, name1, frame2, l2, name2)

        cv2.imshow('Video1', frame1)
        cv2.imshow('Video2', frame2)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video1.release()
    video2.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
