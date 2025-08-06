import pandas as pd
import os

def transform_data():
    # file paths
    raw_dir = 'data/raw/'
    processed_dir = 'data/processed/'

    # checks if the processed directory exists
    os.makedirs(processed_dir, exist_ok=True)

    # loads raw data
    wikip_df = pd.read_csv(os.path.join(raw_dir, 'clickstream-enwiki-2025-06-raw.csv'))
    shop_df = pd.read_csv(os.path.join(raw_dir, 'e-shop-clothing-2008-raw.csv'), sep = ';')

    # renames columns for transformed tsv file
    wikip_df.columns = ['prev', 'curr', 'type', 'n']

    # checks for missing values
    missing_values = wikip_df.isnull().sum()
    print("Missing values in wikip_df:")
    print(missing_values)

    # handles missing values with placeholders
    wikip_df = wikip_df.fillna({'prev': 'unknown', 'curr': 'unknown', 'type': 'other', 'n': 0})



    # shows descriptive statistics for numeric columns (EDA)
    print("Descriptive statistics for numeric columns in wikip_df:")
    print(wikip_df.describe())

    # shows value counts for 'type' column (EDA)
    print("Value counts for 'type' column in wikip_df:")
    print(wikip_df['type'].value_counts())


    # saves the transformed data to the processed folder
    wikip_df.to_csv(os.path.join(processed_dir, 'clickstream-enwiki-2025-06-processed.csv'), index=False)
    print("Transformed wikip_df data has been saved.")

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


    # saves transformed data to processed folder
    shop_df.to_csv(os.path.join(processed_dir, 'e-shop-clothing-2008-processed.csv'), index=False)

    print("\nTransformation completed and data saved to the 'data/processed/' directory.")