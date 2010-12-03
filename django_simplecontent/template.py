class Template(object):
	def __init__(self, manager):
		self.manager = manager

class TemplateManager(object):
	def getFromString(self, string):
		raise NotImplemented

	def getFromEnv(self, path):
		raise NotImplemented

	def getFromFile(self, path):
		return self.getFromString(open(path, 'r').read().decode('utf8'))

class DjangoTemplate(Template):
	def __init__(self, manager, template):
		super(DjangoTemplate, self).__init__(manager)
		self.template = template

	def render(self, variables):
		from django.template import Context
		return self.template.render(Context(variables))

class DjangoTemplateManager(TemplateManager):
	def getFromString(self, string):
		from django.template import Template
		return DjangoTemplate(self, Template(string))

	def getFromEnv(self, path):
		from django.template import loader
		return DjangoTemplate(self, loader.get_template(path))

class Jinja2Template(Template):
	def __init__(self, manager, template, source):
		super(Jinja2Template, self).__init__(manager)
		self.template = template
		self.source = source

	def getBlocks(self, variables = None):
		import jinja2
		blocks = []

		env = self.manager.env
		loader = self.manager.env.loader

		#import ipdb; ipdb.set_trace()
		template = self.template
		source = self.source
		while source:
			if variables:
				context = template.new_context(variables)
			ast = env.parse(source)

			blocks.append([])
			for k, v in template.blocks.items():
				blocks[-1].append({
					'name': k,
					'content': jinja2.utils.concat(v(context)) if variables else None,
					'children': [node.name for node in
						self._findNode(ast, jinja2.nodes.Block, lambda i: i.name == k).find_all(jinja2.nodes.Block)
					]
				})

			extends = ast.find(jinja2.nodes.Extends)
			if not extends:
				break
			template = env.get_template(extends.template.value)
			source, _, _ = loader.get_source(env, extends.template.value)

		return blocks

	def getBlockNames(self):
		return self.template.blocks.keys()

	def getBlockContent(self, name, variables):
		from jinja2.utils import concat
		context = self.template.new_context(variables)
		try:
			return concat(self.template.blocks[name](context))
		except KeyError:
			return ""

	def getParent(self):
		import jinja2
		ast = self.manager.env.parse(self.source)
		extends = ast.find(jinja2.nodes.Extends)
		if not extends:
			return

		return extends.template.value

	def render(self, variables):
		return self.template.render(**variables)

	def _findNode(self, parent, tp, f):
		for node in parent.find_all(tp):
			if f(node):
				return node

class Jinja2TemplateManager(TemplateManager):
	def __init__(self, env = None):
		if not env:
			from jinja2 import Environment, FileSystemLoader
			try:
				from django.conf import settings
				from django.template.loaders.app_directories import app_template_dirs
				self.env = Environment(
					loader = FileSystemLoader(app_template_dirs + settings.TEMPLATE_DIRS)
				)
			except ImportError:
				self.env = Environment()
		else:
			self.env = env

	def getFromString(self, string):
		return Jinja2Template(self, self.env.from_string(string), string)

	def getFromEnv(self, path):
		return Jinja2Template(self, self.env.get_template(path), None)
