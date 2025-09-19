import json
import os
from datetime import datetime
from ..core.processor import DataProcessor


class JSONHandler:
    @staticmethod
    def save_2fa_secrets(secrets, output_file=None):
        """Save 2FA secrets to JSON file"""
        if not output_file:
            output_file = f"2fa_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        data = {"version": 1, "generated": datetime.now().isoformat(), "entries": []}

        for secret in secrets:
            parsed = DataProcessor.parse_2fa_url(secret)
            # Only add valid 2FA entries
            if parsed.get("secret"):
                data["entries"].append(parsed)

        # Only create file if we have valid entries
        if data["entries"]:
            with open(output_file, "w") as f:
                json.dump(data, f, indent=2)
            return output_file
        return None

    @staticmethod
    def save_generic_data(data_list, output_file):
        """Save generic data to JSON file"""
        with open(output_file, "w") as f:
            json.dump(data_list, f, indent=2)
        return output_file

    @staticmethod
    def print_json(data_list):
        """Print data as formatted JSON to console"""
        print(json.dumps(data_list, indent=2))
