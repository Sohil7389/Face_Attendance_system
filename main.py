import pickle
import os
from datetime import datetime
# import EncodeGenerator
import cv2
import numpy as np
import face_recognition
import cvzone
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://face-attendance-system-5f8d0-default-rtdb.firebaseio.com/",
    'storageBucket': "face-attendance-system-5f8d0.appspot.com"
})
bucket = storage.bucket()
# Webcam
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

image_background = cv2.imread('Resources/background.png')

# Importing the Mode Images
folder_Mode_path = 'Resources/Modes'
mode_path_list = os.listdir(folder_Mode_path)
img_Mode_list = []
for path in mode_path_list:
    img_Mode_list.append(cv2.imread(os.path.join(folder_Mode_path, path)))

# Load the encoding file
print("Loading Encoded file......")
file = open("EncodeFile.p", 'rb')
encode_list_known_with_ids = pickle.load(file)
file.close()
encode_list_known, studentIDs = encode_list_known_with_ids
print("File Loaded")
# print(studentIDs)

modeType = 0
counter = 0
id = -1
imgStudent = []


while True:
    success, img = cap.read()

    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

    image_background[162:162+480, 55:55+640] = img
    image_background[44:44+633, 808:808+414] = img_Mode_list[modeType]

    if faceCurFrame:
        for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
            matches = face_recognition.compare_faces(encode_list_known, encodeFace)
            faceDis = face_recognition.face_distance(encode_list_known, encodeFace)
            # print("Matches", matches)
            # print("faceDis", faceDis)

            matchIndex = np.argmin(faceDis)
            # print("MatchIndex", matchIndex)

            if matches[matchIndex]:
                # print("Known Face Detected")
                # print(studentIDs[matchIndex])
                y1, x2, y2, x1 = faceLoc
                # y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                bbox = x1 + 44, y1 + 162, x2 - x1, y2 - y1
                image_background = cvzone.cornerRect(image_background, bbox, rt=0)
                id = studentIDs[matchIndex]

                if counter == 0:
                    cvzone.putTextRect(image_background, "Loading", (275, 400))
                    cv2.imshow("Face Attendance", image_background)
                    cv2.waitKey(1)
                    counter = 1
                    modeType = 1

            if counter != 0:
                if counter == 1:
                    # get the data
                    studentInfo = db.reference(f'Students/{id}').get()
                    print(studentInfo)

                    #get the image
                    blob = bucket.get_blob(f'Images/{id}.png')
                    array = np.frombuffer(blob.download_as_string(), np.uint8)
                    imgStudent = cv2.imdecode(array, cv2.COLOR_BGRA2RGB)

                    # Update the data
                    datetimeObject = datetime.strptime(studentInfo['last_attendance'], "%d-%m-%Y %H:%M:%S")
                    second_elapsed = (datetime.now() - datetimeObject).total_seconds()
                    print(second_elapsed)
                    if second_elapsed > 50:
                        ref = db.reference(f'Students/{id}')
                        studentInfo['total_attendance'] += 1
                        ref.child('total_attendance').set(studentInfo['total_attendance'])
                        ref.child('last_attendance').set(datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
                    else:
                        modeType = 3
                        counter = 0
                        image_background[44:44 + 633, 808:808 + 414] = img_Mode_list[modeType]

                if modeType != 3:
                     if 10 < counter < 20:
                        modeType = 2

                     image_background[44:44 + 633, 808:808 + 414] = img_Mode_list[modeType]

                     if counter <= 10:
                        cv2.putText(image_background, str(studentInfo['total_attendance']), (861, 125), cv2.FONT_HERSHEY_COMPLEX, 1, (255,255,255), 1)
                        cv2.putText(image_background, str(studentInfo['major']), (1006, 550), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0,0,0), 1)
                        cv2.putText(image_background, str(id), (1006, 493), cv2.FONT_HERSHEY_SCRIPT_COMPLEX, 0.6, (0,0,0), 1)
                        cv2.putText(image_background, str(studentInfo['standing']), (910, 625), cv2.FONT_HERSHEY_COMPLEX, 0.6, (100,100,100), 1)
                        cv2.putText(image_background, str(studentInfo['year']), (1025, 625), cv2.FONT_HERSHEY_COMPLEX, 0.6, (100,100,100), 1)
                        cv2.putText(image_background, str(studentInfo['starting_year']), (1125, 625), cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)

                        (w,h), _ = cv2.getTextSize(studentInfo['name'], cv2.FONT_HERSHEY_COMPLEX, 1, 1)
                        offset = (414-w)//2
                        cv2.putText(image_background, str(studentInfo['name']), (808+offset, 445), cv2.FONT_HERSHEY_COMPLEX, 1, (55, 55 ,55), 1)
                        image_background[175:175+216, 909:909+216] = imgStudent
                     counter = counter+1

                     if counter>20:
                        counter = 0
                        modeType = 0
                        studentInfo = []
                        imgStudent = []
                        image_background[44:44 + 633, 808:808 + 414] = img_Mode_list[modeType]
    else:
        modeType = 0
        counter = 0

    cv2.imshow("Face Attendance", image_background)
    cv2.waitKey(1)
