# type: ignore

from setuptools import setup, find_packages

setup(
    name='proj',
    version='0.0.1',
    packages=find_packages(),
    install_requires=[
    ],
    extras_require={
        "progressbar": [
            "enlighten>1.0.0,<2.0.0"
        ],
        "test": [
            "pytest>=9.0.0,<10.0.0",
            "pytest-skip-slow==0.0.5",
            "pytest-xdist>=3.0.0,<4.0.0",
            'typing-extensions>=4.0.0,<5.0.0',
        ],
    },
    entry_points={
        'console_scripts': ['proj = proj.__main__:entrypoint' ]
    },
)
