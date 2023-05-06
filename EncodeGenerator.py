import cv2
import face_recognition
import pickle
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://face-attendance-system-5f8d0-default-rtdb.firebaseio.com/",
    'storageBucket': "face-attendance-system-5f8d0.appspot.com"
})


# Importing students Images
folder_path = 'Images'
path_list = os.listdir(folder_path)
img_list = []
studentsID = []
for path in path_list:
    img_list.append(cv2.imread(os.path.join(folder_path, path)))
    studentsID.append(os.path.splitext(path)[0])
    filename = f'{folder_path}/{path}'
    bucket = storage.bucket()
    blob = bucket.blob(filename)
    blob.upload_from_filename(filename)


def find_encoding(img_list):
    encode_list = []
    for img in img_list:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encode_list.append(encode)

    return encode_list

print("Encoding Started............")
encode_list_known = find_encoding(img_list)
encode_list_known_with_IDs = [encode_list_known, studentsID]
print("Encoding Complete")

file = open("EncodeFile.p", 'wb')
pickle.dump(encode_list_known_with_IDs, file)
file.close()
print("File Saved")
