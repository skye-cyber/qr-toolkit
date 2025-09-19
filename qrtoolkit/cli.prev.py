import argparse
import sys
import os
from tqdm.asyncio import tqdm
from datetime import datetime
from .core.decoder import QRDecoder
from .core.processor import DataProcessor
from .outputs.json_handler import JSONHandler
from .outputs.url_handler import URLHandler
from .outputs.text_handler import TextHandler


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

    decoder = QRDecoder()
    processor = DataProcessor()
    all_results = []

    try:
        # Process files
        for file_path in tqdm(input_files):
            if not args.quiet:
                print(f"Processing: {file_path}")
            results = decoder.decode_from_image(file_path)
            all_results.extend(results)

        # Process camera if requested
        if args.camera:
            if not args.quiet:
                print("Scanning from camera...")
            results = decoder.decode_from_video(args.timeout)
            all_results.extend(results)

        # TODO: Implement screenshot functionality
        if args.screenshot:
            if not args.quiet:
                print("Screenshot functionality not yet implemented")

        if not all_results:
            if not args.quiet:
                print("No QR codes found", file=sys.stderr)
            return 1

        # Process results
        decoded_data = [result["data"] for result in all_results]

        # Handle output based on flags
        if args.json:
            # Handle 2FA secrets specifically
            twofa_secrets = []
            for data in decoded_data:
                if processor.is_2fa_secret(data):
                    twofa_secrets.append(data)
                else:
                    # Check if data contains 2FA secrets
                    secrets = processor.extract_2fa_secrets(data)
                    twofa_secrets.extend(secrets)

            if twofa_secrets:
                output_file = (
                    args.output
                    or f"2fa_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                )
                JSONHandler.save_2fa_secrets(twofa_secrets, output_file)
                if not args.quiet:
                    print(f"2FA secrets saved to: {output_file}")
            elif args.output:
                # Save generic data as JSON
                JSONHandler.save_generic_data(decoded_data, args.output)
                if not args.quiet:
                    print(f"Data saved to JSON: {args.output}")

        elif args.text and args.output:
            # Save as text file
            text_content = "\n".join(decoded_data)
            TextHandler.save_to_file(text_content, args.output)
            if not args.quiet:
                print(f"Data saved to text file: {args.output}")

        # Handle URL opening
        if args.open_url:
            for data in decoded_data:
                if processor.is_url(data):
                    URLHandler.open_url(data)
                    if not args.quiet:
                        print(f"Opened URL: {data}")

        # Copy to clipboard (only first result)
        if args.copy and decoded_data:
            try:
                import pyperclip

                pyperclip.copy(decoded_data[0])
                if not args.quiet:
                    print("Copied to clipboard")
            except ImportError:
                if not args.quiet:
                    print(
                        "pyperclip module required for clipboard functionality",
                        file=sys.stderr,
                    )

        # Print to console (default behavior)
        if args.print and not args.quiet:
            for i, data in enumerate(decoded_data):
                print(f"QR Code {i + 1}: {data}")

        return 0

    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
