from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent

readme = (this_directory / "README.md").read_text(encoding="utf-8")
changelog = (this_directory / "CHANGELOG.md").read_text(encoding="utf-8")

setup(
    name="deepcsv",
    version="0.6.7",
    author="Abdullah Bakr",
    author_email="abdubakora1232@gmail.com",
    description="Automatically processes data files in directories, converts array-like strings to NumPy arrays, detects and fixes data type issues, and saves results as optimized Parquet files and MORE!",
    long_description=readme + "\n\n" + changelog,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=["pandas", "pyarrow", "requests"],
    python_requires=">=3.7",
    url="https://github.com/abdubakr77/deepcsv",
    license="MIT",
    keywords="data-processing pandas numpy etl data-cleaning file-conversion automation parquet bulk-conversion",
    classifiers=[
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],    
    project_urls={
        "Source": "https://github.com/abdubakr77/deepcsv",
        "Tracker": "https://github.com/abdubakr77/deepcsv/issues",
    },
)
