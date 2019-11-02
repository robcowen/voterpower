import os, csv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("JAWSDB_URL"), echo=True) # database engine object from SQLAlchemy that manages connections to the database
                                                # DATABASE_URL is an environment variable that indicates where the database lives
db = scoped_session(sessionmaker(bind=engine))    # create a 'scoped session' that ensures different users' interactions with the
                                                # database are kept separate

f = open("csv/power-index.csv")
reader = csv.reader(f)
i = 0
for Year,Code,Constituency,PC_Electors,Region,Party_Abbreviation,Party,Candidate_Votes,Vote_Share,Total_votes,Majority_Party,Majority,Majority_pc,Probability,Normalised_population,Index in reader: # loop gives each column a name
    i += 1
    if i == 1: continue # Skip first row (headings)
    db.execute("INSERT INTO power_index (election_year, constituency_code, constituency, constituency_size, winning_party, votes_cast, votes_for_winner, majority_raw, majority_percent, probability, normalised_population, index) VALUES (:election_year, :constituency_code, :constituency, :constituency_size, :winning_party, :votes_cast, :votes_for_winner, :majority_raw, :majority_percent, :probability, :normalised_population, :index)", {"election_year": Year, "constituency_code": Code, "constituency": Constituency, "constituency_size": PC_Electors, "winning_party": Party, "votes_cast": Total_votes, "votes_for_winner": Candidate_Votes, "majority_raw": Majority, "majority_percent": Majority_pc, "probability": Probability, "normalised_population": Normalised_population, "index": Index})

    print(f"Imported row {i} into table for constituency {Constituency} with index {Index}")

#db.commit() # transactions are assumed, so close the transaction finished
