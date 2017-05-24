# datatool
## Prerequisites
- Python3
- Django
- Numpy
- Bokeh
- Pandas
- Matplotlib


## How to make it run (Ubuntu guide)
- `apt-get update`
- `apt-get install python3`
- `apt-get install pip3`
- `apt-get install django-admin`
- `pip3 install numpy, pandas, matplotlib, bokeh`
- Clone this repository
- cd into the cloned project
- Do a ```python3 manage.py runserver```

## How to use the application
Go to the address of where you started the application. This is by default http://localhost:8000
You will see a simple upload form where you can upload your CSV file.
Make sure that your file has no invalid data, as this is currently not handled by the site. 
We have provided a csv file you can use for testing called FL_insurance_sample.csv, that you can use.
![alt text](https://www.dropbox.com/s/1kpaazk0s8nzeo9/Screen%20Shot%202017-05-24%20at%2011.16.10.png?dl=1)

When you've uploaded your CSV file, you will get redirected to the following page:
### PICTURE OF ANALYZE FORM GOES HERE

Remember to check the headline boxes for what data you want to extract/generate or the function will get ignored. 
When you're done choosing what you want, submit the form, and have a bit of patience, and you will get redirected to the result page presenting your data in a nice formatted way.

### PICTURE OF RESULTS PAGE GOES HERE

