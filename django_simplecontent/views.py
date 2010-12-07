import os
import tarfile
import time
from django.contrib.auth.decorators import permission_required, login_required
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import Http404, HttpResponseRedirect
from django.conf import settings
from django.forms.formsets import formset_factory
from django.core.urlresolvers import reverse
from django_simplecontent.common import getTemplateManager, buildHtml
from django_simplecontent.models import Template, BlockConnection
from django_simplecontent import forms

templateManager = getTemplateManager()

def get_files(dir):
	for root, dirs, files in os.walk(dir):
		for file in files:
			yield os.path.join(root, file)[len(dir) + 1:]


@login_required
def template_list(request):
	templates = []
	for i, templateDir in enumerate(settings.TEMPLATE_DIRS):
		for templateFile in get_files(templateDir):
			templates.append({
				'path': i,
				'name': templateFile
			})

	return render_to_response('simplecontent/template_list.html', {
		'templates': templates
	}, context_instance = RequestContext(request))

@permission_required('django_simplecontent.change_template')
def template_edit(request, path, template):
	template = template.rstrip("/")
	templatePath = os.path.join(settings.TEMPLATE_DIRS[int(path)], template)

	saved = False
	if request.method == "POST":
		form = forms.TemplateEditForm(request.POST)
		if form.is_valid():
			open(templatePath, 'w').write(form.cleaned_data['content'])
			saved = True

	form = forms.TemplateEditForm({
		'name': template,
		'content': open(templatePath, 'r').read().decode('utf8')
	})

	return render_to_response('simplecontent/template_edit.html', {
		'saved': saved,
		'path': path,
		'name': template,
		'form': form
	}, context_instance = RequestContext(request))

@login_required
def content_list(request):
	files = []
	for contentFile in get_files(settings.SIMPLECONTENT_ROOT):
		files.append({'name': contentFile, 'path': contentFile})

	return render_to_response('simplecontent/content_list.html', {
		'files': files
	}, context_instance = RequestContext(request))

@login_required
def content_edit(request):
	new = bool(request.REQUEST.get("new"))
	path = request.GET["path"]
	absPath = os.path.join(settings.SIMPLECONTENT_ROOT, path)
	template = templateManager.getFromFile(absPath) if not new else None
	parent = template.getParent() if template else request.REQUEST["parent"]

	connections = BlockConnection.objects.filter(template__path = parent) \
		.select_related("block") \
		.order_by("block__html", "-required")
	if not connections:
		raise Http404
	form = forms.ContentEditForm(connections, template, request.POST if request.POST else None)

	saved = False
	if request.method == "POST" and form.is_valid():
		content = '{%% extends "%s" %%}\n' % request.POST["parent"]
		for field in form.cleaned_data.items():
			if not field[1]:
				continue

			content += "{%% block %s %%}%s{%% endblock %%}\n" % field

		open(absPath, 'w').write(content.encode('utf8'))
		saved = True

	return render_to_response('simplecontent/content_edit.html', {
		'form': form,
		'name': path,
		'path': path,
		'parent': parent,
		'saved': saved,
		'new': int(new),
		'root_url': settings.SIMPLECONTENT_ROOT_URL or "/"
	}, context_instance = RequestContext(request))

@login_required
def content_add(request):
	return render_to_response('simplecontent/content_add.html', {
		'templates': Template.objects.all()
	}, context_instance = RequestContext(request))

@login_required
def content_delete(request):
	confirm = bool(request.GET.get("confirm"))
	relPath = request.GET.get("path")
	absPath = os.path.abspath(os.path.join(settings.SIMPLECONTENT_ROOT, relPath))
	if not absPath.startswith(settings.SIMPLECONTENT_ROOT):
		raise Http404

	if not confirm:
		return render_to_response('simplecontent/content_delete.html', {
			'path': relPath
		}, context_instance = RequestContext(request))

	outPath = os.path.abspath(os.path.join(settings.SIMPLECONTENT_OUTPUT_ROOT, relPath))
	for i in (absPath, outPath):
		try:	os.remove(i)
		except:	pass
	return HttpResponseRedirect(reverse('django_simplecontent.views.content_list'))

@login_required
def content_generate(request):
	buildHtml(allowAbort = not bool(request.GET.get("force")))

	return render_to_response('simplecontent/content_generate.html', {
		'success': True
	}, context_instance = RequestContext(request))

@login_required
def backup_create(request):
	try:	os.makedirs(settings.SIMPLECONTENT_BACKUP_DIR)
	except:	pass

	file = os.path.join(settings.SIMPLECONTENT_BACKUP_DIR, time.strftime("%d-%m-%Y-%H:%M.tgz"))
	file = tarfile.open(file, "w:gz")
	try:
		file.add(settings.SIMPLECONTENT_ROOT, os.path.basename(settings.SIMPLECONTENT_ROOT))
	finally:
		file.close()

	return render_to_response('simplecontent/backup_create.html', {
		'success': True
	}, context_instance = RequestContext(request))

@login_required
def backup_restore(request):
	file = request.GET.get("path")
	if not file:
		return render_to_response('simplecontent/backup_restore.html', {
			'files': os.listdir(settings.SIMPLECONTENT_BACKUP_DIR)
		}, context_instance = RequestContext(request))

	absPath = os.path.abspath(os.path.join(settings.SIMPLECONTENT_BACKUP_DIR, file))
	if not absPath.startswith(settings.SIMPLECONTENT_BACKUP_DIR):
		raise Http404

	file = tarfile.open(absPath)
	try:
		file.extractall(os.path.dirname(os.path.normpath(settings.SIMPLECONTENT_ROOT)))
	finally:
		file.close()

	return HttpResponseRedirect(reverse('django_simplecontent.views.content_list'))