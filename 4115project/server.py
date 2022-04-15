from ast import Sub
import os
from django.shortcuts import render
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, url_for, escape,request, render_template, g, redirect, Response

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
    
    cmd2 = f"SELECT MAX(cid) FROM Company WHERE company_name = \'{company_name}\'"
    cursor = g.conn.execute(text(cmd2))
    for r in cursor:
        cid = r[0]
    
    return render_template("cid.html", value = cid)

@app.route("/company_industry")
def company_industry():
    cursor = g.conn.execute("SELECT distinct industry from Application_submits")
    
    industries = []
    for result in cursor:
        industries.append(result)
    cursor.close()
    
    cursor = g.conn.execute("SELECT distinct job_type from Application_submits")
    
    job_types = []
    for result in cursor:
        job_types.append(result)
    cursor.close()
    
    context1 = dict(data1=industries)
    context2 = dict(data2=job_types)
    
    return render_template("company_industry.html", **context1, **context2)
    

@app.route("/company_search")
def company_search():
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
    
# TO DO
@app.route("/company_decide", methods=["POST"])
def company_decide():
    cid = request.form["cid"]
    print(cid)
    industry = request.form["industry_ans"]
    print(industry)
    job_type = request.form["job_type_ans"]
    print(job_type)
    cursor = g.conn.execute(f"SELECT appid FROM Application_submits AppS WHERE industry = \'{industry}\' AND job_type = \'{job_type}\' EXCEPT SELECT appid FROM reviews WHERE cid = \'{cid}\'")
    appid_s = []
    for result in cursor:
        appid_s.append(result)
    cursor.close()
    if len(appid_s) == 0:
        return render_template("company_industry_empty.html")
    cur_appid = appid_s[0][0]
    
    
    cursor = g.conn.execute(f"WITH edu(appid, degree, college_name, graduation, gpa) AS (SELECT appid, degree_type, name, graduation, gpa FROM Applicant NATURAL JOIN Application_Submits NATURAL JOIN studied_at NATURAL JOIN Educational_Institution),rec (appid, relationship, rfirst, rlast, essay) AS (SELECT recommends.appid, recommends.recommendatee_relationship, Recommender.first_namet, Recommender.last_name, essay FROM recommends NATURAL JOIN Recommender),work (appid, position, tenure, job_description, company_name) AS (SELECT appid, position_title, tenure, job_description, company_name FROM worked_at NATURAL JOIN Company ORDER BY tenure DESC) SELECT * FROM Applicant NATURAL JOIN Application_submits NATURAL JOIN edu NATURAL JOIN rec NATURAL JOIN work WHERE appid = \'{cur_appid}\' LIMIT 1")
    
    for record in cursor:
        return_record = record
    
    return render_template("company_decide.html", value = return_record)

@app.route("/decision_update", methods=["POST"])
def decision_update():
    cid = request.form['cid']
    print(cid)
    appid = request.form["appid"]
    print(appid)
    aid = request.form["aid"]
    print(aid)
    decision = request.form["decision"]
    if decision == "yes":
        interested = True
    else:
        interested = False
    print(interested)
    
    cmd = f"INSERT INTO reviews VALUES ({cid},{aid}, {appid}, {interested})"
    g.conn.execute(text(cmd))
    
    return render_template("company_industry.html")

@app.route("/applicant_register")
def applicant():
    return render_template("applicant_register.html")

@app.route("/applicant_add", methods=["POST"])
def applicant_add():
    last_name = request.form["last_name"]
    first_name = request.form["first_name"]
    email = request.form["email"]
    phone_number = request.form["phonenumber"]
    date_of_birth = request.form["dateofbirth"]

    cmd = f"INSERT INTO Applicant(last_name,first_name,email, phone_number, date_of_birth) VALUES (\'{last_name}\',\'{first_name}\', \'{email}\', \'{phone_number}\', \'{date_of_birth}\')"
    
    
    g.conn.execute(
        text(cmd),
        last_name=last_name,
        first_name=first_name,
        email = email,
        phone_number = phone_number,
        date_of_birth=date_of_birth
    )
    
    cmd2 = f"SELECT MAX(aid) FROM Applicant WHERE email = \'{email}\'"
    cursor = g.conn.execute(text(cmd2))
    for r in cursor:
        aid = r[0]
    
    return render_template("aid.html", value = aid)

