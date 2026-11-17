from setuptools import setup, find_packages

setup(
    name="clockify-logger",
    version="1.0.0",
    description="Enduring Planet Weekly Clockify Time Reconstruction, Logging & Client Hour Tracking Assistant",
    author="Abdul Hannan",
    author_email="abdul@enduringplanet.com",
    packages=find_packages(),
    py_modules=["run_logger"],
    install_requires=[
        "requests>=2.28.0",
        "python-dateutil>=2.8.2",
        "tabulate>=0.9.0",
    ],
    entry_points={
        "console_scripts": [
            "clockify-logger=run_logger:main",
        ],
    },
    python_requires=">=3.9",
)
