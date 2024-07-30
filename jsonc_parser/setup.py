from setuptools import setup

with open("README.md", "r", encoding="utf-8") as docs:
    long_description = docs.read()

setup(
    name="jsonc-parser",
    version="1.1.0",
    author="Nickolai Beloguzov",
    author_email="nickolai.beloguzov@gmail.com",
    description="A lightweight, native tool for parsing .jsonc files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=["jsonc_parser"],
    url="https://github.com/NickolaiBeloguzov/jsonc-parser",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Natural Language :: English",
    ],
    python_requires=">=3.5",
)