@app.route("/applicant_submit", methods=["POST"])
def applicant_submit():
    aid = request.form["aid"]
    industry = request.form["industry"]
    job_type = request.form["job_type"]
    compensation_type = request.form["compensation_type"]
    desired_rate = request.form["desired_rate"]
    Submission_date = request.form["Submission_date"]
    
    cmd = f"INSERT INTO Application_submits(aid,industry,job_type, compensation_type, desired_rate, Submission_date) VALUES (\'{aid}\',\'{industry}\', \'{job_type}\',, \'{compensation_type}\', \'{desired_rate}\', \'{Submission_date}\')"
    
    g.conn.execute(
        text(cmd),
        aid=aid,
        industry=industry,
        job_type = job_type,
        compensation_type=compensation_type,
        desired_rate=desired_rate,
        Submission_date = Submission_date
    )

    return render_template("applicant_submit.html")
    
    
    

@app.route("/education_add", methods=["POST"])
def education_add():
    name = request.form["name"]
    city = request.form["city"]
    state = request.form["state"]

    cmd = f"INSERT INTO Educational_Institution(name,city,state) VALUES (\'{name}\',\'{city}\', \'{state}\')"
    
    
    g.conn.execute(
        text(cmd),
        name=name,
        city=city,
        state = state
    )

    return render_template("applicant_submit.html")

# Recommender related pages

@app.route("/recommender_register")
def recommender_register():
    return render_template("recommender_register.html")

@app.route("/recommender_add", methods=["POST"])
def recommender_add():
    last_name = request.form["last_name"]
    first_namet = request.form["first_name"]
    date_of_birth = request.form["date_of_birth"]

    cmd = "INSERT INTO Recommender(rid, last_name,first_namet,date_of_birth) SELECT COALESCE(MAX(rid) + 1,0), :last_name, :first_namet, :date_of_birth FROM Recommender"
    
    g.conn.execute(
        text(cmd),
        last_name=last_name,
        first_namet=first_namet,
        date_of_birth=date_of_birth,
    )
    
    cursor = g.conn.execute("SELECT Max(rid) FROM Recommender")
    for r in cursor:
        rid = r[0]
    
    return render_template("rid.html", value = rid)

@app.route("/applicant_submit")
def applicant_submit():
    cursor = g.conn.execute("SELECT distinct industry from Application_submits")
    
    industries = []
    for result in cursor:
        industries.append(result)
    cursor.close()
    
    cursor = g.conn.execute("SELECT distinct job_type from Application_submits")
    
    job_types = []
    for result in cursor:
        job_types.append(result)
    cursor.close()
    
    context1 = dict(data1=industries)
    context2 = dict(data2=job_types)
    
    return render_template("company_industry.html", **context1, **context2)
    

@app.route("/recommender_search")
def recommender_search():
    cursor = g.conn.execute("SELECT App.aid, appid, first_name, last_name, industry,job_type, email, phone_number FROM Applicant App INNER JOIN Application_submits AppS ON App.aid = AppS.aid")
    records = []
    for result in cursor:
        records.append(result)
    cursor.close()
    context = dict(data=records)
    return render_template("recommender_search.html", **context)

@app.route("/recommender_search_add", methods=["POST"])
def recommender_search_add():
    rid = request.form["rid"]
    aid = request.form["aid"]
    appid = request.form["appid"]
    recommendatee_relationship = request.form["recommendatee_relationship"]
    posted_day = request.form["posted_day"]
    essay = request.form["essay"]
    cmd = "INSERT INTO Recommends(aid, appid, rid, essay, posted_day,recommendatee_relationship) VALUES (:aid, :appid, :rid, :essay, :posted_day,:recommendatee_relationship)"
    g.conn.execute(text(cmd), rid = rid, aid = aid,appid = appid,  recommendatee_relationship = recommendatee_relationship, posted_day = posted_day, essay = essay);
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
