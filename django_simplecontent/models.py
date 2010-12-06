from django.utils.translation import ugettext_lazy as _, ugettext
from django.db import models
from django_simplecontent.global_permissions import register_custom_permissions_simple

class Block(models.Model):
	class Meta:
		verbose_name = _('block')
		verbose_name_plural = _('blocks')

	name = models.CharField(_('name'), max_length = 300)
	verbose_name = models.CharField(_('verbose name'), max_length = 300)
	html = models.BooleanField(_('html'))
	width = models.CharField(_('width'), null = True, blank = True, max_length = 10)
	height = models.CharField(_('height'), null = True, blank = True, max_length = 10)

	def __unicode__(self):
		return self.verbose_name or self.name

class Template(models.Model):
	class Meta:
		verbose_name = _('template')
		verbose_name_plural = _('templates')

	path = models.CharField(_('name'), max_length = 300)
	blocks = models.ManyToManyField(Block, verbose_name = _('blocks'), through = 'BlockConnection')

	def __unicode__(self):
		return self.path

class BlockConnection(models.Model):
	class Meta:
		verbose_name = _('block connection')
		verbose_name_plural = _('block connections')

	block = models.ForeignKey(Block, verbose_name = _('block'))
	template = models.ForeignKey(Template, verbose_name = _('template'))
	required = models.BooleanField(_('required'), default = True)

	def __unicode__(self):
		return ugettext("Connection from template '{template}' to {block}").format(template = self.template.path, block = self.block.name)

#register_custom_permissions_simple((
	#("can_add_content", _("Can add content")),
	#("can_edit_content", _("Can edit content")),
	#("can_delete_content", _("Can delete content")),
	#("can_generate_content", _("Can create backup")),
	#("can_create_backup", _("Can create backup")),
	#("can_restore_backup", _("Can restore backup")),
#))
