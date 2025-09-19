import os
from datetime import datetime


class TextHandler:
    @staticmethod
    def save_to_file(data, output_file=None):
        """Save data to text file"""
        if not output_file:
            output_file = f"qr_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

        with open(output_file, "w") as f:
            f.write(data)

        return output_file

    @staticmethod
    def append_to_file(data, output_file):
        """Append data to text file"""
        with open(output_file, "a") as f:
            f.write(data + "\n")

        return output_file
