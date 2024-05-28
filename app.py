from flask import Flask, render_template, request, redirect, url_for, Response
from flask_sqlalchemy import SQLAlchemy
import requests
import json
import os, csv
from models import Constituency, Result, db
from pprint import pprint

# from sqlalchemy import create_engine
# from sqlalchemy.orm import scoped_session, sessionmaker

import urllib


from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("JAWSDB_URL")
db.init_app(app)

# engine = create_engine(os.getenv("JAWSDB_URL")) # database engine object from SQLAlchemy that manages connections to the database
#                                                 # DATABASE_URL is an environment variable that indicates where the database lives
# db = scoped_session(sessionmaker(bind=engine))    # create a 'scoped session' that ensures different users' interactions with the
#                                                 # database are kept separate


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

    # If postcode not found
    if r['status'] == 404:
        return render_template("index.html", title="What is your vote worth?", error="Postcode not found - please enter a full, valid UK postcode")

    result = r['result']

    constituency = result.get("parliamentary_constituency_2024")

    constituency_url_encoded = urllib.parse.quote_plus(constituency)

    return redirect(url_for('results', constituency=constituency_url_encoded))

@app.route('/<string:constituency>')
def results(constituency):
    # Decode URL
    constituency = urllib.parse.unquote_plus(constituency)

    # Get power index and constituency_code
    constituency_response = Constituency.query.filter_by(election_year=2019, constituency=constituency).one_or_none()

    if constituency_response is None:
        return Response("Constituency not found", status=404)
    print(constituency_response.constituency)
    

    # Calculate average voter index for 2019
    constituencies = Constituency.query.filter_by(election_year=2019).order_by(Constituency.voter_index.desc()).all()

    total_voter_index = 0
    max_voter_index = 0
    min_voter_index = 1000
    for constituency in constituencies:
        total_voter_index += constituency.voter_index
        if constituency.voter_index > max_voter_index:
            max_voter_index = constituency.voter_index
        if constituency.voter_index < min_voter_index:
            min_voter_index = constituency.voter_index

    average_voter_index = total_voter_index / len(constituencies)

    # Get first five constituencies
    top_five = constituencies[:5]

    # Get last five constituencies
    bottom_five = constituencies[-5:]


    efficiency = round(average_voter_index * 100)
    voter_index = round(constituency_response.voter_index, 4)
    code = constituency_response.constituency_code
    ranking = constituency_response.ranking

    ## Get full 2019 election results for constituency
    results = Result.query.filter_by(constituency_code=code, election_year=2019).order_by(Result.votes.desc()).all()

    # Work out comparison with national average
    if average_voter_index > voter_index:
        power_comparison = str(round(average_voter_index / voter_index))
        power_comparison_text = power_comparison+"x less"
    else:
        power_comparison = str(round(voter_index / average_voter_index))
        power_comparison_text = power_comparison+"x more"

    total_votes = 0

    results_sorted = sorted(results, key=lambda x: x.votes, reverse=True)

    party_name_lookup = {
        "Con": "Conservative",
        "Lab": "Labour",
        "LD": "Liberal Democrat",
        "Grn": "Green",
        "Brx": "Brexit Party (now Reform UK)",
        "SNP": "Scottish National Party",
        "PC": "Plaid Cymru",
        "DUP": "Democratic Unionist Party",
        "SF": "Sinn Féin",
        "APNI": "Alliance Party of Northern Ireland",
        "SDLP": "Social Democratic and Labour Party",
        "UUP": "Ulster Unionist Party",
        "Aontú": "Aontú",
        "PBP": "People Before Profit",
        "Con (NI)": "Conservative",
        "Grn (NI)": "Green",
        "Other[a]": "Other"
    }

    party_colour_lookup = {
        "Con": "#0087DC",
        "Lab": "#DC241f",
        "LD": "#FAA61A",
        "Grn": "#6AB023",
        "Brx": "#12B6CF",
        "SNP": "#FFF95D",
        "PC": "#008142",
        "DUP": "#D46A4C",
        "SF": "#326760",
        "APNI": "#99FF66",
        "SDLP": "#99CCFF",
        "UUP": "#9999FF",
        "Aontú": "#800000",
        "PBP": "#800080",
        "Con (NI)": "#0087DC",
        "Grn (NI)": "#6AB023",
        "Other[a]": "#CCCCCC"
    }

    total_votes = 0
    results_array = []
    results_array.append(["Party", "Votes"])
    colours_array = []
    for result in results:
        results_array.append([party_name_lookup[result.party], result.votes])
        colours_array.append(party_colour_lookup[result.party])
        
        total_votes += result.votes

    pprint(results_array)


    # Votes of second placed candidate
    # second_placed_votes = results[1][4]
    second_placed_votes = results_sorted[1].votes

    # Votes that went to candidates other than the winner
    # non_winner_votes = total_votes - results[0][4]
    non_winner_votes = total_votes - results_sorted[0].votes

    # Surplus votes for winner over those needed to beat second place
    # surplus_votes = results[0][4] - results[1][4]
    surplus_votes = results_sorted[0].votes - results_sorted[1].votes

    # Total wasted votes
    total_wasted_votes = surplus_votes + non_winner_votes

    # Winning party and second-placed party
    winning_party = party_name_lookup[results_sorted[0].party]
    second_placed_party = party_name_lookup[results_sorted[1].party]

    # URL encode constituency for sharing
    # constituency_encode = constituency.constituency.replace(" ", "%20")
    #constituency_encode = urllib.parse.quote_plus(constituency_encode)
    # constituency_encode = urllib.parse.quote_plus(constituency.constituency)

    # Encode URL for sharing as query string
    url = url_for('results', constituency=urllib.parse.quote_plus(constituency_response.constituency), _external=True)
    url = urllib.parse.quote_plus(url)


    return render_template("results.html", constituency = constituency_response.constituency, url=url, voter_index = voter_index, average_voter_index = average_voter_index, results = results, power_comparison_text = power_comparison_text, second_placed_votes = second_placed_votes, non_winner_votes = non_winner_votes, surplus_votes = surplus_votes, total_wasted_votes = total_wasted_votes, winning_party = winning_party, second_placed_party = second_placed_party, efficiency = efficiency, ranking = ranking,  top_five = top_five, bottom_five = bottom_five, results_array = results_array, colours_array = colours_array, max_voter_index = max_voter_index, min_voter_index = min_voter_index, quote_plus=urllib.parse.quote_plus, title = "Results for "+constituency_response.constituency)


@app.route('/privacy')
def privacy():
    return render_template("privacy.html", title = "Privacy Policy")


@app.route('/methodology')
def methodology():
    return render_template("methodology.html", title = "Methodology")

if __name__ == '__main__':
    app.run()
