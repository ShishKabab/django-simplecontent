import os

from django.conf import settings
from django.http import HttpResponse
from django_simplecontent.common import renderTemplate, makeProcessor, getTemplateManager, getPageProcessors
from django_simplecontent.template import DjangoTemplate

class ContentMiddleware(object):
	templateManager = getTemplateManager()
	pageProcessors = getPageProcessors(includeStatic = False)

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