from setuptools import setup, find_packages

setup(
    name="goputn",
    version="0.3.0",
    description="Moteur gopuTN — terminal client pour gopHub",
    author="Ceose",
    packages=find_packages(),
    include_package_data=True,
    
    entry_points={
        "console_scripts": [
            "gopuTN=engine:main",
            "gotn=gopuTN.gotn.cli:main",
            "goputn=engine:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
