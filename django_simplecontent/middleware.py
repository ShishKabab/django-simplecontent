import os

from django.conf import settings
from django.http import HttpResponse
from common import renderTemplate, importClass, makeProcessor
from template import DjangoTemplate

class ContentMiddleware(object):
	templateManager = getattr(settings, 'SIMPLECONTENT_TEMPLATEMANAGER', 'django_simplecontent.template.DjangoTemplateManager')
	templateManager = importClass(templateManager)()
	pageProcessors = getattr(settings, 'SIMPLECONTENT_LIVE_PROCESSORS', ())
	pageProcessors = [makeProcessor(entry) for entry in pageProcessors]

	def process_response(self, request, response):
		if response.status_code == 404:
			fileInfo = {
				'srcPath': os.path.join(settings.SIMPLECONTENT_ROOT, request.path[1:]),
				'relPath': request.path[1:],
				'outPath': None
			}
			if os.access(fileInfo["srcPath"], os.F_OK):
				return HttpResponse(renderTemplate(
					fileInfo,
					self.templateManager,
					pageProcessors = self.pageProcessors
				))
		return response