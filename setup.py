from setuptools import setup, find_packages

setup(
    name='ops_stack',
    version='1.0',
    packages=find_packages(),
    url='https://github.com/ust-ops/ops_stack',
    install_requires=[
        'setuptools~=46.1.3',
        'requests~=2.23.0',
        'pyfiglet~=0.8.post1',
        'boto3~=1.13.1',
        'pytz~=2020.1',
        'xmltodict~=0.12.0',
        'pysftp~=0.2.9',
        'httplib2~=0.17.3',
        'google-api-python-client~=1.8.2',
        'oauth2client~=4.1.3',
        'jira~=2.0.0',
        'PyInquirer~=1.0.3',
        'botocore~=1.16.26',
        'PyYAML~=5.3.1'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    author='Ruwan Mettananda',
    author_email='ruwan.m@ustocktrade.com',
    description='ustocktrade ops stack (gen2) for automation'
)
