from setuptools import setup
import os


basedir = os.path.abspath(os.path.dirname(__file__))


def read_file(filename):
    f = open(os.path.join(basedir, filename))
    try:
        return f.read()
    finally:
        f.close()


VERSION = '0.9.2'
setup(
    name="reddcoin-electrum-server",
    version=VERSION,
    scripts=['run_electrum_server', 'electrum-server', 'electrum-configure', 'electrum.conf.sample'],
    install_requires=['plyvel', 'jsonrpclib', 'tinyrpc', 'irc', 'gevent', 'gevent-websocket', 'werkzeug', 'requests'],
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
        'electrum_server.stratum_tcp',
        'electrum_server.stratum_http'
    ],
    description="Reddcoin Electrum server",
    author="Thomas Voegtlin, Larry Ren",
    author_email="thomasv1@gmx.de, ren@reddcoin.com",
    maintainer="Larry Ren",
    maintainer_email="ren@reddcoin.com",
    license="GNU Affero GPLv3",
    url="https://wallet.reddcoin.com",
    download_url="https://pypi.python.org/packages/source/l/reddcoin-electrum-server/reddcoin-electrum-server-%s.tar.gz" % VERSION,
    long_description=read_file('README.rst'),
    platforms="All",
    classifiers=[
        'Environment :: Console',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'Topic :: Office/Business :: Financial',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
