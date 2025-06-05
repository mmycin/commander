from setuptools import setup
import subprocess
import sys
import os

# Read requirements from requirements.txt
def read_requirements():
    with open('requirements.txt') as f:
        return f.read().splitlines()

# Custom post-install command
class CustomInstallCommand:
    def run(self):
        # Install requirements
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])

        # Run pyinstaller command
        subprocess.check_call([
            'pyinstaller',
            '--onefile',
            '--name', 'commander',
            'main.py'
        ])

# Run the custom install command if setup.py is run directly
if __name__ == '__main__':
    setup(
        name='commander',
        version='1.0',
        install_requires=read_requirements(),
        description='Commander CLI app',
        author='Tahcin Ul Karim (Mycin)',
        cmdclass={},  # We’re manually running post-install commands below instead
    )

    # Run custom post-install actions
    CustomInstallCommand().run()
