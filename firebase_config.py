import pyrebase

firebaseConfig = {
    "apiKey": "AIzaSyCKz_o_Px7n9ng3iNzMI2mrShuHSIVEI3c",
    "authDomain": "resume-ai-app-cbc0b.firebaseapp.com",
    "projectId": "resume-ai-app-cbc0b",
    "storageBucket": "resume-ai-app-cbc0b.firebasestorage.app",
    "messagingSenderId": "732463770378",
    "appId": "1:732463770378:web:7501b3e82c89be7ddd68f3",
    "databaseURL": ""
}

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()