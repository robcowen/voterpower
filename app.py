from flask import Flask, render_template, request, redirect
import requests
import json
import os, csv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

import urllib

app = Flask(__name__)

engine = create_engine(os.getenv("JAWSDB_URL")) # database engine object from SQLAlchemy that manages connections to the database
                                                # DATABASE_URL is an environment variable that indicates where the database lives
db = scoped_session(sessionmaker(bind=engine))    # create a 'scoped session' that ensures different users' interactions with the
                                                # database are kept separate


@app.route('/')
def index():
    return render_template("index.html", title="What is your vote worth?")

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
    constituency_response = db.execute("SELECT id, voter_index, constituency_code, ranking FROM constituencies WHERE constituency = :constituency AND election_year = 2017", {"constituency": constituency}).fetchone()

    # Get average voter index
    average_voter_index = db.execute("SELECT AVG(voter_index) AS average_voter_index FROM constituencies", {}).fetchone()

    # Get top five constituencies
    top_five = db.execute("SELECT constituency, voter_index FROM constituencies WHERE election_year = 2017 ORDER BY voter_index DESC LIMIT 5", {}).fetchall()

    # Get bottom five constituencies
    bottom_five = db.execute("SELECT constituency, voter_index FROM constituencies WHERE election_year = 2017 ORDER BY voter_index ASC LIMIT 5", {}).fetchall()

    average_voter_index = round(average_voter_index[0],4)
    efficiency = round(average_voter_index * 100)
    voter_index = round(constituency_response.voter_index, 4)
    code = constituency_response.constituency_code
    ranking = constituency_response.ranking

    ## Get full 2017 election results for constituency
    results = db.execute("SELECT * FROM results WHERE constituency_code = :code AND election_year = 2017", {"code": code}).fetchall()

    # Work out comparison with national average
    if average_voter_index > voter_index:
        power_comparison = str(round(average_voter_index / voter_index))
        power_comparison_text = power_comparison+"x less"
    else:
        power_comparison = str(round(voter_index / average_voter_index))
        power_comparison_text = power_comparison+"x more"

    total_votes = 0

    results_dict = {
        'Conservative': 0,
        'Labour': 0,
        'Lib Dem': 0,
        'Scottish National Party': 0,
        'Plaid Cymru': 0,
        'Green': 0,
        'UKIP': 0,
        'Independent': 0
    }

    for result in results:
        # Get total votes
        total_votes += result[4]

        # Create dict of results
        results_dict[result[3]] = result[4]



    # Votes of second placed candidate
    second_placed_votes = results[1][4]

    # Votes that went to candidates other than the winner
    non_winner_votes = total_votes - results[0][4]

    # Surplus votes for winner over those needed to beat second place
    surplus_votes = results[0][4] - results[1][4]

    # Total wasted votes
    total_wasted_votes = surplus_votes + non_winner_votes

    # Winning party and second-placed party
    winning_party = results[0][3]
    second_placed_party = results[1][3]

    # URL encode constituency for sharing
    constituency_encode = constituency.replace(" ", "%20")
    constituency_encode = urllib.parse.quote_plus(constituency_encode)



    return render_template("results.html", constituency = constituency, voter_index = voter_index, average_voter_index = average_voter_index, results = results, power_comparison_text = power_comparison_text, second_placed_votes = second_placed_votes, non_winner_votes = non_winner_votes, surplus_votes = surplus_votes, total_wasted_votes = total_wasted_votes, winning_party = winning_party, second_placed_party = second_placed_party, efficiency = efficiency, ranking = ranking, constituency_encode = constituency_encode, top_five = top_five, bottom_five = bottom_five, results_dict = results_dict)




if __name__ == '__main__':
    app.run()
