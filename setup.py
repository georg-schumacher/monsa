from setuptools import setup, find_packages

setup(
    name="monsa",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[],
    entry_points={"console_scripts": ["monsa=monsa.monsa:main"]},
    author="Superstein",
    author_email="superstein@superstein.com",
    description="monsa - MOvie aNd Series App",
    long_description=open("readme.md").read(),
    long_description_content_type="text/markdown",
    url="htttps://github.com/dein_username/monsa",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
