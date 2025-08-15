import pandas as pd
import sqlite3
import os
def load_data():
    # file path
    processed_dir = 'data/processed/'
    db_path = "data/databases/wikip_cs.db"
    wikip_parquet = "wikip_cleaned.parquet"
    wikip_table = 'wikip_cleaned'
    wiki_parquet = ''
    # checks if the processed directory exists
    os.makedirs(processed_dir, exist_ok=True)
    # connects to database
    conn = sqlite3.connect(db_path)
    wikip_df = pd.read_sql(f"SELECT * FROM {wikip_table}", conn)
    # adds columns to parquet
    wikip_df.columns = ['prev', 'curr', 'type', 'n']
    wiki_parquet= wikip_df.to_parquet(processed_dir + wikip_parquet, engine="pyarrow", index=False)
    print("Wikipedia database converted into Parquet file")
    # loads the transformed data
    # wikip_df = pd.read_csv(os.path.join(processed_dir, 'clickstream-enwiki-2025-06-processed.csv'))
    shop_df = pd.read_csv(os.path.join(processed_dir, 'e-shop-clothing-2008-processed.csv'), sep = ',')

    return wiki_parquet, shop_df

if __name__ == "__main__":
    load_data()