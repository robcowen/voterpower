import os, csv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from models import Constituency, Result

from dotenv import load_dotenv

load_dotenv()

engine = create_engine(os.getenv("JAWSDB_URL")) # database engine object from SQLAlchemy that manages connections to the database
                                                # DATABASE_URL is an environment variable that indicates where the database lives
db = scoped_session(sessionmaker(bind=engine))    # create a 'scoped session' that ensures different users' interactions with the
                                                # database are kept separate

f = open("csv/power-index-2019.csv")

# Read CSV file
reader = csv.reader(f)

# Create keys for dictionary from first row
keys = next(reader)

print(keys)

i = 1
# Create dictionary from CSV file
for row in reader:
    row = dict(zip(keys, row))

    if row['ONS Code'] is None or row['ONS Code'] == "":
        continue
    

    # Create Constituency object
    constituency = Constituency(
        election_year = 2019,
        constituency_code = row['ONS Code'],
        constituency = row['\ufeffConstituency'],
        constituency_size = row['Total population'],
        winning_party = row['Party'],
        votes_cast = row['Total'],
        votes_for_winner = row['Votes for winner'],
        majority_raw = row['Majority'],
        majority_percent = row['% majority'],
        probability = row['Probability'],
        normalised_population = row['Population weighting'],
        voter_index = row['Voter Power Index'],
        ranking = i
    )

    print(i, constituency.constituency)


    i += 1
    # Add Constituency object to database
    db.add(constituency)

    db.commit() # transactions are assumed, so close the transaction finished

    # Constituency,ONS Code,Total population,Population weighting,Region,Country,Change,Party,Majority,Turnout,Con,Lab,LD,Grn,Brx,SNP,PC,DUP,SF,APNI,SDLP,UUP,Aontú,PBP,Con,Grn,Other[a],Total,Votes for winner,% majority,Probability,Voter Power Index

