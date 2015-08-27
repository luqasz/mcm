from setuptools import setup

dev_pkgs=[
        'bumpversion==0.5.3',
        ]

install_pkgs=[
        '',
        ]

tests_pkgs=[
        'nose==1.3.7',
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
        setup_requires=dev_pkgs,
        install_requires=install_pkgs,
        tests_require=tests_pkgs,
        extras_require={'tests': tests_pkgs},
        # entry_points={
        #     'console_scripts': 'mcm=mcm.cli:main'
        # },
        zip_safe=False
)
