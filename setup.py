from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="dupimgsearch",
    version="0.1.1",
    author="yurielie",
    description="CLI tools to search duplicate images in given directories",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yurielie/dupimgsearch",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points = {
        'console_scripts': ['dupimgsearch = dupimgsearch.dupimgsearch:main']
    },
    python_requires='>=3.9',
)