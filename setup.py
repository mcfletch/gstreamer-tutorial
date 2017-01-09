#! /usr/bin/env python
from setuptools import setup

version = '1.0.0'

if __name__ == "__main__":
    extraArguments = {
        'classifiers': [
            """Programming Language :: Python :: 2""",
            """Programming Language :: Python :: 3""",
            """Topic :: Software Development :: Libraries :: Python Modules""",
            """Intended Audience :: Developers""",
        ],
        'keywords': 'gstreamer,mpeg,hls',
        'platforms': ['Linux'],
    }
    ### Now the actual set up call
    setup (
        name = "gstdemo",
        version = version,
        url = "https://github.com/mcfletch/gstreamer-tutorial",
        description = "Demonstrates GStreamer Python server-side API usage",
        author = "Mike C. Fletcher",
        author_email = "mcfletch@vrplumber.com",
        license = "MIT",
        package_dir = {
            'gstdemo':'gstdemo',
        },
        packages = [
            'gstdemo',
        ],
        options = {
            'sdist':{'force_manifest':1,'formats':['gztar','zip'],},
        },
        entry_points = {
            'console_scripts': [
                'gst-demo = gstdemo.demo:main',
            ],
        },
        **extraArguments
    )

