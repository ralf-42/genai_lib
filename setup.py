#
# genai_lib
#
import os
 from setuptools import setup, find_packages
 

 def read_requirements():
  with open('requirements.txt') as f:
  return [line.strip() for line in f if line.strip() and not line.startswith('#')]
 

 setup(
  name='genai_lib',
  version='0.1.0',
  author='Ralf Bendig',
  author_email='',
  description='Leichtgewichtige Bibliothek für den Kurs GenAI.',
  long_description=open('README.md').read(),
  long_description_content_type='text/markdown',
  url='https://github.com/ralf-42/genai_lib',
  packages=find_packages(),
  install_requires=read_requirements(),
  classifiers=[
  "Development Status :: 3 - Alpha",
  "Intended Audience :: Developers",
  "Programming Language :: Python :: 3",
  "Programming Language :: Python :: 3.8",
  "Programming Language :: Python :: 3.9",
  "Programming Language :: Python :: 3.10",
  "Programming Language :: Python :: 3.11",
  "License :: OSI Approved :: MIT License",
  "Operating System :: OS Independent",
  ],
  python_requires=">=3.11",
 )