import re
from setuptools import setup

# Helper functions

def get_info():
    """Returns tool's details as a dict."""
    info = None
    with open('gitchm/__init__.py', 'r', encoding='utf-8') as f:
        info = dict(re.findall(
            r"__(\w+)__ = '([^']+)'$",
            f.read(),
            re.MULTILINE
        ))

    with open('README.md', 'r', encoding='utf-8') as g:
        info['long_description'] = g.read()

    return info

# Details

INFO = get_info()
REQUIRES = [
    'GitPython>=3.1.3',
    'python-dateutil>=2.8.1',
]
TEST_REQUIRES = [
    'pytest>=5.4.3',
    'pytest-asyncio>=0.12.0',
    'pytest-mock>=3.1.1',
]
PACKAGES = ['gitchm']


# Setup

setup(
    name=INFO['title'],
    version=INFO['version'],
    description=INFO['short_description'],
    long_description=INFO['long_description'],
    long_description_content_type="text/markdown",
    author=INFO['author'],
    author_email=INFO['author_email'],
    license=INFO['license'],
    url=INFO['url'],
    packages=PACKAGES,
    install_requires=REQUIRES,
    extras_require={'tests': TEST_REQUIRES},
    python_requires='>=3.8',
    entry_points = {'console_scripts': ['gitchm = gitchm.main:main']},
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.8',
        'Operating System :: POSIX',
    ],
    keywords=(
        'git commit history repo repository working tree directory '
        'mirror replicate replicator reproduce'
    ),
)
