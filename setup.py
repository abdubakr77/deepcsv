from setuptools import setup, find_packages

setup(
    name="deepcsv",
    version="0.4.0",
    author="Abdullah Bakr",
    author_email="abdubakora1232@gmail.com",
    description="Automatically walks through folders and subfolders, finds all CSV and XLSX files, detects and fixes data issues, and saves the results as Parquet files while keeping the exact same folder structure.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=["pandas", "pyarrow"],
    python_requires=">=3.7",
    url="https://github.com/abdubakr77/deepcsv",
    project_urls={
        "Source": "https://github.com/abdubakr77/deepcsv",
        "Tracker": "https://github.com/abdubakr77/deepcsv/issues",
    },
)
