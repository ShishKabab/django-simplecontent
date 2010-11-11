from distutils.core import setup

setup(
	name = "django-simplecontent",
	version = "0.1",
	author = "Vincent den Boer",
	author_email = "vincent@shishkabab.net",
	description = "A simple way to test static content and templates and writing them to disk when you're finished",
	download_url = TODO,
	url = TODO,
	packages = ['django_simplecontent'],
	#package_data = {'django_simplecontent': ['templates/dajaxice/*']},
	classifiers = [
		'Environment :: Web Environment',
		'Framework :: Django',
		'Intended Audience :: Developers',
		'License :: OSI Approved :: BSD License',
		'Operating System :: OS Independent',
		'Programming Language :: Python',
		'Topic :: Utilities'
	]
)
