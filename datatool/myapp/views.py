# -*- coding: utf-8 -*-
import os

from django.shortcuts import render
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from datatool.myapp.models import Document
from datatool.myapp.forms import DocumentForm

def list(request):
    # Handle file upload
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            newdoc = Document(docfile=request.FILES['docfile'], file_name=request.FILES['docfile'])
            newdoc.save()

            request.session['document'] = request.FILES['docfile'].name
            # Redirect to the document list after POST
            return HttpResponseRedirect(reverse('list'))
    else:
        form = DocumentForm()  # A empty, unbound form

    # Load documents for the list page
    documents = Document.objects.all()
    # print(request.session['document'])
    # Render list page with the documents and the form
    return render(
        request,
        'list.html',
        {'documents': documents, 'form': form}
    )


def remove(request, file_name):
    if request.method == 'GET':
        doc = Document.objects.get(file_name=file_name)
        doc.delete()
        try:
            print(doc.docfile.url)
            # Of some reason doesn't remove the file from the directory
            if os.path.isfile(doc.docfile.url):
                os.remove(doc.docfile.url)
                # elif os.path.isdir(file_path): shutil.rmtree(file_path)
        except Exception as e:
            print(e)

        return HttpResponseRedirect(reverse('list'))

