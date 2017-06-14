import os
from concurrent.futures import ProcessPoolExecutor
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from datatool.datatool.functionlist import functions
from datatool.datatool.models import Document
from datatool.datatool.forms import DocumentForm
from datatool.datatool.analyzetools.tools import *
import pandas as pd


def index(request):
    # Handle file upload (if form is submitted)
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            newdoc = Document(docfile=request.FILES['docfile'], file_name=request.FILES['docfile'])

            # This both saves in our database and our directory
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
        'index.html',
        {'documents': documents, 'form': form}
    )


# Deletes a file when the delete link is clicked on the index page
def remove(request, file_name):
    if request.method == 'GET':
        doc = Document.objects.get(file_name=file_name)
        with os.path.isfile(doc.docfile.path):
            os.remove(doc.docfile.path)
            doc.delete()

        return HttpResponseRedirect(reverse('index'))

# Shows our form for our analysis
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

        # Holds all results and are parsed to the data template
        results = {}
        # TODO: Was supposed to handle exceptions
        err_messages = {}
        docname = request.session['document']
        csv = pd.DataFrame()
        # Prepare a process pool with 4 workers to process all our data
        # This does not activate the GIL as threads does.
        th_ex = ProcessPoolExecutor(max_workers=4)

        # If the document is a csv file, set the CSV.
        if docname.endswith('.csv'):
            csv = pd.read_csv('media/documents/' + docname)

        # Puts our non-chart results in our results dictionary
        def put_result(result):
            results.update({result[0]: result[1]})

        # Unwraps and puts our charts in our results disctionary
        def put_chart(result):
            if results.get(result[0]) is None:
                results.update({result[0] : []})
            results.get(result[0]).append({'script': result[1]['script'], 'div': result[1]['div']})

        # For every function we have checked in our form
        for func in request.POST.getlist('functions'):

            # Gives the maximum value for all the headers and returns the requested info headers for that row
            if func == "AMAX":
                future = th_ex.submit(maximum_value, csv,
                                        request.POST.getlist(func + '_headers'),
                                        request.POST.getlist(func + '_info_headers'))

                res_threads.append(future)

            # Generates a bar chart of occurences
            elif func == "BAR":
                # Get the Chart object from our tool and convert it to the required components to show in the template
                bar_headers = request.POST.getlist(func + '_headers')
                for bar_header in bar_headers:
                    future = th_ex.submit(bar_chart, csv, bar_header)
                    chart_threads.append(future)

            # Generates a bar chart of sums (of the header) and groups them by another header
            elif func == "BAR_SUM":
                group_header = request.POST[func + '_group_by']
                value_header = request.POST[func + '_header']
                future = th_ex.submit(bar_chart_sum, csv, value_header, group_header)
                chart_threads.append(future)

            # Generates a histogram
            elif func == "HIST":
                future = th_ex.submit(histogram, csv, request.POST[func + '_label'], request.POST[func + '_value'])
                chart_threads.append(future)

            # Generates a pie chart
            elif func == "PIE":
                pie_headers = request.POST.getlist(func + '_headers')
                for pie_header in pie_headers:
                    # The following doesn't work, since matplotlib is not thread safe. Using bokeh instead
                    # future = th_ex.submit(pie_chart, csv, pie_header)
                    # plb_threads.append(future)

                    # Bokeh implementation for speed optimization
                    future = th_ex.submit(pie_chart_alternative, csv, pie_header)
                    chart_threads.append(future)

            # Gives the minimum value for all the headers and returns the requested info headers for that row
            elif func == "AMIN":
                future = th_ex.submit(minimum_value, csv,
                                      request.POST.getlist(func + '_headers'),
                                      request.POST.getlist(func + '_info_headers'))
                res_threads.append(future)

            # Finds median for a given header and groups it by something else
            elif func == "MED_FOR":
                future = th_ex.submit(median_value_for, csv,
                                          request.POST.getlist(func + '_headers'),
                                          request.POST[func + '_group_by'])
                res_threads.append(future)

            # Finds average for a single/whole column
            elif func == "AVG":
                future = th_ex.submit(average_value, csv, request.POST.getlist(func + '_headers'))
                res_threads.append(future)

            # Finds average for a column grouped by another column's unique values
            elif func == "AVG_FOR":
                future = th_ex.submit(average_value_for, csv,
                                      request.POST.getlist(func + '_headers'),
                                      request.POST[func + '_group_by'])
                res_threads.append(future)

            # Sum of all values in a column
            elif func == "SUM":
                future = th_ex.submit(sums, csv, request.POST.getlist(func + '_headers'))
                res_threads.append(future)

            # Occurences for a specified header (unique counts)
            elif func == "OCCUR":
                future = th_ex.submit(occurrences, csv, request.POST.getlist(func + '_headers'))
                res_threads.append(future)

            # Generates a scatter chart (all mixed up)
            elif func == "SCATTER":
                scatter_x = request.POST[func + '_x']
                scatter_y = request.POST[func + '_y']
                future = th_ex.submit(scatter_chart, csv, scatter_x, scatter_y)
                chart_threads.append(future)

            # Generates a more useful scatter chart where points get grouped by something
            elif func == "SCATTER_GROUP":
                scatter_x = request.POST[func + '_x']
                scatter_y = request.POST[func + '_y']
                grouped_by = request.POST[func + '_by']
                future = th_ex.submit(scatter_chart_grouped, csv, scatter_x, scatter_y, grouped_by)
                chart_threads.append(future)

            # Generate a line chart with a single line
            elif func == "LINE":
                line_x = request.POST[func + '_x']
                line_y = request.POST[func + '_y']
                future = th_ex.submit(line_graph, csv, line_x, line_y)
                chart_threads.append(future)

            # Generate a line chart with multiple lines.
            elif func == "LINE_MULTI":
                line_x = request.POST[func + '_x']
                line_y = request.POST[func + '_y']
                grouped_by = request.POST[func + '_group']
                future = th_ex.submit(multiple_lines, csv, line_x, line_y, grouped_by)
                chart_threads.append(future)

        # Wait for all processes to finish
        th_ex.shutdown(wait=True)

        # Map the results form the futures to the total result object parsed to the html page
        for th in chart_threads:
            put_chart(th.result())

        for th in res_threads:
            put_result(th.result())

        return render(
            request,
            'data.html',
            {
                'results': results,
                # Exceptions will go here
                'errors': err_messages
            }
        )
