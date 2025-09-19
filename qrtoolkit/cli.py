import argparse
import sys
import os
import asyncio
from tqdm.asyncio import tqdm
from datetime import datetime
from .core.decoder import QRDecoder
from .core.processor import DataProcessor
from .outputs.json_handler import JSONHandler
from .outputs.url_handler import URLHandler
from .outputs.text_handler import TextHandler

# from .utils.Execptions import QRToolException
from .utils.colors import foreground
from .utils.loger import get_logger

logger = get_logger()

fg = foreground()
RESET = fg.RESET


def main():
    parser = argparse.ArgumentParser(description="QR Code Processing Toolkit")

    # Input options
    input_group = parser.add_argument_group("Input Options")
    input_group.add_argument("inputs", nargs="*", help="Input image files")
    input_group.add_argument("-d", "--directory", help="Directory to scan for images")
    input_group.add_argument(
        "-c", "--camera", action="store_true", help="Use camera to scan QR code"
    )
    input_group.add_argument(
        "-s", "--screenshot", action="store_true", help="Capture screenshot"
    )

    # Output options
    output_group = parser.add_argument_group("Output Options")
    output_group.add_argument("-o", "--output", help="Output file")
    output_group.add_argument(
        "-j", "--json", action="store_true", help="Save as JSON (for 2FA)"
    )
    output_group.add_argument(
        "-t", "--text", action="store_true", help="Save as text file"
    )
    output_group.add_argument(
        "-u", "--open-url", action="store_true", help="Auto-open URLs"
    )
    output_group.add_argument("--copy", action="store_true", help="Copy to clipboard")
    output_group.add_argument(
        "--quiet", action="store_true", help="Suppress console output"
    )
    output_group.add_argument(
        "--print", action="store_true", default=True, help="Print to console (default)"
    )

    # Processing options
    process_group = parser.add_argument_group("Processing Options")
    process_group.add_argument(
        "--batch", action="store_true", help="Process multiple files"
    )
    process_group.add_argument(
        "--timeout", type=int, default=30, help="Camera timeout in seconds"
    )

    process_group.add_argument(
        "--stream",
        action="store_true",
        help="Keep reading from camera until terminated.",
    )

    args = parser.parse_args()

    # Validate input
    input_files = []
    if args.inputs:
        input_files = args.inputs
    elif args.directory:
        if not os.path.exists(args.directory):
            parser.error(f"Directory not found: {args.directory}")
        input_files = [
            os.path.join(args.directory, f)
            for f in os.listdir(args.directory)
            if f.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".tiff"))
        ]

    if not any([input_files, args.camera, args.screenshot]):
        parser.error(
            "Please specify an input source (files, directory, camera, or screenshot)"
        )
    ArgsProcessor(args, input_files).process()


