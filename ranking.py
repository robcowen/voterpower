import os, csv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("JAWSDB_URL")) # database engine object from SQLAlchemy that manages connections to the database
                                                # DATABASE_URL is an environment variable that indicates where the database lives
db = scoped_session(sessionmaker(bind=engine))    # create a 'scoped session' that ensures different users' interactions with the
                                                # database are kept separate

results = db.execute("SELECT id, voter_index FROM constituencies ORDER BY voter_index DESC", {}).fetchall()

i = 1

for result in results:
    print (result)
    db.execute("UPDATE constituencies SET ranking = :ranking WHERE id = :id",
    {"ranking": i, "id": result[0]})

    i += 1

db.commit() # transactions are assumed, so close the transaction finished
