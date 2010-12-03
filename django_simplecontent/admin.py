from django_simplecontent.models import Template, Block, BlockConnection
from django.contrib import admin

class ConnectionInline(admin.StackedInline):
	model = BlockConnection
	extra = 1

class TemplateAdmin(admin.ModelAdmin):
	inlines = [ConnectionInline]

admin.site.register(Template, TemplateAdmin)
admin.site.register(Block)
admin.site.register(BlockConnection)
