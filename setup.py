import setuptools

setuptools.setup(
    name="iterwrite",
    version="0.0.0-a",
    license="MIT",
    packages=setuptools.find_packages(exclude=["tests"]),
    author="James Ross",
    author_email="jamespatross@gmail.com",
    description="Print tidy results.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/jamesross2/iterwrite",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[],
    test_suite="pytest",
    tests_require=["pytest", "pytest-cov", "black", "isort", "darglint"],
)
