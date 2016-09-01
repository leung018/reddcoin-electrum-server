from setuptools import setup
import os


basedir = os.path.abspath(os.path.dirname(__file__))


def read_file(filename):
    f = open(os.path.join(basedir, filename))
    try:
        return f.read()
    finally:
        f.close()


VERSION = '1.0'
setup(
    name="reddcoin-electrum-server",
    version=VERSION,
    scripts=['run_electrum_server.py', 'electrum-server', 'electrum-configure', 'electrum.conf.sample'],
    install_requires=['plyvel', 'jsonrpclib', 'irc>=11, <=14.0'],
    package_dir={'electrum_server': 'src'},
    py_modules=[
        'electrum_server.__init__',
        'electrum_server.utils',
        'electrum_server.storage',
        'electrum_server.deserialize',
        'electrum_server.networks',
        'electrum_server.blockchain_processor',
        'electrum_server.server_processor',
        'electrum_server.processor',
        'electrum_server.version',
        'electrum_server.ircthread',
        'electrum_server.stratum_tcp'
    ],
    description="Reddcoin Electrum server",
    author="Thomas Voegtlin, John Nash, Larry Ren",
    author_email="thomasv1@gmx.de, john@redd.ink, ren@reddcoin.com",
    maintainer="John Nash",
    maintainer_email="john@redd.ink",
    license="MIT Licence",
    url="https://github.com/reddcoin-project/reddcoin-electrum-server",
    download_url="https://pypi.python.org/packages/source/l/reddcoin-electrum-server/reddcoin-electrum-server-%s.tar.gz" % VERSION,
    long_description=read_file('README.rst'),
    platforms="All",
    classifiers=[
        'Environment :: Console',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT Licence',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'Topic :: Office/Business :: Financial',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
