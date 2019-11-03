import os, csv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("JAWSDB_URL")) # database engine object from SQLAlchemy that manages connections to the database
                                                # DATABASE_URL is an environment variable that indicates where the database lives
db = scoped_session(sessionmaker(bind=engine))    # create a 'scoped session' that ensures different users' interactions with the
                                                # database are kept separate

f = open("csv/full-2017-results.csv")
reader = csv.reader(f)
i = 0
for Year, Code, Party, Candidate_Votes in reader: # loop gives each column a name
    i += 1
    if i == 1: continue # Skip first row (headings)
    db.execute("INSERT INTO results (election_year, constituency_code, party, votes) VALUES (:election_year, :constituency, :party, :votes)",
    {"election_year": Year, "constituency_code": Code, "party": Party, "votes": Candidate_Votes})

    print(f"Imported row {i} into table for constituency {Code} and party {Party} with votes {Candidate_Votes}")

db.commit() # transactions are assumed, so close the transaction finished