class ArgsProcessor:
    """
    Handle Process based on inputs and provided flags
    Allows args chaining for multiprocessing
    """

    def __init__(self, args, input_files):
        self.args = args
        self.decoder = QRDecoder()
        self.processor = DataProcessor()
        self.all_results = []
        self.input_files = (
            tqdm(input_files, desc=f"{fg.DWHITE_FG}Files:{RESET}")
            if len(input_files) > 1
            else input_files
        )

    def _map_op_(self) -> None:
        _map_ = {
            self.args.camera: self.use_camera,
            self.args.screenshot: self.use_screenshot,
        }

        operation_method = next((_map_[key] for key in _map_ if key), None)
        if operation_method:
            operation_method()

    def _map_ouputs_(self) -> None:
        _map_ = {
            self.args.json: self.output_json,
            self.args.text: self.output_text,
        }
        output_method = next((_map_[key] for key in _map_ if key), None)
        if output_method:
            output_method()

    def _map_flags_(self) -> None:
        _map_ = {
            self.args.open_url: self.open_url,
            self.args.copy: self.copy,
        }
        flag_method = next((_map_[key] for key in _map_ if key), None)
        if flag_method:
            flag_method()

    def use_camera(self):
        # Process camera if requested
        if not self.args.quiet:
            logger.info(
                f"{fg.DWHITE_FG}Scanning from camera{RESET}{fg.BBLUE_FG}...{RESET}"
            )
            results = self.decoder.decode_from_video(
                stream=self.args.stream, timeout=self.args.timeout
            )

            self.all_results.extend(results)

        return

    def use_screenshot(self):
        # TODO: Implement screenshot functionality
        if not self.args.quiet:
            logger.warn("Screenshot functionality not yet implemented")

    def process_files(self):
        # Process files
        for file_path in self.input_files:
            if not self.args.quiet:
                if len(self.input_files) == 1:
                    logger.info(f"Processing: {file_path}")
            results = self.decoder.decode_from_image(file_path)
            self.all_results.extend(results)

    def output_json(self):
        # Handle 2FA secrets specifically
        twofa_secrets = []
        for data in tqdm(self.decoded_data, desc=f"{fg.DWHITE_FG}Data:{RESET}"):
            if self.processor.is_2fa_secret(data):
                twofa_secrets.append(data)
            else:
                # Check if data contains 2FA secrets
                secrets = self.processor.extract_2fa_secrets(data)
                twofa_secrets.extend(secrets)

        if twofa_secrets:
            output_file = (
                self.args.output
                or f"2fa_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            saved = JSONHandler.save_2fa_secrets(twofa_secrets, output_file)
            if saved and not self.args.quiet:
                logger.info(f"2FA secrets saved to: {fg.BLUE_FG}{output_file}{RESET}")
            else:
                logger.warn(f"{fg.FYELLOW_FG}No valid 2fa were found{RESET}")
        elif self.args.output:
            # Save generic data as JSON
            JSONHandler.save_generic_data(self.decoded_data, self.args.output)
            if not self.args.quiet:
                logger.info(
                    f"Data saved to JSON: {fg.BLUE_FG}{fg.LINE}{self.args.output}{RESET}"
                )

    def output_text(self):
        # Save as text file
        output = self.args.output or "qrscan_output.txt"
        text_content = "\n".join(self.decoded_data)
        TextHandler.save_to_file(text_content, output)
        if not self.args.quiet:
            logger.info(f"Data saved to text file: {fg.CYAN_FG}{output}{RESET}")

    def open_url(self):
        for data in self.decoded_data:
            if self.processor.is_url(data):
                URLHandler.open_url(data)
                if not self.args.quiet:
                    print(f"Opened URL: {fg.BLUE_FG}{data}{RESET}")

    def copy(self):
        try:
            import pyperclip

            pyperclip.copy(self.decoded_data[0])
            if not self.args.quiet:
                print(
                    f"Copied {fg.LINE}{fg.FGREEN_FG}{self.decoded_data[0]}{RESET} to clipboard"
                )
        except ImportError:
            if not self.args.quiet:
                print(
                    "pyperclip module required for clipboard functionality",
                    file=sys.stderr,
                )

    def process(self):
        try:
            # Handle base processing operation calls
            self.process_files()  # For file from input/directory passed
            self._map_op_()  # Camera and screenshot functionality

            if not self.all_results:
                if not self.args.quiet:
                    print("No QR codes found", file=sys.stderr)
                return 1

            # Process results
            self.decoded_data = [result["data"] for result in self.all_results]

            # Handle output based on flags
            self._map_ouputs_()

            # Handle (URL opening, Copy to clipboard (only first result))
            self._map_flags_()

            # Print to console (default behavior)
            if self.args.print and not self.args.quiet:
                for i, data in enumerate(self.decoded_data):
                    print(f"QR Code {i + 1}: {fg.GREEN_FG}{data}{RESET}")

            return 0

        except Exception as e:
            raise
            print(f"Error: {str(e)}", file=sys.stderr)
            return 1


if __name__ == "__main__":
    sys.exit(main())
