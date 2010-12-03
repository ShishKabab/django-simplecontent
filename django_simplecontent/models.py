from django.db import models

class Block(models.Model):
	name = models.CharField(max_length = 300)
	verbose_name = models.CharField(max_length = 300)
	html = models.BooleanField()
	width = models.CharField(null = True, blank = True, max_length = 10)
	height = models.CharField(null = True, blank = True, max_length = 10)

	def __unicode__(self):
		return self.verbose_name or self.name

class Template(models.Model):
	path = models.CharField(max_length = 300)
	blocks = models.ManyToManyField(Block, through = 'BlockConnection')

	def __unicode__(self):
		return self.path

class BlockConnection(models.Model):
	block = models.ForeignKey(Block)
	template = models.ForeignKey(Template)
	required = models.BooleanField(default = True)

	def __unicode__(self):
		return "Connection from template '%s' to block '%s'" % (self.template.path, self.block.name)
