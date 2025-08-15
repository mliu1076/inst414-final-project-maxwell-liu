import pandas as pd
import logging
import os
from etl.extract import extract_data
from etl.transform import transform_data
from etl.load import load_data
from vis.visualizations import generate_wikipedia_sankey
from analysis.evaluate_model import analyze_shopping, analyze_wikipedia

# === Error logging ===
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "etl_process.log")

logging.basicConfig(
    filename=LOG_FILE,
    filemode="a",  # append mode
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

def main():
    logging.info("ETL process started.")

    try:
        extract_data()
        logging.info("Data extraction completed successfully.")
    except Exception as e:
        logging.exception("Error during data extraction.")
        return

    try:
        transform_data()
        logging.info("Data transformation completed successfully.")
    except Exception as e:
        logging.exception("Error during data transformation.")
        return

    try:
        wiki_parquet, shop_df = load_data()
        logging.info(f"Data loaded successfully: {wiki_parquet}, shopping data shape: {shop_df.shape}")
    except Exception as e:
        logging.exception("Error during data loading.")
        return

    try:
        wikip_df = pd.read_parquet(wiki_parquet).head(100)
        logging.info(f"Wikipedia parquet file read successfully, shape: {wikip_df.shape}")

        # checks column names
        expected_cols = ['prev', 'curr', 'type', 'n']
        if list(wikip_df.columns) != expected_cols:
            wikip_df.columns = expected_cols
            logging.info("Wikipedia DataFrame columns renamed to: %s", expected_cols)

    except Exception as e:
        logging.exception("Error reading or preparing Wikipedia parquet data.")
        return

    try:
        generate_wikipedia_sankey(wikip_df)
        logging.info("Wikipedia Sankey diagram generated successfully.")
    except Exception as e:
        logging.exception("Error generating Wikipedia Sankey diagram.")

    try:
        analyze_wikipedia(wikip_df)
        logging.info("Wikipedia analysis completed successfully.")
    except Exception as e:
        logging.exception("Error during Wikipedia analysis.")

    try:
        analyze_shopping(shop_df)
        logging.info("Shopping analysis completed successfully.")
    except Exception as e:
        logging.exception("Error during shopping analysis.")

    logging.info("ETL process completed.")

if __name__ == "__main__":
    main()
    print(f"ETL process completed. See log file: {LOG_FILE}")