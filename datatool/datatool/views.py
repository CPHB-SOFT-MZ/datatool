# -*- coding: utf-8 -*-
import os
from concurrent.futures import ThreadPoolExecutor
from threading import Thread

from bokeh.embed import components
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from queue import Queue

from django.utils.safestring import mark_safe

from datatool.datatool.functionlist import functions
from datatool.datatool.models import Document
from datatool.datatool.forms import DocumentForm
from datatool.datatool.analyzetools.tools import Tools
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
            tool.set_csv(csv)
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
        chart_queue = Queue()
        res_queue = Queue()
        plb_queue = Queue()
        results = {}
        err_messages = {}
        threads = []
        #thread_pool = ThreadPoolExecutor(4)

        def put_plb(result):
            if results.get(result[0]) is None:
                results.update({result[0] : []})
            results.get(result[0]).append({'html': mark_safe(result[1])})
        def put_result(result):
            results.update({result[0]: result[1]})

        def put_chart(result):
            script, div = components(result[1])
            if results.get(result[0]) is None:
                results.update({result[0] : []})
            results.get(result[0]).append({'script': script, 'div': div})

            print("Done with ", result[0])

        # For every function we have checked in our form
        for func in request.POST.getlist('functions'):

            # TODO: Implement the rest of the ifs
            if func == "AMAX":
                amax_thread = Thread(target=tool.maximum_value, args=(res_queue, request.POST.getlist('AMAX_headers'),
                                                                      request.POST.getlist('AMAX_info_headers')))

                threads.append(amax_thread)
                amax_thread.start()

            elif func == "BAR":
                # Get the Chart object from our tool and convert it to the required components to show in the template
                bar_headers = request.POST.getlist('BAR_headers')
                for bar_header in bar_headers:
                    bar_thread = Thread(target=tool.bar_chart, args=(chart_queue, bar_header))
                    threads.append(bar_thread)
                    bar_thread.start()

            elif func == "BAR_SUM":
                group_header = request.POST['BAR_SUM_group_by']
                value_header = request.POST['BAR_SUM_header']

                bar_sum_thread = Thread(target=tool.bar_chart_sum,
                                        args=(chart_queue, value_header, group_header))
                threads.append(bar_sum_thread)
                bar_sum_thread.start()

            elif func == "HIST":
                hist_thread = Thread(target=tool.histogram,
                                     args=(chart_queue, request.POST['HIST_label'], request.POST['HIST_value']))
                threads.append(hist_thread)
                hist_thread.start()

            # Of some odd reason multithreading doesn't work with Bokeh's donut call. Might refactor this to matplotlib
            elif func == "DONUT":
                donut_headers = request.POST.getlist('DONUT_headers')
                for donut_header in donut_headers:
                    #tool.donut_chart(plb_queue, donut_header)
                    donut_thread = Thread(target=tool.donut_chart, args=(plb_queue, donut_header))
                    threads.append(donut_thread)
                    donut_thread.start()

            elif func == "AMIN":
                amin_thread = Thread(target=tool.minimum_value, args=(res_queue, request.POST.getlist('AMIN_headers'),
                                                                      request.POST.getlist('AMIN_info_headers')))
                threads.append(amin_thread)
                amin_thread.start()
            elif func == "MED_FOR":
                print(request.POST.getlist('MED_FOR_headers'))
                print(request.POST['MED_FOR_group_by'])
                med_thread = Thread(target=tool.median_value_for,
                                    args=(res_queue, request.POST.getlist('MED_FOR_headers'),
                                          request.POST['MED_FOR_group_by']))
                threads.append(med_thread)
                med_thread.start()
            elif func == "AVG":
                avg_th = Thread(target=tool.average_value, args=(res_queue, request.POST.getlist('AVG_headers')))
                threads.append(avg_th)
                avg_th.start()
            elif func == "AVG_FOR":
                avg_thread = Thread(target=tool.average_value_for,
                                    args=(res_queue, request.POST.getlist('AVG_FOR_headers'),
                                          request.POST['AVG_FOR_group_by']))
                threads.append(avg_thread)
                avg_thread.start()
            elif func == "SUM":
                sum_thread = Thread(target=tool.sum, args=(res_queue, request.POST.getlist('SUM_headers')))
                threads.append(sum_thread)
                sum_thread.start()
            elif func == "OCCUR":
                occur_thread = Thread(target=tool.occurrences, args=(res_queue,
                                                                     request.POST.getlist('OCCUR_headers')))
                threads.append(occur_thread)
                occur_thread.start()

            elif func == "SCATTER":
                scatter_x = request.POST['SCATTER_x']
                scatter_y = request.POST['SCATTER_y']
                scatter_thread = Thread(target=tool.scatter_chart, args=(chart_queue, scatter_x, scatter_y))
                threads.append(scatter_thread)
                scatter_thread.start()

            elif func == "SCATTER_GROUP":
                scatter_x = request.POST['SCATTER_GROUP_x']
                scatter_y = request.POST['SCATTER_GROUP_y']
                grouped_by = request.POST['SCATTER_GROUP_by']
                scatter_thread = Thread(target=tool.scatter_chart_grouped,
                                        args=(chart_queue, scatter_x, scatter_y, grouped_by))
                threads.append(scatter_thread)
                scatter_thread.start()

            elif func == "LINE":
                line_x = request.POST['LINE_x']
                line_y = request.POST['LINE_y']
                line_thread = Thread(target=tool.line_graph,
                                     args=(chart_queue, line_x, line_y))
                threads.append(line_thread)
                line_thread.start()

            elif func == "LINE_MULTI":
                line_x = request.POST['LINE_MULTI_x']
                line_y = request.POST['LINE_MULTI_y']
                grouped_by = request.POST['LINE_MULTI_group']
                line_thread = Thread(target=tool.multiple_lines,
                                     args=(chart_queue, line_x, line_y, grouped_by))
                threads.append(line_thread)
                line_thread.start()

        for th in threads:
            th.join()
        while not chart_queue.empty():
            put_chart(chart_queue.get())
        while not res_queue.empty():
            put_result(res_queue.get())
        while not plb_queue.empty():
            put_plb(plb_queue.get())

        return render(
            request,
            'data.html',
            {
                'results': results,
                'errors': err_messages
            }
        )
