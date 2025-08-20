import pandas as pd
import os
import sqlite3
import logging

# configures logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[
    logging.StreamHandler(),  # logs to console
    logging.FileHandler('transform_data.log', mode='a')  # logs to a file
])

def transform_data():
    # file paths
    raw_dir = 'data/raw/'
    processed_dir = 'data/processed/'
    db_path = "data/databases/wikip_cs.db"
    raw_table = 'wikip_cs'
    # cleaned table name in database
    clean_table = 'wikip_cleaned'

    try:
        # checks if the processed directory exists
        os.makedirs(processed_dir, exist_ok=True)
        logging.info(f"Processed directory '{processed_dir}' ensured.")
    except Exception as e:
        logging.error(f"Error ensuring processed directory: {e}")
        raise

    try:
        # creates connection to database
        conn = sqlite3.connect(db_path)
        logging.info(f"Successfully connected to the database: {db_path}")
    except Exception as e:
        logging.error(f"Error connecting to the database: {e}")
        raise

    try:
        # Reads data from the database table
        wikip_df = pd.read_sql(f"SELECT * FROM {raw_table}", conn)
        logging.info(f"Successfully loaded data from table '{raw_table}' in the database.")
    except Exception as e:
        logging.error(f"Error reading data from database table '{raw_table}': {e}")
        conn.close()
        raise

    try:
        # reads shop data from CSV file
        shop_df = pd.read_csv(os.path.join(raw_dir, 'e-shop-clothing-2008-raw.csv'), sep=';')
        logging.info("Successfully loaded e-shop data.")
    except Exception as e:
        logging.error(f"Error loading e-shop CSV file: {e}")
        conn.close()
        raise

    try:
        # renames columns for the transformed dataframe
        wikip_df.columns = ['prev', 'curr', 'type', 'n']
        logging.info("Columns in wikip_df renamed successfully.")
    except Exception as e:
        logging.error(f"Error renaming columns in wikip_df: {e}")
        conn.close()
        raise

    try:
        # checks for missing values
        missing_values = wikip_df.isnull().sum()
        print("Missing values in wikip_df:")
        print(missing_values)

        # handles missing values with placeholders
        wikip_df = wikip_df.fillna({'prev': 'unknown', 'curr': 'unknown', 'type': 'other', 'n': 0})
        wikip_df_cleaned = wikip_df.dropna()

        # shows descriptive statistics for numeric columns (EDA)
        print("Descriptive statistics for numeric columns in wikip_df:")
        print(wikip_df.describe())

        # shows value counts for 'type' column (EDA)
        print("Value counts for 'type' column in wikip_df:")
        print(wikip_df['type'].value_counts())

        # saves cleaned database
        wikip_df_cleaned.to_sql(clean_table, conn, if_exists="replace", index=False)
        logging.info(f"Cleaned wikip_df saved to database table '{clean_table}'.")
    except Exception as e:
        logging.error(f"Error during data transformation or saving to database: {e}")
        conn.close()
        raise

    try:
        # saves the transformed data to the processed folder
        wikip_df_cleaned.to_csv(os.path.join(processed_dir, 'clickstream-enwiki-2025-06-processed.csv'), index=False)
        logging.info("Cleaned wikip_df saved to CSV in the processed directory.")
    except Exception as e:
        logging.error(f"Error saving transformed wikip_df to CSV: {e}")
        conn.close()
        raise

    try:
        # adds column names to shop_df
        shop_df.columns = ['year', 'month', 'day', 'order', 'country', 'session_id', 
                           'page_1_main_category', 'page_2_clothing_model', 'colour', 
                           'location', 'model_photography', 'price', 'price_2', 'page']

        # handles missing values
        shop_df = shop_df.dropna()  # drops rows with missing values

        # converts both price columns to numeric
        shop_df['price'] = pd.to_numeric(shop_df['price'], errors='coerce')
        shop_df['price_2'] = pd.to_numeric(shop_df['price_2'], errors='coerce')

        # shows data types and basic descriptive statistics (EDA)
        print("\nSecond file data (shop_df) summary:")
        print(shop_df.describe())  
        print(shop_df.info()) 
    except Exception as e:
        logging.error(f"Error transforming e-shop data: {e}")
        conn.close()
        raise

    try:
        # saves transformed data to processed folder
        shop_df.to_csv(os.path.join(processed_dir, 'e-shop-clothing-2008-processed.csv'), index=False)
        logging.info("Transformed e-shop data saved to CSV in the processed directory.")
    except Exception as e:
        logging.error(f"Error saving transformed e-shop data to CSV: {e}")
        conn.close()
        raise

    print("\nTransformation completed and data saved to the 'data/processed/' directory.")
    conn.close()

if __name__ == "__main__":
    transform_data()