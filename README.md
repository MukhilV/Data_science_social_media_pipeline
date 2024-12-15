[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/8IqmWj30)


## Project explanantion:
- The Dashboard to visualize the data collected from 4chan and reddit is built under the folder project1_impl/reddit_4chan_dashboard.
- We had built 3 different dashboards.
    - 4chan dashboard 
    - reddit dashboard 
    - Dashboard for platform comparision 
- This is a python web application built with Flask framework and other libraries to support plots in the dashboard

## Structure of the Directory:
- `/app` contains all the files related to building the dashboard 
    - `/app/routes` - contains URLs and its Handler
    - `/app/static` -  contains necessary JS and CSS files to support the application 
    - `/app/templates` - contains all the HTML files that will be rendered for each route in /app/routes 
    - `__init__.py` - Registers all the routes
    - `queries.py` - contains all the queries that is required to fetch data from the database
    - `utils.py` - contains helper functions
- README.md - This is the file
- requirements.txt - contains all the dependency libararies for this project 

## If you are a TA and have previlege to access our remote machine, then
- Go into the folder project1_impl/reddit_4chan_dashboard.
- Activate the virtual env `source env/dev/bin/activate`
- Run `python3 app.py`
- You can access the application at http://127.0.0.1:5000/

## If you cannot access our remote machine, then follow the below steps:
Steps to run the project:
- Go into the folder project1_impl/reddit_4chan_dashboard.
- You probably want to use virtual environments to keep evertying clean.

  `python -m venv ./env/dev`

  Activate your new environment: `source env/dev/bin/activate`

  Deactivate your environment: `deactivate`
- Install all the dependecies with the command: `pip install -r requirements.txt`
- You might want to set up your own environmental variables, as those are not pushed to git hub.
- Now, Run `python3 app.py`
- You can access the application at http://127.0.0.1:5000/
