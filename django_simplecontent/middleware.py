import os

from django.conf import settings
from django.http import HttpResponse
from django_simplecontent.common import renderTemplate, makeProcessor, getTemplateManager, getPageProcessors
from django_simplecontent.template import DjangoTemplate

class ContentMiddleware(object):
	templateManager = getTemplateManager()
	pageProcessors = getPageProcessors(includeStatic = False)
	rootUrl = settings.SIMPLECONTENT_ROOT_URL or "/"

	def process_response(self, request, response):
		if response.status_code == 404:
			if not request.path.startswith(self.rootUrl):
				return response

			path = request.path[len(self.rootUrl):]
			fileInfo = {
				'srcPath': os.path.join(settings.SIMPLECONTENT_ROOT, path),
				'relPath': path,
				'outPath': None
			}
			if os.access(fileInfo["srcPath"], os.F_OK):
				return HttpResponse(renderTemplate(
					fileInfo,
					self.templateManager,
					pageProcessors = self.pageProcessors
				))
		return response