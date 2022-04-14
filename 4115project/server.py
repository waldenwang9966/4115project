#!/usr/bin/env python2.7

"""
Columbia W4111 Intro to databases
Example webserver

To run locally

    python server.py

Go to http://localhost:8111 in your browser


A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""

import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, session, url_for, escape,request, render_template, g, redirect, Response

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
app = Flask(__name__, template_folder=tmpl_dir)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# XXX: The Database URI should be in the format of:
#
#     postgresql://USER:PASSWORD@<IP_OF_POSTGRE_SQL_SERVER>/<DB_NAME>
#
# For example, if you had username ewu2493, password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://ewu2493:foobar@<IP_OF_POSTGRE_SQL_SERVER>/postgres"
#
# For your convenience, we already set it to the class database

# Use the DB credentials you received by e-mail
DB_USER = "dw2723"
DB_PASSWORD = "7492"

DB_SERVER = "w4111.cisxo09blonu.us-east-1.rds.amazonaws.com"

DATABASEURI = (
    "postgresql://" + DB_USER + ":" + DB_PASSWORD + "@" + DB_SERVER + "/proj1part2"
)


#
# This line creates a database engine that knows how to connect to the URI above
#
engine = create_engine(DATABASEURI)


@app.before_request
def before_request():
    """
    This function is run at the beginning of every web request
    (every time you enter an address in the web browser).
    We use it to setup a database connection that can be used throughout the request

    The variable g is globally accessible
    """
    try:
        g.conn = engine.connect()
    except:
        print("uh oh, problem connecting to database")
        import traceback

        traceback.print_exc()
        g.conn = None


@app.teardown_request
def teardown_request(exception):
    """
    At the end of the web request, this makes sure to close the database connection.
    If you don't the database could run out of memory!
    """
    try:
        g.conn.close()
    except Exception as e:
        pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to e.g., localhost:8111/foobar/ with POST or GET then you could use
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
#
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route("/")
def index():

    """
    request is a special object that Flask provides to access web request information:

    request.method:   "GET" or "POST"
    request.form:     if the browser submitted a form, this contains the data in the form
    request.args:     dictionary of URL arguments e.g., {a:1, b:2} for http://localhost?a=1&b=2

    See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
    """

    # DEBUG: this is debugging code to see what request looks like
    print(request.args)
    return render_template("index.html")


"""
    #
    # example of a database query
    #
    cursor = g.conn.execute("SELECT last_name FROM Applicant")
    names = []
    for result in cursor:
        names.append(result["last_name"])  # can also be accessed using result[0]
    cursor.close()

    #
    # Flask uses Jinja templates, which is an extension to HTML where you can
    # pass data to a template and dynamically generate HTML based on the data
    # (you can think of it as simple PHP)
    # documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
    #
    # You can see an example template in templates/index.html
    #
    # context are the variables that are passed to the template.
    # for example, "data" key in the context variable defined below will be
    # accessible as a variable in index.html:
    #
    #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
    #     <div>{{data}}</div>
    #
    #     # creates a <div> tag for each element in data
    #     # will print:
    #     #
    #     #   <div>grace hopper</div>
    #     #   <div>alan turing</div>
    #     #   <div>ada lovelace</div>
    #     #
    #     {% for n in data %}
    #     <div>{{n}}</div>
    #     {% endfor %}
    #
    context = dict(data=names)

    #
    # render_template looks in the templates/ folder for files.
    # for example, the below file reads template/index.html
    #
    return render_template("index.html", **context)

"""
#
# This is an example of a different path.  You can see it at
#
#     localhost:8111/another
#
# notice that the functio name is another() rather than index()
# the functions for each app.route needs to have different names
#
@app.route("/company_register")
def company():
    return render_template("company_register.html")

@app.route("/recommender_add", methods=["POST"])
def add():
    company_name = request.form["company_name"]
    companize_size = request.form["company_size"]
    cmd = "INSERT INTO Company(company_name,company_size) VALUES (:company_name), (:company_size)"
    g.conn.execute(
        text(cmd),
        company_name=company_name,
        company_size=company_size
    )
    
    return redirect("/")


@app.route("/applicant_register")
def applicant():
    return render_template("applicant_register.html")


@app.route("/recommender_register")

def recommender_register():
    return render_template("recommender_register.html")


@app.route("/recommender_search")
def recommender_search():
    if "rid" in session:
        cursor = g.conn.execute("SELECT * FROM Applicant")
        records = []
        for result in cursor:
            records.append(result)
        cursor.close()

        context = dict(data=records)

        return render_template("recommender_search.html", **context)
    else:
        return redirect("/recommender_register")
        

# Example of adding new data to the database
@app.route("/add", methods=["POST"])
def add():
    name = request.form["name"]
    print(name)
    cmd = "INSERT INTO test(name) VALUES (:name1), (:name2)"
    g.conn.n(text(cmd), name1=name, name2=name)
    return redirect("/")


@app.route("/recommender_add", methods=["POST"])
def recommender_add():
    last_name = request.form["last_name"]
    first_namet = request.form["first_name"]
    date_of_birth = request.form["date_of_birth"]

    cmd = "INSERT INTO Recommender(rid, last_name,first_namet,date_of_birth) SELECT Max(rid) + 1, :last_name, :first_namet, :date_of_birth FROM Recommender"
    g.conn.execute(
        text(cmd),
        last_name=last_name,
        first_namet=first_namet,
        date_of_birth=date_of_birth,
    )
    
    cursor = g.conn.execute("SELECT Max(rid) FROM Recommender")
    for r in cursor:
        rid = r[0]
    session["rid"] = rid
    return redirect("/recommender_search")
'''
cmd = 'INSERT INTO test(name) VALUES (:name1), (:name2)';
g.conn.execute(text(cmd), name1 = name, name2 = name);
'''
@app.route("/recommender_search_add", methods=["POST"])
def recommender_search_add():
    if "rid" in session:
        rid = session["rid"]
        aid = request.form["aid"]
        recommendatee_relationship = request.form["recommendatee_relationship"]
        posted_day = request.form["posted_day"]
        essay = request.form["essay"]

        cmd = "INSERT INTO Recommends(aid, rid, recommendatee_relationship,posted_day,essay) VALUES (:aid, :rid, :recommendatee_relationship, :posted_day, :essay)"
        g.conn.execute(text(cmd), rid = rid, aid = aid, recommendatee_relationship = recommendatee_relationship, posted_day = posted_day, essay = essay);
        return redirect("/recommender_logoff")
    else:
        return redirect("/")

@app.route("/recommender_logoff")
def logout():
    session.pop("rid", None)
    return redirect("/")


@app.route("/login")
def login():
    abort(401)
    this_is_never_executed()


if __name__ == "__main__":
    import click

    @click.command()
    @click.option("--debug", is_flag=True)
    @click.option("--threaded", is_flag=True)
    @click.argument("HOST", default="0.0.0.0")
    @click.argument("PORT", default=8111, type=int)
    def run(debug, threaded, host, port):
        """
        This function handles command line parameters.
        Run the server using

            python server.py

        Show the help text using

            python server.py --help

        """

        HOST, PORT = host, port
        print("running on %s:%d" % (HOST, PORT))
        app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

    run()
