# -*- coding: utf-8 -*-
import os

from django.shortcuts import render
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, render_to_response
from datatool.myapp.models import Document
from datatool.myapp.forms import DocumentForm
from datatool.myapp.analyzetools.tools import Tools
import pandas as pd

tool = Tools()
def list(request):
    # Handle file upload
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            newdoc = Document(docfile=request.FILES['docfile'], file_name=request.FILES['docfile'])
            newdoc.save()

            request.session['document'] = request.FILES['docfile'].name
            # Redirect to the document list after POST
            return HttpResponseRedirect(reverse('analyze'))
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

def analyze(request):
    if request.method == 'GET':
        docname = request.session['document']
        headers = docname
        if docname.endswith('.csv'):
            csv = pd.read_csv('media/documents/' + docname)
            tool.set_csv(csv)
            headers = csv.axes[1]
            request.session['headers'] = []
            saved_list = request.session['headers']
            for header in headers:
                saved_list.append(header)
            request.session['headers'] = saved_list
            print(request.session['headers'])
        return render(
            request,
            'analyze.html',
            {
                'headers': headers
            }
        )
    if request.method == 'POST':
        docname = request.session['document']
        csv = pd.read_csv('media/documents/' + docname)

        for header in request.POST.getlist('headers'):
            print(tool.maximum_value(header))
        return render(
            request,
            'analyze.html',
            {
                'selected': request.POST.getlist('headers')
            }
        )

