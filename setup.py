from pathlib import Path

from setuptools import find_packages, setup

readme = (Path(__file__).parent / "README.md").read_text()

setup(
    name='nicovideo.py',
    version='0.0.2',
    description='Get nicovideo\'s video metadata.',
    long_description=readme,
    long_description_content_type='text/markdown',
    author='okaits#7534',
    author_email='okaits@okaits7534.mydns.jp',
    url='https://github.com/okaits/nicovideo.py',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Natural Language :: Japanese',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    keywords=[
        'nicovideo'
    ],
    license='GNU Lesser General Public License 3.0',
    packages=find_packages()
)
