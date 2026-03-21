from setuptools import setup, find_packages

setup(
    name="deepcsv",
    version="0.1.0",
    author="Abdullah Bakr",
    description="Automatically walks folders and converts list strings to lists in CSV/XLSX files",
    packages=find_packages(),
    install_requires=["pandas"],
    python_requires=">=3.7",
)
