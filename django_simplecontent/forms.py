from django import forms
from tinymce.widgets import TinyMCE

class TemplateEditForm(forms.Form):
	name = forms.CharField()
	content = forms.CharField(widget = forms.Textarea())

class ContentEditForm(forms.Form):
	def __init__(self, connections, template, *args, **kwds):
		super(ContentEditForm, self).__init__(*args, **kwds)

		for connection in connections:
			block = connection.block
			params = {
				"label": block.verbose_name or block.name,
				"required": connection.required
			}
			if template and not self.is_bound:
				params["initial"] = template.getBlockContent(block.name, {})
			if block.html:
				params["widget"] = forms.Textarea()
				params["widget"].attrs["style"] = "width: 100%"

			self.fields[block.name] = forms.CharField(**params)

def ContentEditFormFactory(connections):
	class _ContentEditForm(ContentEditForm):
		def __init__(self, *args, **kwds):
			super(_ContentEditForm, self).__init__(connections, None, *args, **kwds)

	return _ContentEditForm
