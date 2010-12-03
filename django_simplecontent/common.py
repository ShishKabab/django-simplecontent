from os.path import join as joinPath
from django.conf import settings
from django_simplecontent import processor

try:
	from importlib import import_module
except:
	from django.utils.importlib import import_module

def importClass(path):
	# Taken from django.core.handlers.base
	try:
		dot = path.rindex('.')
	except ValueError:
		raise ImportError('%s isn\'t a module' % path)

	mod, cls = path[:dot], path[dot+1:]
	try:
		mod = import_module(mod)
	except ImportError, e:
		raise ImportError('Error importing module %s: "%s"' % (mod, e))
	try:
		cls = getattr(mod, cls)
	except AttributeError:
		raise ImportError('Module "%s" does not define a "%s" class' % (mod, cls))

	return cls

def getTemplateManager():
	templateManager = getattr(settings, 'SIMPLECONTENT_TEMPLATEMANAGER', 'django_simplecontent.template.DjangoTemplateManager')
	templateManager = importClass(templateManager)()
	return templateManager

def getPageProcessors(includeStatic):
	pageProcessors = getattr(settings, 'SIMPLECONTENT_LIVE_PROCESSORS', ())
	if includeStatic:
		pageProcessors += getattr(settings, 'SIMPLECONTENT_STATIC_PROCESSORS', ())
	pageProcessors = [makeProcessor(entry) for entry in pageProcessors]

	return pageProcessors

def makeProcessor(entry):
	kwds = {}
	if isinstance(entry, tuple):
		path = entry[0]
		args = entry[1:]
	elif isinstance(entry, processor):
		path = entry.path
		args = entry.args
		kwds = entry.kwds
	else:
		path = entry
		args = ()

	return importClass(path)(*args, **kwds)

def renderTemplate(fileInfo, templateManager, allowAbort = False, pageProcessors = []):
	render = True
	for proccessor in pageProcessors:
		render &= proccessor.processFile(fileInfo) == True

	variables = {"fileInfo": fileInfo}
	for proccessor in pageProcessors:
		variables = proccessor.processVariables(fileInfo, variables)

	template = templateManager.getFromFile(fileInfo["srcPath"])
	for proccessor in pageProcessors:
		proccessor.processTemplate(fileInfo, variables, template)

	if render or not allowAbort:
		return template.render(variables)
