import cv2
from pyzbar.pyzbar import decode
import os
import matplotlib.pyplot as plt
import sys
from ..utils.colors import foreground
# from ..utils.loger import get_logger

# logger = get_logger()

fg = foreground()
RESET = fg.RESET


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
                results.append(
                    {
                        "data": obj.data.decode("utf-8"),
                        "type": obj.type,
                        "quality": getattr(obj, "quality", None),
                    }
                )

            return results

        except Exception as e:
            raise Exception(f"Error decoding QR code: {str(e)}")

    def decode_from_video(self, stream=False, timeout=30):
        """Decode QR code from video feed with timeout"""
        cap = cv2.VideoCapture(0)
        start_time = cv2.getTickCount()

        plt.ion()  # interactive mode on

        result = []
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                decoded_objects = decode(frame)
                current_time = (
                    cv2.getTickCount() - start_time
                ) / cv2.getTickFrequency()

                if decoded_objects:
                    for i, _object in enumerate(decoded_objects):
                        left, top, w, h = _object.rect

                        cv2.rectangle(
                            frame, (left, top), (left + w, top + h), (0, 255, 0), 2
                        )
                        cv2.putText(
                            frame,
                            f"QR-{i}",
                            (left, top - 10),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.9,
                            (0, 255, 0),
                            2,
                        )
                        if stream:
                            data = {
                                "data": _object.data.decode("utf-8"),
                                "type": _object.type,
                            }
                            if data not in result:
                                result.append(data)
                                print(
                                    f"{fg.DWHITE_FG}Data: {fg.BBLUE_FG}{_object.data.decode("utf-8")}{RESET}",
                                    end="\r",
                                )
                    if not stream:
                        cap.release()
                        plt.ioff()
                        plt.close()

                if current_time > timeout and not stream:
                    break

                # --- Show frame with matplotlib ---
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                plt.imshow(frame_rgb)
                plt.title("QR Scanner")
                plt.axis("off")
                plt.pause(0.001)  # allow UI to update
                plt.clf()  # clear for next frame

            cap.release()
            plt.ioff()
            plt.close()
            return (
                result
                if stream
                else [
                    {"data": obj.data.decode("utf-8"), "type": obj.type}
                    for obj in decoded_objects
                ]
            )

        except KeyboardInterrupt:
            cap.release()
            plt.ioff()
            plt.close()
            return (
                result
                if stream
                else [
                    {"data": obj.data.decode("utf-8"), "type": obj.type}
                    for obj in decoded_objects
                ]
            )
            # sys.exit("\nToolKit Exit!")


if __name__ == "__main__":
    qr = QRDecoder()
    qr.decode_from_video()
