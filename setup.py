from setuptools import setup, find_packages

setup(
    name='harder',
    version='0.0.1',
    author='Christopher Brown',
    author_email='io@henrian.com',
    url='https://github.com/chbrown/harder',
    keywords='cd dvd media transfer disk drive luddite',
    description='Automatically copy soft media, like CDs and DVDs, to your hard drive',
    long_description=open('README.md').read(),
    license=open('LICENSE').read(),
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        # https://pypi.python.org/pypi?:action=list_classifiers
        'Development Status :: 1 - Alpha',
        'License :: OSI Approved :: MIT License',
    ],
    install_requires=[
        'pyudev',  # http://pyudev.readthedocs.org/en/latest/
    ],
    entry_points={
        'console_scripts': [
            'harder = harder.cli:main',
        ],
    },
)
