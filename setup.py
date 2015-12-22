from setuptools import setup

dev_pkgs=[
        'bumpversion==0.5.3',
        'pytest-xdist==1.13.1',
        ]

install_pkgs=[
        '',
        ]

tests_pkgs=[
        'pytest==2.8.5',
        'mock==1.3.0'
        ]

setup(
        name='mcm',
        version='0.1.0',
        description='Mikrotik configuration manager.',
        url='http://github.com/luqasz/mcm',
        author='Łukasz Kostka',
        author_email='lukasz.kostka@netng.pl',
        license='MIT',
        packages=['mcm'],
        install_requires=install_pkgs,
        tests_require=tests_pkgs,
        extras_require={
            'tests': tests_pkgs,
            'develop': dev_pkgs,
        },
        entry_points={
            'console_scripts': 'mcm=mcm.cli:main'
        },
        zip_safe=False
)
