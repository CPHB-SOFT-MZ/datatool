# datatool
## Prerequisites
- Python3
- Django
- Numpy
- Bokeh
- Pandas
- Matplotlib
- Mpld3


## How to make it run (Ubuntu guide)
- `apt-get update`
- `apt-get install python3`
- `apt-get install pip3`
- `pip3 install django, django-admin, numpy, pandas, matplotlib, bokeh`
- `pip3 install django-admin`
- `pip3 install numpy`
- `pip3 install pandas`
- `pip3 install matplotlib`
- `pip3 install bokeh`
- `pip3 install mpld3`
- Clone this repository
- cd into the cloned project
- Do a `python3 manage.py runserver`

## How to use the application
Go to the address of where you started the application. This is by default http://localhost:8000
You will see a simple upload form where you can upload your CSV file.
Make sure that your file has no invalid data, as this is currently not handled by the site. 
We have provided a csv file you can use for testing called FL_insurance_sample.csv, that you can use.
![alt text](https://www.dropbox.com/s/1kpaazk0s8nzeo9/Screen%20Shot%202017-05-24%20at%2011.16.10.png?dl=1)

When you've uploaded your CSV file, you will get redirected to the following page:
![alt text](https://www.dropbox.com/s/hncvoeor69ba1ns/Screen%20Shot%202017-05-24%20at%2011.30.54.png?dl=1)

Remember to check the headline boxes for what data you want to extract/generate or the function will get ignored (Just like on the above picture)
On some of the forms, you can choose multiple values. If there's only a single column to choose from, it will generate multiple charts with the selected data.

When you're done choosing what you want, submit the form, and have a bit of patience, and you will get redirected to the result page presenting your data in a nice formatted way.

![alt text](https://www.dropbox.com/s/wq1hlv4fdxb81an/Screen%20Shot%202017-05-24%20at%2012.25.14.png?dl=1)
![alt text](https://www.dropbox.com/s/zjgtggbm3v4yxgb/Screen%20Shot%202017-05-24%20at%2012.25.04.png?dl=1)
