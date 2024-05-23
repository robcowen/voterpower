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
reader = csv.reader(f)
i = 0

keys = next(reader)

print(keys)


# Loop through CSV file, only interested in columns in 'Con', 'Lab', 'LD', 'Grn', 'Brx', 'SNP', 'PC', 'DUP', 'SF', 'APNI', 'SDLP', 'UUP', 'Aontú', 'PBP', 'Con', 'Grn', 'Other[a]' and 'Constituency code'
for row in reader:
    row = dict(zip(keys, row))

    # Create Result objects for each party in each constituency
    for party in ['Con', 'Lab', 'LD', 'Grn', 'Brx', 'SNP', 'PC', 'DUP', 'SF', 'APNI', 'SDLP', 'UUP', 'Aontú', 'PBP']:
        if row['ONS Code'] is None or row['ONS Code'] == '':
            continue

        if row[party] is None or row[party] == '' or row[party] == '0':
            continue

        result = Result(
            election_year = 2019,
            constituency_code = row['ONS Code'],
            party = party,
            votes = row[party]
        )

        print(i, result.constituency_code, result.party, result.votes)

        i += 1

        db.add(result)

        db.commit() # transactions are assumed, so close the transaction finished
        