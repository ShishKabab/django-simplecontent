import os

from django.conf import settings
from django.http import HttpResponse
from django_simplecontent.common import renderTemplate, makeProcessor, getTemplateManager, getPageProcessors, getDynamicPages
from django_simplecontent.template import DjangoTemplate

class ContentMiddleware(object):
	templateManager = getTemplateManager()
	pageProcessors = getPageProcessors(includeStatic = False)
	rootUrl = getattr(settings, "SIMPLECONTENT_ROOT_URL", None) or "/"
	dynamicPages = getDynamicPages()

	def process_response(self, request, response):
		if response.status_code == 404:
			if not request.path.startswith(self.rootUrl):
				return response

			path = request.path[len(self.rootUrl):]
			template = None
			variables = {}
			fileInfo = {
				'srcPath': os.path.join(settings.SIMPLECONTENT_ROOT, path),
				'relPath': path,
				'outPath': None
			}
			if not os.access(fileInfo["srcPath"], os.F_OK):
				page = self.dynamicPages.get(path.strip("/"))
				if not page:
					return response

				info = page(self.templateManager)
				fileInfo['srcPath'] = info['srcPath']
				template = info['template']
				variables = info['variables']

			return HttpResponse(renderTemplate(
				fileInfo,
				self.templateManager,
				pageProcessors = self.pageProcessors,
				template = template,
				variables = variables
			))

		return response