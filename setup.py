from setuptools import setup, find_packages

# Get the long description from the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='mongodriver',
    version='1.3.3',
    license='MIT',
    author="Jake Strouse",
    author_email='jstrouse@meh.llc',
    packages=find_packages(),
    url='https://github.com/jakestrouse00/mongodriver',
    keywords='mongodb',
    install_requires=[
        'pymongo==4.4.1',
        'pymongo[srv]==4.4.1',
        'motor==3.2.0',
        'motor[srv]==3.2.0'
    ],
    description='Object-oriented interactions with MongoDB',
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",

)
