"""
Configuration du package Punk Eco.

Ce fichier permet d'installer le package en mode développement avec pip.
"""

import os
from setuptools import setup, find_packages

# Lire la description du projet depuis le README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Lire les dépendances depuis requirements.txt
def read_requirements(filename='requirements.txt'):
    """Lit les dépendances depuis un fichier de requirements."""
    requirements = []
    if not os.path.exists(filename):
        return requirements
        
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                # Supprimer les commentaires en fin de ligne
                if '#' in line:
                    line = line.split('#')[0].strip()
                requirements.append(line)
    return requirements

# Configuration du package
setup(
    name="punk_eco",
    version="0.1.0",
    author="Punk Eco Team",
    author_email="contact@punk-eco.ma",
    description="Moroccan Economy Data Warehouse - Suivi des indicateurs économiques marocains",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/punk-eco/moroccan-economy-dashboard",
    project_urls={
        'Bug Reports': 'https://github.com/punk-eco/moroccan-economy-dashboard/issues',
        'Source': 'https://github.com/punk-eco/moroccan-economy-dashboard',
    },
    packages=find_packages(include=['app', 'app.*']),
    package_dir={'': '.'},
    include_package_data=True,
    zip_safe=False,
    python_requires='>=3.8',
    install_requires=read_requirements(),
    extras_require={
        'dev': read_requirements('requirements-dev.txt'),
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Framework :: Flask",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    entry_points={
        'console_scripts': [
            'punk_eco=app.cli:main',
        ],
    },
)
