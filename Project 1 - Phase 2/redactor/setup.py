from setuptools import setup, find_packages
setup(
        name='redactor',
        version='1.0',
        author='Pramod Aravind Byakod',
        author_email='pramod.a.byakod-1@ou.edu',
        packages=find_packages(exclude=('tests', 'docs')),
        setup_requires=['pytest-runner'],
        tests_require=['pytest']
)
