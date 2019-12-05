
from setuptools import find_packages, setup

# get the dependencies and installs
with open("requirements.txt", "r", encoding="utf-8") as f:
    requires = [x.strip() for x in f if x.strip()]

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="pyvalet",
    version="0.2",
    author='Tyler Roberts',
    author_email='tcroberts@live.ca',
    description="BoC Valet API Wrapper",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tylercroberts/pyvalet",
    packages=find_packages(exclude=["tests"]),
    install_requires=requires,
    extras_require={
        "docs": [
            "sphinx>=1.6.3, <2.0",
            "sphinx_rtd_theme==0.4.1",
            "nbsphinx==0.3.4",
            "nbstripout==0.3.3",
            "recommonmark==0.5.0",
            "sphinx-autodoc-typehints==1.6.0",
            "sphinx_copybutton==0.2.5",
            "jupyter_client>=5.1.0, <6.0",
            "tornado>=4.2, <6.0",
            "ipykernel>=4.8.1, <5.0",
        ],
        "tests": ["pytest==5.2.1",
                  "pytest-cov==2.8.1",
                  "coverage-badge",
                  "coveralls"]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6'
)
