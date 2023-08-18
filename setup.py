import os
import subprocess
from os import path
from codecs import open
from setuptools import setup, find_packages

HERE = path.abspath(path.dirname(__file__))

with open(path.join(HERE, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

remote_version = (
    subprocess.run(["git", "describe", "--tags"], stdout=subprocess.PIPE)
    .stdout.decode("utf-8")
    .strip()
)

if "-" in remote_version:
    v, i, s = remote_version.split("-")
    remote_version = v + "+" + i + ".git." + s

assert "-" not in remote_version
assert "." in remote_version

assert os.path.isfile("dxlib/version.py")
with open("dxlib/VERSION", "w", encoding="utf-8") as fh:
    fh.write("%s\n" % remote_version)

setup(
    name="dxlib",
    version=remote_version,
    description="Quantitative Methods for Finance",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/delphos-quant/dxlib",
    author="Rafael Zimmer",
    author_email="rzimmerde@gmail.com",
    license="MIT",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent"
    ],
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
)
