from setuptools import setup, find_packages

# Get the long description from the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='mongodriver',
    version='1.2.5',
    license='MIT',
    author="Jake Strouse",
    author_email='jstrouse@meh.llc',
    packages=find_packages('src'),
    url='https://github.com/jakestrouse00/mongodriver',
    package_dir={'': 'src'},
    keywords='mongodb',
    install_requires=[
        'pymongo==3.12.0',
        'pymongo[srv]'
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
