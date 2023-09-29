from setuptools import find_packages, setup

setup(
    name="freeparse",
    version="0.1",
    author="Roman Kochanov",
    author_email="",
    description="User-friendly text file parser",
    #url="",
    python_requires=">=3.6",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "pyparsing",
        "railroad-diagrams",
        "jeanny3",
        "beautifulsoup4",
    ],
    entry_points = {
        'console_scripts': ['freeparse=freeparse.command_line:main']
    }
)
