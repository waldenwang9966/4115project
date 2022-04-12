jobs = [
    {"title": "Software Engineer", "date": "04-01-2022"},
    {"title": "TeleMarketer", "date": "04-03-2022"},
    {"title": "Financial Advisor", "date": "04-07-2022"},
    {"title": "Intern", "date": "04-03-2022"},
]


from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html", jobs=jobs)


if __name__ == "__main__":
    app.run(debug=True)
