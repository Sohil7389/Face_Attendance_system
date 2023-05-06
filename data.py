import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://face-attendance-system-5f8d0-default-rtdb.firebaseio.com/"
})

ref = db.reference('Students')

data = {
    "123456":
        {
            "name": "sohil",
            "major": "machine learning",
            "starting_year": 2019,
            "total_attendance": 5,
            "standing": "Best",
            "year": 4,
            "last_attendance": "02-05-2023 10:12:12"
        },

    "852741":
        {
            "name": "Emly Blunt",
            "major": "Economics",
            "starting_year": 2017,
            "total_attendance": 10,
            "standing": "Good",
            "year": 2,
            "last_attendance": "02-05-2023 10:15:12"
        },

    "963852":
        {
            "name": "Elon musk",
            "major": "AI",
            "standing": "Good",
            "starting_year": 2015,
            "total_attendance": 20,
            "year": 5,
            "last_attendance": "02-05-2023 10:18:12"
        }
}
for key, value in data.items():
    ref.child(key).set(value)
