from setuptools import setup, find_packages
import os
import re

# Read version from __init__.py
with open(os.path.join("dirmap", "__init__.py"), "r", encoding="utf-8") as f:
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", f.read(), re.M)
    if version_match:
        version = version_match.group(1)
    else:
        raise RuntimeError("Unable to find version string in __init__.py")

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="dirmap",
    version=version,
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
