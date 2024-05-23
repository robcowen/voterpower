from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Constituency(db.Model):
    __tablename__ = 'constituencies'
    
    id = db.Column(db.Integer, primary_key=True)
    election_year = db.Column(db.Integer)
    constituency_code = db.Column(db.String(45))
    constituency = db.Column(db.String(100))
    constituency_size = db.Column(db.Integer)
    winning_party = db.Column(db.String(45))
    votes_cast = db.Column(db.Integer)
    votes_for_winner = db.Column(db.Integer)
    majority_raw = db.Column(db.Integer)
    majority_percent = db.Column(db.Float)
    probability = db.Column(db.Float)
    normalised_population = db.Column(db.Float)
    voter_index = db.Column(db.Float)
    ranking = db.Column(db.Integer)

    def __init__(self, election_year, constituency_code, constituency, constituency_size, winning_party,
                 votes_cast, votes_for_winner, majority_raw, majority_percent, probability, normalised_population,
                 voter_index, ranking):
        self.election_year = election_year
        self.constituency_code = constituency_code
        self.constituency = constituency
        self.constituency_size = constituency_size
        self.winning_party = winning_party
        self.votes_cast = votes_cast
        self.votes_for_winner = votes_for_winner
        self.majority_raw = majority_raw
        self.majority_percent = majority_percent
        self.probability = probability
        self.normalised_population = normalised_population
        self.voter_index = voter_index
        self.ranking = ranking


class Result(db.Model):
    __tablename__ = 'results'
    
    id = db.Column(db.Integer, primary_key=True)
    election_year = db.Column(db.Integer)
    constituency_code = db.Column(db.String(45))
    party = db.Column(db.String(45))
    votes = db.Column(db.Integer)

    def __init__(self, election_year, constituency_code, party, votes):
        self.election_year = election_year
        self.constituency_code = constituency_code
        self.party = party
        self.votes = votes