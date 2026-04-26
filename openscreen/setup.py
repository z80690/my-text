from setuptools import setup, find_packages

setup(
    name="openscreen",
    version="1.0.0",
    packages=find_packages(),
    description="OpenScreen module",
    author="TRAE",
    author_email="trae@example.com",
    url="https://github.com/TRAE/openscreen",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'openscreen=openscreen.core.main:main',
        ],
    },
)