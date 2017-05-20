# -*- coding: utf-8 -*-
import os
from threading import Thread
from bokeh.embed import components
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from queue import Queue

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
            'bar': 'BAR',
            'hist': 'HIST'
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
        chart_queue = Queue()
        res_queue = Queue()
        results = {}
        err_messages = {}
        threads = []

        def put_result(result):
            results.update({result[0]: result[1]})

        def put_chart(result):
            script, div = components(result[1])

            results.update({result[0]: {
                'script': script,
                'div': div
            }})
            print("Done with ", result[0])
        # For every function we have checked in our form
        for func in request.POST.getlist('functions'):

            # TODO: Implement the rest of the ifs
            # TODO: Add all results, or a representation of the results to a list collecting everything for our template
            if func == "AMAX":
                amax_thread = Thread(target=tool.maximum_value, args=(res_queue, request.POST.getlist('AMAX_headers'),
                                               request.POST.getlist('AMAX_info_headers')))

                threads.append(amax_thread)
                amax_thread.start()

            elif func == "BAR":
                # Get the Chart object from our tool and convert it to the required components to show in the template
                bar_thread = Thread(target=tool.bar_chart, args=(chart_queue, request.POST['BAR_header']))
                threads.append(bar_thread)
                bar_thread.start()

            elif func == "HIST":
                hist_thread = Thread(target=tool.histogram, args=(chart_queue, request.POST['HIST_label'], request.POST['HIST_value']))
                threads.append(hist_thread)
                hist_thread.start()

        for th in threads:
            th.join()
        while not chart_queue.empty():
            put_chart(chart_queue.get())
        while not res_queue.empty():
            put_result(res_queue.get())

        return render(
            request,
            'data.html',
            {
                'results' : results,
                'errors': err_messages
            }
        )

