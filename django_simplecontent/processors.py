import os
from xml.etree import ElementTree
from datetime import datetime

class PageProcessor:
	def processFile(self, fileInfo):
		pass

	def processVariables(self, fileInfo, variables):
		return variables

	def processTemplate(self, fileInfo, variables, template):
		pass

	def processEnd(self):
		pass

class LastModifiedProcessor(PageProcessor):
	def processFile(self, fileInfo):
		fileInfo["srcModified"] = datetime.fromtimestamp(os.path.getmtime(fileInfo["srcPath"]))
		try:
			fileInfo["outModified"] = datetime.fromtimestamp(os.path.getmtime(fileInfo["outPath"]))
		except:
			fileInfo["outModified"] = None

	def processVariables(self, fileInfo, variables):
		variables['lastModified'] = fileInfo["srcModified"]
		return variables

class CustomVariablesProcessor(PageProcessor):
	def __init__(self, **variables):
		self.variables = variables

	def processVariables(self, fileInfo, variables):
		variables.update(self.variables)
		return variables

class GoogleSitemapProcessor(PageProcessor):
	def __init__(self, outFile):
		self.outDir = None
		self.outFile = outFile
		self.sitemap = ElementTree.TreeBuilder()
		self.sitemap.start("urlset", {"xmlns": "http://www.google.com/schemas/sitemap/0.84"})

	def processFile(self, fileInfo):
		if not self.outDir:
			self.outDir = fileInfo["outPath"][: -len(fileInfo["relPath"])]

		self.sitemap.start("url", {})
		self.sitemap.start("loc", {})
		self.sitemap.data("/" + fileInfo["relPath"])
		self.sitemap.end("loc")
		self.sitemap.start("lastmod", {})
		self.sitemap.data(fileInfo["srcModified"].strftime("%Y-%m-%d"))
		self.sitemap.end("lastmod")
		self.sitemap.end("url")

	def processEnd(self):
		self.sitemap.end("urlset")

		xml = ElementTree.ElementTree(self.sitemap.close())
		xml.write(os.path.join(self.outDir, self.outFile), encoding = "utf8")

class HtmlSitemapProcessor(PageProcessor):
	def __init__(self, template, outFile, titleBlock = "title"):
		self.template = template
		self.templateManager = None
		self.outDir = None
		self.outFile = outFile
		self.titleBlock = titleBlock
		self.files = []

	def processFile(self, fileInfo):
		if not self.outDir:
			self.outDir = fileInfo["outPath"][: -len(fileInfo["relPath"])]

	def processTemplate(self, fileInfo, variables, template):
		self.templateManager = template.manager
		self.files.append({
			'path': fileInfo["relPath"],
			'title': template.getBlockContent(self.titleBlock, variables)
		})

	def processEnd(self):
		content = self.templateManager.getFromEnv(self.template)
		content = content.render({
			'fileInfo': {'relPath': 'sitemap.html'},
			'pages': sorted(self.files, key = lambda i: i["title"]),
			'lastModified': datetime.now()
		})
		open(os.path.join(self.outDir, self.outFile), 'w').write(content.encode('utf8'))

class OnlyModifiedProcessor(PageProcessor):
	def processFile(self, fileInfo):
		return fileInfo["srcModified"] > fileInfo["outModified"]
