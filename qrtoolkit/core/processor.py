import re
import json
import urllib.parse


class DataProcessor:
    @staticmethod
    def is_url(data):
        """Check if data is a URL"""
        url_pattern = re.compile(
            r"^(?:http|ftp)s?://"  # http:// or https://
            # domain...
            r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"
            r"localhost|"  # localhost...
            r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
            r"(?::\d+)?"  # optional port
            r"(?:/?|[/?]\S+)$",
            re.IGNORECASE,
        )
        return bool(url_pattern.match(data))

    @staticmethod
    def is_2fa_secret(data):
        """Check if data contains 2FA secret (otpauth://)"""
        return data.startswith("otpauth://")

    @staticmethod
    def extract_2fa_secrets(data):
        """Extract 2FA secrets from data"""
        if DataProcessor.is_2fa_secret(data):
            return [data]

        # Handle multiple secrets or other formats
        secrets = []
        if "otpauth://" in data:
            # Simple extraction - can be enhanced
            secrets = re.findall(r"otpauth://[^\s]+", data)

        return secrets

    @staticmethod
    def parse_2fa_url(url):
        """Parse otpauth URL into components"""
        parsed = urllib.parse.urlparse(url)
        query_params = urllib.parse.parse_qs(parsed.query)

        return {
            "type": parsed.path.lstrip("/").split("/")[0],
            "label": parsed.path.lstrip("/").split("/")[1]
            if len(parsed.path.split("/")) > 2
            else "",
            "secret": query_params.get("secret", [""])[0],
            "issuer": query_params.get("issuer", [""])[0],
            "algorithm": query_params.get("algorithm", ["SHA1"])[0],
            "digits": query_params.get("digits", ["6"])[0],
            "period": query_params.get("period", ["30"])[0],
        }
