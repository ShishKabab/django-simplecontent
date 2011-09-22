import os
from os.path import join as joinPath
from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django_simplecontent.common import buildHtml

class Command(BaseCommand):
	args = '[--force] <output_directory>'
	help = 'Renders content in content root and stores it in <output_directory>'
	option_list = BaseCommand.option_list + (
		make_option('--force',
			action='store_true',
			dest='force',
			default=False,
			help='Generates all content ignoring page processor opinions'),
		)

	def handle(self, *args, **options):
		buildHtml(outputRoot = args[0], allowAbort = not options["force"])
