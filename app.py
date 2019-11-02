from flask import Flask, render_template, request
import requests
import json
app = Flask(__name__)


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

    print(result)

    return result.get("parliamentary_constituency")

@app.route('/fancyvisuals', methods=['POST'])
def fancyvis():

    return "I will do some fancy visuals in this route"


if __name__ == '__main__':
    app.run()
