import face_recognition
import os


class FaceRecognizer:


    def __init__(self, image_path):

        if not os.path.exists(image_path):

            raise FileNotFoundError(
                image_path
            )


        image = face_recognition.load_image_file(
            image_path
        )


        encodings = face_recognition.face_encodings(
            image
        )


        if len(encodings) == 0:

            raise Exception(
                "Aucun visage trouvé dans l'image propriétaire"
            )


        self.owner_encoding = encodings[0]



    def is_owner(self, frame):


        rgb = frame[:, :, ::-1]


        faces = face_recognition.face_encodings(
            rgb
        )


        for face in faces:


            result = face_recognition.compare_faces(
                [
                    self.owner_encoding
                ],
                face,
                tolerance=0.5
            )


            if result[0]:

                return True



        return False