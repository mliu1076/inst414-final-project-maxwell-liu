import os
import sqlite3
import pandas as pd
import logging

# configure error logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[
    logging.StreamHandler(),  # logs to console
    logging.FileHandler('load_data.log', mode='a')  # logs to a file
])

def load_data():
    processed_dir = 'data/processed/'
    db_path = "data/databases/wikip_cs.db"
    wikip_parquet = "wikip_cleaned.parquet"
    wikip_table = 'wikip_cleaned'
    wiki_parquet = ''
    
    # checks if the processed directory exists
    try:
        os.makedirs(processed_dir, exist_ok=True)
        logging.info(f"Processed directory '{processed_dir}' ensured.")
    except Exception as e:
        logging.error(f"Error ensuring processed directory: {e}")
        raise

    # connects to the database
    try:
        conn = sqlite3.connect(db_path)
        logging.info(f"Successfully connected to the database: {db_path}")
    except Exception as e:
        logging.error(f"Error connecting to the database: {e}")
        raise

    # query and loads data from the database
    try:
        wikip_df = pd.read_sql(f"SELECT * FROM {wikip_table}", conn)
        logging.info(f"Successfully loaded data from table '{wikip_table}' in the database.")
    except Exception as e:
        logging.error(f"Error reading data from database table '{wikip_table}': {e}")
        conn.close()
        raise

    # add columns to the dataframe
    try:
        wikip_df.columns = ['prev', 'curr', 'type', 'n']
        logging.info("Columns in the Wikipedia DataFrame renamed successfully.")
    except Exception as e:
        logging.error(f"Error renaming columns: {e}")
        conn.close()
        raise

    # saves dataFrame to Parquet file
    try:
        wikip_parquet_path = os.path.join(processed_dir, wikip_parquet)
        wikip_df.to_parquet(wikip_parquet_path, engine="pyarrow", index=False)
        logging.info(f"Wikipedia DataFrame saved as Parquet file: {wikip_parquet_path}")
    except Exception as e:
        logging.error(f"Error saving DataFrame to Parquet: {e}")
        conn.close()
        raise

    # loads the e-shop dataset 
    try:
        shop_df = pd.read_csv(os.path.join(processed_dir, 'e-shop-clothing-2008-processed.csv'), sep=',')
        logging.info(f"E-shop dataset loaded successfully from 'e-shop-clothing-2008-processed.csv'.")
    except Exception as e:
        logging.error(f"Error loading e-shop dataset: {e}")
        conn.close()
        raise

    # returns the Parquet file path and the shop dataframe
    conn.close()
    return wikip_parquet_path, shop_df
