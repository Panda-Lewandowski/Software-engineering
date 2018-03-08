from setuptools import setup, find_packages

setup(
    name='polyeditor',
    version='polyeditor.__version__',
    packages=find_packages(),
    entry_points={
        'console_scripts':
            ['polyeditor = main:run_editor']
        },
    install_requires=[
        'PyQt5==5.10'
    ]
)
