# -*- coding: utf-8 -*-
import os

from bokeh.embed import components
from bokeh.resources import CDN
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

# This is actually our index
# TODO: Rename to index so we can make it look nicer. Or at least redirect to this view on the index
def list(request):

    # Handle file upload (if form is submitted)
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            newdoc = Document(docfile=request.FILES['docfile'], file_name=request.FILES['docfile'])

            # This both saves in our database and our directory
            # TODO: Check that the comment above is actually valid
            newdoc.save()

            # Add the documents filename to the session (This is the one we're working at)
            request.session['document'] = request.FILES['docfile'].name

            # Redirect to the document list after POST
            return HttpResponseRedirect(reverse('analyze'))
    else:
        form = DocumentForm()  # A empty, unbound form

    # Load documents for the list page
    documents = Document.objects.all()

    # Render list page with the documents and the form
    return render(
        request,
        'list.html',
        {'documents': documents, 'form': form}
    )

# Deletes a file when the delete link is clicked on the index page
# TODO: Make it work so it also removes the file in the dir
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

        # Get the document name from the session
        docname = request.session['document']

        # Prepare a variable to hold a list of our column headers
        headers = None

        # If the document is a csv file, set the CSV for our tool and load the column headers into the headers variable
        if docname.endswith('.csv'):
            csv = pd.read_csv('media/documents/' + docname)
            tool.set_csv(csv)
            headers = csv.axes[1]

        # TODO: Give a list of functions instead of just AMAX
        functions = {
            'amax': 'AMAX',
            'bar': 'BAR'
        }
        return render(
            request,
            'analyze.html',
            {
                'functions': functions,
                'headers': headers
            }
        )

# This method is called when the form is submitted and will take care of analyzing the data
def analyze_data(request):
    if request.method == 'POST':
        results = {}
        # For every function we have checked in our form
        for function in request.POST.getlist('functions'):

            # TODO: Implement the rest of the ifs
            # TODO: Add all results, or a representation of the results to a list collecting everything for our template
            if function == "AMAX":
                amax = tool.maximum_value(request.POST.getlist('AMAX_headers'), request.POST.getlist('AMAX_info_headers'))
                results.update({"amax": amax})
            elif function == "BAR":
                # Get the Chart object from our tool and convert it to the required components to show in the template
                p = tool.bar_chart(request.POST['BAR_header'])
                script, div = components(p)
                results.update({'bar': {
                    'script': script,
                    'div': div
                }})

        # TODO: Render the data.html template with every calculated data as well as graphs. Maybe in a list of objects?
        return render(
            request,
            'data.html',
            {
                'results' : results,
                'selected': request.POST.getlist('AMAX_headers')
            }
        )

