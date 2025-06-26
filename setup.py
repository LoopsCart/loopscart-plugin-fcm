from setuptools import setup, find_packages

setup(
    name='fcm_messaging',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Django>=4.2.7",
        "firebase-admin>=5.0.0",
        "djangorestframework>=3.14.0",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Framework :: Django",
        "Framework :: Django :: 4.2",
    ],
)
