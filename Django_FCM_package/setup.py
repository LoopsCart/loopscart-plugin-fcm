from setuptools import find_packages, setup

setup(
    name="fcm-messaging",
    version="0.1",
    packages=find_packages(include=["FCM_Package", "FCM_Package.*", "api", "api.*"]),
    install_requires=[],
)
