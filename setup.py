from setuptools import setup, find_packages

setup(
    name="cprc",
    version="1.1.0",
    description="Crystal Pulse Resonant Core - Field Health Engine based on Jingmai Philosophy",
    author="luoxuejian000",
    packages=find_packages(),
    install_requires=["numpy>=1.24.0"],
    python_requires=">=3.8",
)
