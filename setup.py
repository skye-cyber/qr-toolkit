import os
from setuptools import find_namespace_packages, setup


DESCRIPTION = "A toolkit for QR code processing and 2FA secret management"
EXCLUDE_FROM_PACKAGES = ["build", "dist", "test", "src", "*~", "*.db", "*.prev*"]


setup(
    name="qr-toolkit",
    author="wambua",
    author_email="swskye17@gmail.com",
    version=open(os.path.abspath("version.txt")).read(),
    packages=find_namespace_packages(exclude=EXCLUDE_FROM_PACKAGES),
    description=DESCRIPTION,
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://pypi.org/project/qr-toolkit/",
    entry_points={
        "console_scripts": [
            "qrscan=qrtoolkit:main",
            "qrtool=qrtoolkit:main",
            "qrtoolkit=qrtoolkit:main",
        ],
    },
    python_requires=">=3.12",
    install_requires=[
        "setuptools",
        "wheel",
        "argparse",
        "opencv-python",
        "pyzbar",
        "Pillow",
        "pyperclip",
    ],
    include_package_data=True,
    package_data={
        # 'pkg': ['dirname/**', 'config.json'],
    },
    # include_dirs=[...],
    zip_safe=False,
    license="GNU v3",
    keywords=["qr-code", "2fa", "otp", "authentication"],
    classifiers=[
        "Environment :: Console",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
)
