from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="dirmap",
    version="0.1.0",
    author="Catalin cighi",
    author_email="catalin.cighil@gmail.com",
    description="Map directory structure respecting .gitignore rules",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/catalincighi/directory-mapping",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "pathspec>=0.9.0",
        "PyYAML>=6.0",
    ],
    entry_points={
        "console_scripts": [
            "dirmap=dirmap.cli:main",
        ],
    },
)
