from setuptools import setup

setup(
    name="electrum-server",
    version="0.9",
    scripts=['run_electrum_server', 'electrum-server'],
    install_requires=['plyvel', 'jsonrpclib', 'irc'],
    package_dir={'electrumserver': 'src'},
    py_modules=[
        'electrumserver.__init__',
        'electrumserver.utils',
        'electrumserver.storage',
        'electrumserver.deserialize',
        'electrumserver.networks',
        'electrumserver.blockchain_processor',
        'electrumserver.server_processor',
        'electrumserver.processor',
        'electrumserver.version',
        'electrumserver.ircthread',
        'electrumserver.stratum_tcp',
        'electrumserver.stratum_http'
    ],
    description="Reddcoin Electrum Server",
    author="Thomas Voegtlin, Larry Ren",
    author_email="thomasv1@gmx.de, ren@reddcoin.com",
    license="GNU GPLv3",
    url="https://reddwallet.org",
    long_description="""Reddcoin Electrum Server"""
)
