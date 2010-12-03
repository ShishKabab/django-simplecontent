import os
from os.path import join as joinPath
from django.core.management.base import BaseCommand, CommandError
from django.template import Context, Template
from django.conf import settings
from django_simplecontent.common import getTemplateManager, getPageProcessors

class Command(BaseCommand):
	args = '<output_directory>'
	help = 'Renders content in content root and stores it in <output_directory>'
	joinPath = os.path.join

	templateManager = getTemplateManager()
	pageProcessors = getPageProcessors(includeStatic = True)

	def handle(self, *args, **options):
		if not args[0].endswith("/"):
			args[0] += "/"
		self.handleDir(settings.SIMPLECONTENT_ROOT, args[0], "")
		for pageProcessor in self.pageProcessors:
			pageProcessor.processEnd()

	def handleDir(self, contentRoot, outputRoot, directory):
		try:
			os.makedirs(os.path.join(outputRoot, directory))
		except: pass

		for entry in os.listdir(joinPath(contentRoot, directory)):
			fileInfo = {
				'relPath': joinPath(directory, entry),
				'srcPath': joinPath(contentRoot, entry),
				'outPath': joinPath(outputRoot, entry)
			}
			if os.path.isdir(fileInfo["srcPath"]):
				self.handleDir(contentRoot, outputRoot, fileInfo["relPath"])
				continue

			content = renderTemplate(fileInfo, self.templateManager, allowAbort = True, pageProcessors = self.pageProcessors)
			if content:
				open(fileInfo["outPath"], 'w').write(content.encode('utf8'))
