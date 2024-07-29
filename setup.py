from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='sqlalchemy_filters',
    version='0.1.0',
    packages=find_packages('lib'),
    package_dir={'': 'lib'},
    install_requires=[
        'pydantic>=2.8.2',
        'SQLAlchemy>=2.0.31',
        'starlette>=0.37.2,<0.38.0',
    ],
    python_requires='>=3.6',
    author='Murtazo Khurramov',
    author_email='murtazox04@gmail.com',
    description='A package for filtering SQLAlchemy queries.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/murtazox04/sqlalchemy-filters',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
