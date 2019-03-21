import codecs
import os
import re
import sys
from shutil import rmtree

from setuptools import Command, find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))

version = '0.0.1'
changes = os.path.join(here, 'CHANGES.rst')
match = r'^#*\s*(?P<version>[0-9]+\.[0-9]+(\.[0-9]+)?)$'
with codecs.open(changes, encoding='utf-8') as changes:
    for line in changes:
        res = re.match(match, line)
        if res:
            version = res.group('version')
            break


# Get the long description
with codecs.open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

# Get requirements.txt
with codecs.open(os.path.join(here, 'requirements.txt')) as f:
    install_requires = []
    for line in f:
        requirement = line.split("#", 1)[0].strip()
        if not requirement:
            continue

        if requirement.startswith("--"):
            continue

        install_requires.append(requirement)


class UploadCommand(Command):
    """Support setup.py publish."""

    description = 'Build and publish the package.'
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print('\033[1m{0}\033[0m'.format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status('Removing previous builds…')
            rmtree(os.path.join(here, 'dist'))
        except FileNotFoundError:
            pass

        self.status('Building Source distribution…')
        os.system('{0} setup.py sdist'.format(sys.executable))

        self.status('Uploading the package to PyPi via Twine…')
        os.system('twine upload dist/*')

        self.status('Pushing git tags…')
        os.system('git tag v{0}'.format(version))
        os.system('git push --tags')

        sys.exit()


setup(
    name='template-to-pdf',
    version=version,
    description='Tool for converting HTML templates to PDF',
    long_description=long_description,
    url='https://github.com/olist/template_to_pdf',
    author='Olist Developers',
    author_email='developers@olist.com',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Pre-processors',
        'Topic :: Software Development :: Testing',
    ],
    packages=find_packages(exclude=['tests*']),
    install_requires=install_requires,
    cmdclass={
        'upload': UploadCommand,
    },
)
