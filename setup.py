from setuptools import setup

setup(
    name='fststr',
    version='0.5',
    packages=['fststr',],
    scripts=['bin/applyfst.py'],
    license='MIT license',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
)
