#!/usr/bin/env python3
"""
IMM-Romania - Email, Calendar, and Tasks for Exchange on-premises.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="imm-romania",
    version="1.0.0",
    author="OpenClaw Community",
    author_email="community@openclaw.ai",
    description="Email, Calendar, and Tasks for Exchange on-premises (2016/2019)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/openclaw/imm-romania",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    install_requires=[
        "exchangelib>=5.0.0",
        "requests_ntlm>=1.1.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
        ],
    },
    scripts=[
        "scripts/cli.py",
    ],
    entry_points={
        "console_scripts": [
            "imm-romania=cli:main",
        ],
    },
)