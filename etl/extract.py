import pandas as pd
import sqlite3
import os
def extract_data():
    # file paths
    wikip_raw = 'data/extracted/clickstream-enwiki-2025-06.tsv'
    wikip_raw_url = 'https://dumps.wikimedia.org/other/clickstream/2025-06/clickstream-enwiki-2025-06.tsv.gz'  
    shop_clickstr_raw = 'data/extracted/e-shop clothing 2008.csv'  
    output_dir = 'data/raw/'  
    db_path = "data/databases/wikip_cs.db"
    conn = sqlite3.connect(db_path)
    # checks if the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # transforms tsv file to csv file so it is easier to use in the future 
    # skips bad lines since panda can't read some of the special characters in the file
    #wikip_df = pd.read_csv(wikip_raw, sep=r'\s+', encoding='utf-8', header=None, on_bad_lines='skip')  
    wikip_df = pd.read_csv(wikip_raw_url, sep="\t", compression="gzip", on_bad_lines="skip")
    print("Successfully read wikipedia clickstream dataset")
    wikip_df.to_sql("wikip_cs", conn, if_exists="replace", index=False)
    print("Added wikipedia dataset to database")
    conn.close()
    shop_df = pd.read_csv(shop_clickstr_raw)
    print("Successfully loaded shopping clickstream dataset")

    # saves the extracted data into the 'data/raw/' directory
    #wikip_df.to_csv(os.path.join(output_dir, 'clickstream-enwiki-2025-06-raw.csv'), index=False)
    shop_df.to_csv(os.path.join(output_dir, 'e-shop-clothing-2008-raw.csv'), index=False)
    print("Data has been saved to the 'data/raw/' directory.")

if __name__ == "__main__":
    extract_data()