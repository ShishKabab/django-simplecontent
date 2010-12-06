import os
from os.path import join as joinPath
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django_simplecontent.common import buildHtml

class Command(BaseCommand):
	args = '<output_directory>'
	help = 'Renders content in content root and stores it in <output_directory>'

	def handle(self, *args, **options):
		buildHtml(outputRoot = args[0])
