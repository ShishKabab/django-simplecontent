import os
import grp
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
		raise
		raise ImportError('Error importing module %s: "%s"' % (mod, e))
	try:
		cls = getattr(mod, cls)
	except AttributeError:
		raise
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

def getDynamicPages():
	dynamicPages = getattr(settings, 'SIMPLECONTENT_DYNAMIC_PAGES', {})
	for key, value in dynamicPages.items():
		dynamicPages[key] = importClass(value)

	return dynamicPages

def makeProcessor(entry):
	kwds = {}
	if isinstance(entry, basestring):
		path = entry
		args = ()
	elif isinstance(entry, tuple):
		path = entry[0]
		args = entry[1:]
	elif hasattr(entry, "path") and hasattr(entry, "args") and hasattr(entry, "kwds"):
		path = entry.path
		args = entry.args
		kwds = entry.kwds
	else:
		raise ImportError("Invalid processor entry: %s" % entry)

	return importClass(path)(*args, **kwds)

def renderTemplate(fileInfo, templateManager, allowAbort = False, pageProcessors = [], template = None, variables = {}):
	render = True
	for proccessor in pageProcessors:
		render &= proccessor.processFile(fileInfo) != False

	variables = variables.copy()
	variables["fileInfo"] = fileInfo
	for proccessor in pageProcessors:
		variables = proccessor.processVariables(fileInfo, variables)

	template = template or templateManager.getFromFile(fileInfo["srcPath"])
	for proccessor in pageProcessors:
		proccessor.processTemplate(fileInfo, variables, template)

	if render or not allowAbort:
		return template.render(variables)

def buildHtml(contentRoot = None, outputRoot = None, directory = "", allowAbort = True, templateManager = None, pageProcessors = None,
	umask = None, group = None):
	if not contentRoot:
		contentRoot = settings.SIMPLECONTENT_ROOT
	if not outputRoot:
		outputRoot = settings.SIMPLECONTENT_OUTPUT_ROOT
	if not directory and not contentRoot.endswith("/"):
		contentRoot += "/"
	if not templateManager:
		templateManager = getTemplateManager()
	if not pageProcessors:
		pageProcessors = getPageProcessors(includeStatic = True)
	if not umask:
		umask = getattr(settings, "SIMPLECONTENT_OUTPUT_UMASK", None)
	if not group:
		group = getattr(settings, "SIMPLECONTENT_OUTPUT_GROUP", None)
		group = group and grp.getgrnam(group).gr_gid

	try:
		os.makedirs(os.path.join(outputRoot, directory))
	except: pass

	for entry in os.listdir(joinPath(contentRoot, directory)):
		fileInfo = {
			'relPath': joinPath(directory, entry),
			'srcPath': joinPath(contentRoot, directory, entry),
			'outPath': joinPath(outputRoot, directory, entry),
			'outUmask': umask,
			'outGroup': group
		}
		if os.path.isdir(fileInfo["srcPath"]):
			buildHtml(contentRoot, outputRoot, fileInfo["relPath"], allowAbort, templateManager, pageProcessors)
			continue

		try:
			content = renderTemplate(fileInfo, templateManager, allowAbort = allowAbort, pageProcessors = pageProcessors)
		except Exception, e:
			print "Error rendering page '%s': %s" % (fileInfo["relPath"], e)
			continue

		if content:
			open(fileInfo["outPath"], 'w').write(content.encode('utf8'))
		if umask:
			os.chmod(fileInfo["outPath"], umask)
		if group:
			os.chown(fileInfo["outPath"], -1, group)

	if not directory:
		dynamicPages = getDynamicPages()
		for path, view in dynamicPages.items():
			info = view(templateManager)
			fileInfo = {
				'srcPath': info['srcPath'],
				'relPath': path,
				'outPath': joinPath(outputRoot, path)
			}
			template = info['template']
			variables = info['variables']

			content = renderTemplate(fileInfo, templateManager, allowAbort = allowAbort, pageProcessors = pageProcessors,
				template = template, variables = variables)
			if content:
				open(fileInfo["outPath"], 'w').write(content.encode('utf8'))
			if umask:
				os.chmod(fileInfo["outPath"], umask)
			if group:
				os.chown(fileInfo["outPath"], -1, group)

		for pageProcessor in pageProcessors:
			pageProcessor.processEnd()
