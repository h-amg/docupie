# setup.py
from setuptools import setup, find_packages

setup(
    name="docupie",
    version="0.1.0",
    description="An advanced document processing tool that leverages AI to extract structured data from PDFs",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Husam Gibreel",
    author_email="husamgibreel@gmail.com",
    url="https://github.com/h-amg/docupie",
    packages=find_packages(),
    install_requires=[
        "pytesseract==0.3.13",
        "Spire.Doc==13.1.0",
        "plum-dispatch==1.7.4",
        "openai==1.59.8",
        "requests==2.32.3",
        "pdf2image==1.17.0",
    ],
    python_requires=">=3.10.4",
)
