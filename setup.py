from pathlib import Path

from setuptools import find_packages, setup

setup(
	name='bring-python-api',
	version='1.0.2',
	long_description=Path('README.md').read_text(encoding='utf8'),
	long_description_content_type='text/markdown',
	python_requires='>=3.8',
	packages=find_packages(),
	include_package_data=True,
	url='https://github.com/Psychokiller1888/bring-api',
	license='GPL-3.0',
	author='Psychokiller1888',
	maintainer='Psychokiller1888',
	author_email='laurentchervet@bluewin.ch',
	description='Bring! web api for Python',
	install_requires=[
		'requests~=2.26.0'
	],
	classifiers=[
		"Development Status :: 5 - Production/Stable",
		"Environment :: Web Environment",
		"Intended Audience :: Developers",
		"License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
		"Operating System :: OS Independent",
		"Programming Language :: Python :: 3.8"
	]
)
