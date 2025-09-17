import cv2
import numpy as np
from pyzbar.pyzbar import decode
from PIL import Image
import os


class QRDecoder:
    def __init__(self):
        pass

    def decode_from_image(self, image_path):
        """Decode QR code from image file"""
        try:
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image file not found: {image_path}")

            image = cv2.imread(image_path)
            decoded_objects = decode(image)

            results = []
            for obj in decoded_objects:
                results.append({
                    'data': obj.data.decode('utf-8'),
                    'type': obj.type,
                    'quality': getattr(obj, 'quality', None)
                })

            return results

        except Exception as e:
            raise Exception(f"Error decoding QR code: {str(e)}")

    def decode_from_video(self, timeout=30):
        """Decode QR code from video feed with timeout"""
        cap = cv2.VideoCapture(0)
        start_time = cv2.getTickCount()

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            decoded_objects = decode(frame)
            current_time = (cv2.getTickCount() - start_time) / \
                cv2.getTickFrequency()

            if decoded_objects:
                cap.release()
                return [{
                    'data': obj.data.decode('utf-8'),
                    'type': obj.type
                } for obj in decoded_objects]

            if current_time > timeout:
                break

            cv2.imshow('QR Scanner', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
        return []
