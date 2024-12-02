from setuptools import setup, find_packages

setup(
    name='tsmith',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'openrouter',
    ],
    entry_points={
        'console_scripts': [
            'tsmith=tsmith:main',
        ],
    },
    author='Your Name',
    author_email='your.email@example.com',
    description='A script to process files with Openrouter API',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/tsmith',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    include_package_data=True,
)
