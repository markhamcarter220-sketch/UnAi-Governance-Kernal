"""
Setup configuration for governance-kernel package.
"""

from setuptools import setup, find_packages

with open("../../README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="governance-kernel",
    version="1.0.0",
    author="Mark Carter",
    author_email="governance@governance-kernel.org",
    description="Universal framework for preventing authority accumulation in AI and complex systems",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/governance-kernel/governance-kernel",
    project_urls={
        "Bug Tracker": "https://github.com/governance-kernel/governance-kernel/issues",
        "Documentation": "https://github.com/governance-kernel/governance-kernel/docs",
        "Source Code": "https://github.com/governance-kernel/governance-kernel",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Systems Administration",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        # Minimal dependencies for production use
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.990",
        ],
    },
    entry_points={
        "console_scripts": [
            "governance-kernel=governance_kernel.cli:main",
        ],
    },
)
