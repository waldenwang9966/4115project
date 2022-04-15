import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, session, url_for, escape,request, render_template, g, redirect, Response

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
app = Flask(__name__, template_folder=tmpl_dir)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

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
    try:
        g.conn = engine.connect()
    except:
        print("uh oh, problem connecting to database")
        import traceback

        traceback.print_exc()
        g.conn = None


@app.teardown_request
def teardown_request(exception):
    try:
        g.conn.close()
    except Exception as e:
        pass

# Main Page
@app.route("/")
def index():
    # DEBUG: this is debugging code to see what request looks like
    print(request.args)
    return render_template("index.html")

@app.route("/company_register")
def company():
    return render_template("company_register.html")

@app.route("/company_add", methods=["POST"])
def company_add():
    company_name = request.form["company_name"]
    company_size = request.form["company_size"]
    
    cmd = "INSERT INTO Company(company_name,company_size) VALUES (:company_name, :company_size)"
    g.conn.execute(
        text(cmd),
        company_name=company_name,
        company_size=company_size
    )
    '''
    cursor = g.conn.execute(f"SELECT cid FROM Company WHERE company_name = {company_name}")
    for r in cursor:
        cid = r[0]
    print("right here...")
    print(cid)
    session["cid"] = cid
    '''
    return redirect("/company_search")

@app.route("/company_search")
def company_search():
    if "company" in session:
        cursor = g.conn.execute("SELECT aid, appid, date_of_birth, name as college, gpa, compensation_type, desired_rate, submission_date, essay, recommendatee_relationship FROM Applicant NATURAL JOIN Application_submits NATURAl JOIN recommends NATURAL JOIN Educational_Institution NATURAL JOIN studied_at;")
        applicants = []
        for result in cursor:
            applicants.append(result)
        cursor.close()
        context1 = dict(data1=applicants)
        
        cursor = g.conn.execute("SELECT * FROM Company")
        companies = []
        for result in cursor:
            companies.append(result)
        cursor.close()
        context2 = dict(data2=companies)
        
        return render_template("company_search.html", **context1, **context2)
    else:
        return render_template("company_not_login.html")
# TO DO
@app.route("/company_search_add", methods=["POST"])
def company_search_add():
    if "company" in session:
        
        cmd = "INSERT INTO Recommends(aid, rid, recommendatee_relationship,posted_day,essay) VALUES (:aid, :rid, :recommendatee_relationship, :posted_day, :essay)"
        g.conn.execute(text(cmd), rid = rid, aid = aid, recommendatee_relationship = recommendatee_relationship, posted_day = posted_day, essay = essay);
        return redirect("/company_search_add")
    else:
        return redirect("/")

@app.route("/company_logoff")
def company_logout():
    session.pop("company", None)
    return redirect("/company_register")


@app.route("/applicant_register")
def applicant():
    return render_template("applicant_register.html")


# Recommender related pages

@app.route("/recommender_register")
def recommender_register():
    return render_template("recommender_register.html")

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
        return render_template("recommender_not_login.html")

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
def recommender_logout():
    session.pop("rid", None)
    return redirect("/recommender_register")


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
