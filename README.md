# Mobile Cluster

## Installation

Clone the repository. 

Requirements:
 * MongoDB
 * Python (only tested with Python 2.7)

Python requirements:
 * flask
 * pymongo

Install MongoDB as described in the [documentation](https://www.mongodb.com/).

To setup Python create a virtual environment or a conda environment.
Then install the requirements:

    pip install flask pymongo


## How to run

Start MongoDB:

    bin/mongod --dbpath /path/to/my/data

Now start the server:

    python master.py

For the master page point your browser to: [http://localhost:5000/static/master.html](http://localhost:5000/static/master.html)

The first time the master starts up the database must be initialised with a new job. Choose the parameters on the master page (the defaults are fine) and press "Submit". This populates MongoDB with the jobs for this fractal image.

On the master view page press "Start" to start listening for registered clients in the task farm and distributing jobs to them.

Once the job descriptions have been created in MongoDB the view page is directly available from here: [http://localhost:5000/static/master_view.html](http://localhost:5000/static/master_view.html).

A new set of job descriptions can be created at any time - note that the database is wiped and the old job descriptions are no longer available. If there are still jobs in the database then the master can be safely stopped and restarted.

For the client page point your browser to: [http://localhost:5000/static/index.html](http://localhost:5000/static/index.html).

Enter a user name and submit it. By clicking "Start" the client collects a job description from the master, processes it and returns the results to the master. Each job has to be started by clicking "Start".


