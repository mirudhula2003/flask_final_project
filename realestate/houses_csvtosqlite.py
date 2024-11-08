import pandas as pd
from app import app, db, RealEstate  # Ensure 'RealEstate' is the correct model name for your database

# Function to add real estate entries from CSV to the database
def add_real_estate_from_csv(csv_file):
    # Read the CSV file into a pandas DataFrame
    df = pd.read_csv(csv_file)

    # Iterate through the rows of the DataFrame and add each entry to the database
    for index, row in df.iterrows():
        # Create a new RealEstate object for each row in the DataFrame
        real_estate = RealEstate(
            area_type=row['area_type'],
            availability=row['availability'],
            location=row['location'],
            size=row['size'],
            society=row['society'],
            total_sqft=row['total_sqft'],
            bath=row['bath'],
            balcony=row['balcony'],
            price=row['price']
        )

        # Add the real estate object to the session
        db.session.add(real_estate)

    # Commit the session to save all the entries to the database
    db.session.commit()
    print(f"{len(df)} real estate entries have been added to the database.")

# Ensure you have the application context when calling db.session
with app.app_context():
    add_real_estate_from_csv('/Users/mirudhulaloganath/Desktop/GUVI/python/assignment3/realestate/Bengaluru_House_Data.csv')
