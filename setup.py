
from setuptools import find_packages, setup

# get the dependencies and installs
with open("requirements.txt", "r", encoding="utf-8") as f:
    requires = [x.strip() for x in f if x.strip()]

setup(
    name="pyvalet",
    version="0.1",
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
        "tests": ["pytest",
                  "pytest-cov"]
    },
)
