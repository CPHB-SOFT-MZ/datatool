# -*- coding: utf-8 -*-
import os
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from multiprocessing import Pool, Process, Manager
from threading import Thread

import time
from bokeh.embed import components
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from queue import Queue

from django.utils.safestring import mark_safe

from datatool.datatool.functionlist import functions
from datatool.datatool.models import Document
from datatool.datatool.forms import DocumentForm
from datatool.datatool.analyzetools.tools import *
import pandas as pd


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
        try:
            if os.path.isfile(doc.docfile.path):
                os.remove(doc.docfile.path)
                # elif os.path.isdir(file_path): shutil.rmtree(file_path)
                doc.delete()
        except Exception as e:
            print(e)

        return HttpResponseRedirect(reverse('list'))


def analyze(request):
    if request.method == 'GET':

        # Get the document name from the session
        docname = request.session['document']

        # Prepare a variable to hold a list of our column headers
        headers = None
        g = {}
        # If the document is a csv file, set the CSV for our tool and load the column headers into the headers variable
        if docname.endswith('.csv'):
            csv = pd.read_csv('media/documents/' + docname)
            headers = csv.axes[1]
            g.update({'numbers': csv.select_dtypes(['int64', 'float64']).axes[1]})
            g.update({'object': csv.select_dtypes(['object']).axes[1]})
            print(headers)
            print(g)

        return render(
            request,
            'analyze.html',
            {
                'functions': functions,
                'headers': headers,
                'groups': g
            }
        )


# This method is called when the form is submitted and will take care of analyzing the data
def analyze_data(request):
    if request.method == 'POST':
        chart_threads = []
        res_threads = []
        plb_threads = []
        results = {}
        err_messages = {}
        docname = request.session['document']
        csv = pd.DataFrame()
        th_ex = ProcessPoolExecutor(max_workers=4)
        # Prepare a variable to hold a list of our column headers
        # If the document is a csv file, set the CSV for our tool and load the column headers into the headers variable
        if docname.endswith('.csv'):
            csv = pd.read_csv('media/documents/' + docname)

        def put_plb(result):
            print(result)
            #if results.get(result[0]) is None:
            #    results.update({result[0] : []})
            #results.get(result[0]).append({'html': mark_safe(result[1])})

        def put_result(result):
            results.update({result[0]: result[1]})

        def put_chart(result):
            if results.get(result[0]) is None:
                results.update({result[0] : []})
            results.get(result[0]).append({'script': result[1]['script'], 'div': result[1]['div']})

        # For every function we have checked in our form
        for func in request.POST.getlist('functions'):

            # TODO: Implement the rest of the ifs
            if func == "AMAX":
                future = th_ex.submit(maximum_value, csv,
                                        request.POST.getlist('AMAX_headers'),
                                        request.POST.getlist('AMAX_info_headers'))

                res_threads.append(future)

            elif func == "BAR":
                # Get the Chart object from our tool and convert it to the required components to show in the template
                bar_headers = request.POST.getlist('BAR_headers')
                for bar_header in bar_headers:
                    future = th_ex.submit(bar_chart, csv, bar_header)
                    chart_threads.append(future)

            elif func == "BAR_SUM":
                group_header = request.POST['BAR_SUM_group_by']
                value_header = request.POST['BAR_SUM_header']
                future = th_ex.submit(bar_chart_sum, csv, value_header, group_header)
                chart_threads.append(future)

            elif func == "HIST":
                future = th_ex.submit(histogram, csv, request.POST['HIST_label'], request.POST['HIST_value'])
                chart_threads.append(future)

            # Of some odd reason multithreading doesn't work with Bokeh's donut call. Might refactor this to matplotlib
            elif func == "DONUT":
                donut_headers = request.POST.getlist('DONUT_headers')
                for donut_header in donut_headers:
                    future = th_ex.submit(donut_chart, csv, donut_header)
                    time.sleep(5)
                    plb_threads.append(future)


            elif func == "AMIN":
                future = th_ex.submit(minimum_value, csv,
                                      request.POST.getlist('AMIN_headers'),
                                      request.POST.getlist('AMIN_info_headers'))
                res_threads.append(future)

            elif func == "MED_FOR":
                future = th_ex.submit(median_value_for, csv,
                                          request.POST.getlist('MED_FOR_headers'),
                                          request.POST['MED_FOR_group_by'])
                res_threads.append(future)

            elif func == "AVG":
                future = th_ex.submit(average_value, csv, request.POST.getlist('AVG_headers'))
                res_threads.append(future)

            elif func == "AVG_FOR":
                future = th_ex.submit(average_value_for, csv,
                                      request.POST.getlist('AVG_FOR_headers'),
                                      request.POST['AVG_FOR_group_by'])
                res_threads.append(future)

            elif func == "SUM":
                future = th_ex.submit(sums, csv, request.POST.getlist('SUM_headers'))
                res_threads.append(future)

            elif func == "OCCUR":
                future = th_ex.submit(occurrences, csv, request.POST.getlist('OCCUR_headers'))
                res_threads.append(future)

            elif func == "SCATTER":
                scatter_x = request.POST['SCATTER_x']
                scatter_y = request.POST['SCATTER_y']
                future = th_ex.submit(scatter_chart, csv, scatter_x, scatter_y)
                chart_threads.append(future)

            elif func == "SCATTER_GROUP":
                scatter_x = request.POST['SCATTER_GROUP_x']
                scatter_y = request.POST['SCATTER_GROUP_y']
                grouped_by = request.POST['SCATTER_GROUP_by']
                future = th_ex.submit(scatter_chart_grouped, csv, scatter_x, scatter_y, grouped_by)
                chart_threads.append(future)

            elif func == "LINE":
                line_x = request.POST['LINE_x']
                line_y = request.POST['LINE_y']
                future = th_ex.submit(line_graph, csv, line_x, line_y)
                chart_threads.append(future)

            elif func == "LINE_MULTI":
                line_x = request.POST['LINE_MULTI_x']
                line_y = request.POST['LINE_MULTI_y']
                grouped_by = request.POST['LINE_MULTI_group']
                future = th_ex.submit(multiple_lines, csv, line_x, line_y, grouped_by)
                chart_threads.append(future)

        # Wait for all processes to finish
        th_ex.shutdown(wait=True)

        # Map the results form the futures to the total result object parsed to the html page
        for th in chart_threads:
            put_chart(th.result())

        for th in res_threads:
            put_result(th.result())

        for th in plb_threads:
            print(th.result())

        return render(
            request,
            'data.html',
            {
                'results': results,
                'errors': err_messages
            }
        )
