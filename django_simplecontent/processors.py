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
	def __init__(self, outFile, excludeFile = None, url = "/"):
		self.outDir = None
		self.outFile = outFile
		self.umask = None
		self.group = None
		self.excludes = [i for i in open(excludeFile, "r").read().split("\n") if i] \
			if excludeFile else []
		self.url = url
		self.sitemap = ElementTree.TreeBuilder()
		self.sitemap.start("urlset", {"xmlns": "http://www.google.com/schemas/sitemap/0.84"})

	def processFile(self, fileInfo):
		if not self.outDir:
			self.outDir = fileInfo["outPath"][: -len(fileInfo["relPath"])]
		if not self.umask:
			self.umask = fileInfo.get("outUmask")
		if not self.group:
			self.group = fileInfo.get("outGroup")

		if fileInfo["relPath"] not in self.excludes:
			self.sitemap.start("url", {})
			self.sitemap.start("loc", {})
			self.sitemap.data(self.url + "/" + fileInfo["relPath"])
			self.sitemap.end("loc")
			self.sitemap.start("lastmod", {})
			self.sitemap.data(fileInfo["srcModified"].strftime("%Y-%m-%d"))
			self.sitemap.end("lastmod")
			self.sitemap.end("url")

	def processEnd(self):
		self.sitemap.end("urlset")

		outPath = os.path.join(self.outDir, self.outFile)
		xml = ElementTree.ElementTree(self.sitemap.close())
		xml.write(outPath, encoding = "utf8")

		if self.umask:
			os.chmod(outPath, self.umask)
		if self.group:
			os.chown(outPath, -1, self.group)

class HtmlSitemapProcessor(PageProcessor):
	def __init__(self, template, outFile, titleBlock = "title", excludeFile = None):
		self.template = template
		self.templateManager = None
		self.outDir = None
		self.outFile = outFile
		self.umask = None
		self.group = None
		self.titleBlock = titleBlock
		self.files = []
		self.excludes = [i for i in open(excludeFile, "r").read().split("\n") if i] \
			if excludeFile else []

	def processFile(self, fileInfo):
		if not self.outDir:
			self.outDir = fileInfo["outPath"][: -len(fileInfo["relPath"])]
		if not self.umask:
			self.umask = fileInfo.get("outUmask")
		if not self.group:
			self.group = fileInfo.get("outGroup")

	def processTemplate(self, fileInfo, variables, template):
		self.templateManager = template.manager
		if fileInfo["relPath"] not in self.excludes:
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

		outPath = os.path.join(self.outDir, self.outFile)
		open(outPath, 'w').write(content.encode('utf8'))
		if self.umask:
			os.chmod(outPath, self.umask)
		if self.group:
			os.chown(outPath, -1, self.group)

class OnlyModifiedProcessor(PageProcessor):
	def processFile(self, fileInfo):
		if fileInfo["outModified"] == None:
			#print ("New file %s " % fileInfo["relPath"])
			return True
		elif fileInfo["srcModified"] > fileInfo["outModified"]:
			#print ("File changed %s " % fileInfo["relPath"])
			return True
		else:
			#print ("File unchanged %s " % fileInfo["relPath"])
			return False
