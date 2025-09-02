from setuptools import setup, find_packages

setup(
    name="rehab-exercise-planner",
    version="0.1.0",
    description="A tool for planning rehabilitation exercises.",
    author="Jannis Bauer",
    author_email="jannislb@gmail.com",
    packages=find_packages(),
    install_requires=[
        "pyqt5",
    ],
    python_requires=">=3.9",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)