from flask import Flask, render_template, request, redirect
import requests
import json
import os, csv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

engine = create_engine(os.getenv("JAWSDB_URL")) # database engine object from SQLAlchemy that manages connections to the database
                                                # DATABASE_URL is an environment variable that indicates where the database lives
db = scoped_session(sessionmaker(bind=engine))    # create a 'scoped session' that ensures different users' interactions with the
                                                # database are kept separate


@app.route('/')
def index():
    return render_template("index.html")

@app.route('/postcode_search', methods=['POST'])
def postcode_search():

    postcode = request.form['postcode']

    # Query API

    r = requests.get(
      'https://api.postcodes.io/postcodes/'+postcode)

    if r:
        print("Success")
    else:
        print("Error: API unavailable")

    r = r.json()

    result = r['result']

    constituency = result.get("parliamentary_constituency")

    return redirect("/"+constituency)

@app.route('/<string:constituency>')
def results(constituency):

    # Get power index and constituency_code
    constituency_response = db.execute("SELECT voter_index, constituency_code FROM power_index WHERE constituency = :constituency AND election_year = 2017", {"constituency": constituency}).fetchone()

    voter_index = constituency_response.voter_index
    code = constituency_response.constituency_code

    results = db.execute("SELECT * FROM results WHERE constituency_code = :code AND election_year = 2017", {"code": code}).fetchall()

    print(results)

    return render_template("results.html", constituency = constituency, voter_index = voter_index, results = results)


@app.route('/fancyvisuals', methods=['POST'])
def fancyvis():

    return "I will do some fancy visuals in this route"


if __name__ == '__main__':
    app.run()
