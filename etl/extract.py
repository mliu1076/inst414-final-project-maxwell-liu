import pandas as pd
import sqlite3
import os
import requests
import zipfile
import io
import logging

# configures error logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[
    logging.StreamHandler(),  # logs to console
    logging.FileHandler('extract_data.log', mode='a')  # logs to a file
])

def extract_data():
    """
    Extract function of the ETL pipeline. 

    This function performs the following tasks:
    1. Creates a SQLite database to store the Wikipedia dataset.
    2. Downloads the first 10,000 rows from an the online Wikipedia TSV file source,
       and stores it in the database.
    3. Downloads a ZIP file containing a shopping dataset from the online source,
       extracts the enclosed CSV file, and saves it locally.
    """
    try:
        # file paths
        wikip_raw_url = 'https://dumps.wikimedia.org/other/clickstream/2025-06/clickstream-enwiki-2025-06.tsv.gz'  
        shop_clickstr_raw_url = 'https://archive.ics.uci.edu/static/public/553/clickstream+data+for+online+shopping.zip'  # URL to ZIP file
        output_dir = 'data/raw/'  
        db_path = "data/databases/wikip_cs.db"
        db_dir = os.path.dirname(db_path)

        # makes sure the database directory exists
        os.makedirs(db_dir, exist_ok=True)
        
        # creates connection to the database
        conn = sqlite3.connect(db_path)

        # makes sure the output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # reads/samples the first 10,000 rows from the raw TSV file
        try:
            wikip_df = pd.read_csv(wikip_raw_url, sep="\t", compression="gzip", on_bad_lines="skip", nrows=10000)
            logging.info("Successfully read the first 10,000 rows of the Wikipedia clickstream dataset")
        except Exception as e:
            logging.error(f"Error reading the Wikipedia TSV file: {e}")
            raise

        # saves the first 10,000 rows to the SQLite database
        try:
            wikip_df.to_sql("wikip_cs", conn, if_exists="replace", index=False)
            logging.info("Added Wikipedia dataset (first 10,000 rows) to the database")
        except Exception as e:
            logging.error(f"Error inserting Wikipedia dataset into the database: {e}")
            raise

        # close the database connection
        conn.close()

        # downloads and extract the e-shop dataset (CSV inside ZIP file)
        try:
            response = requests.get(shop_clickstr_raw_url)
            response.raise_for_status()  # raises an HTTPError if the response code is not 200
            with zipfile.ZipFile(io.BytesIO(response.content)) as zf:
                # lists files in the ZIP to find the specific CSV file
                zip_files = zf.namelist()
                logging.info(f"Files in ZIP: {zip_files}")

                csv_filename = 'e-shop clothing 2008.csv' 
                with zf.open(csv_filename) as file:
                    shop_df = pd.read_csv(file)
                    logging.info("Successfully loaded shopping clickstream dataset")
        except requests.exceptions.RequestException as e:
            logging.error(f"Error downloading the ZIP file: {e}")
            raise
        except zipfile.BadZipFile as e:
            logging.error(f"Error extracting ZIP file: {e}")
            raise
        except Exception as e:
            logging.error(f"Error reading the CSV from the ZIP file: {e}")
            raise

        # saves extracted data into the 'data/raw/' directory
        try:
            shop_df.to_csv(os.path.join(output_dir, 'e-shop-clothing-2008-raw.csv'), index=False)
            logging.info("Data has been saved to the 'data/raw/' directory.")
        except Exception as e:
            logging.error(f"Error saving the shopping clickstream data to CSV: {e}")
            raise

    except Exception as main_exception:
        # catches any other errors in the whole process and log a message
        logging.error(f"An error occurred: {main_exception}")

# if __name__ == "__main__":
#     extract_data()