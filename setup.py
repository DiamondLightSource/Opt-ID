from setuptools import setup, find_packages


setup(
    name='opt-id',
    description='Optimisation of IDs using Python and Opt-AI',
    url='https://github.com/DiamondLightSource/Opt-ID',
    author='Mark Basham',
    author_email='mark.basham@diamond.ac.uk',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.7',
        'Operating System :: POSIX :: Linux',
    ],
    license='Apache License, Version 2.0',
    zip_safe=False,
)
