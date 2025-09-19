import webbrowser
from urllib.parse import urlparse


class URLHandler:
    @staticmethod
    def is_valid_url(url):
        """Check if a string is a valid URL"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    @staticmethod
    def open_url(url):
        """Open URL in default browser"""
        if URLHandler.is_valid_url(url):
            webbrowser.open(url)
            return True
        return False
