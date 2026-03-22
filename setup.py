from setuptools import setup, find_packages

setup(
    name="deepcsv",
    version="0.2.0",
    author="Abdullah Bakr",
    description="Automatically walks folders and converts list strings to lists in CSV/XLSX files",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=["pandas"],
    python_requires=">=3.7",
)
