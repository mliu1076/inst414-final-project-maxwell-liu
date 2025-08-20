import pandas as pd
import plotly.graph_objects as go
import os
import logging

# configures logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[
    logging.StreamHandler(),  # logs to console
    logging.FileHandler('generate_wikipedia_sankey.log', mode='a')  # logs to a file
])

PARQUET_PATH = "data/processed/wikip_cleaned.parquet"  # output from ETL
OUTPUT_DIR = "data/outputs"

def generate_wikipedia_sankey(wikip_df):
    """
    Generates a Sankey diagram showing the navigation flow between Wikipedia pages.

    Parameters:
    - wikip_df: DataFrame with columns ['prev', 'curr', 'type', 'n']
    """

    # ensures the output directory exists
    try:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        logging.info(f"Output directory '{OUTPUT_DIR}' ensured.")
    except Exception as e:
        logging.error(f"Error ensuring the output directory: {e}")
        raise

    # checks if the required columns exist
    required_cols = {'prev', 'curr', 'type', 'n'}
    if not required_cols.issubset(wikip_df.columns):
        error_message = f"DataFrame must contain the following columns: {required_cols}"
        logging.error(error_message)
        raise ValueError(error_message)
    else:
        logging.info(f"DataFrame contains the required columns: {required_cols}")

    try:
        # gets all unique labels and map them to indices
        labels = list(pd.unique(wikip_df[['prev', 'curr']].values.ravel()))
        label_indices = {label: i for i, label in enumerate(labels)}

        # map prev/curr to source/target indices
        wikip_df = wikip_df.copy()
        wikip_df['source'] = wikip_df['prev'].map(label_indices)
        wikip_df['target'] = wikip_df['curr'].map(label_indices)

        # map link type to color
        type_color_map = {
            'link': 'rgba(31, 119, 180, 0.6)',
            'external': 'rgba(255, 127, 14, 0.6)',
            'other': 'rgba(44, 160, 44, 0.6)'
        }
        wikip_df['color'] = wikip_df['type'].map(type_color_map).fillna('rgba(127,127,127,0.6)')
        logging.info("Data transformation for Sankey diagram completed.")
    except Exception as e:
        logging.error(f"Error during data transformation: {e}")
        raise

    try:
        # builds Sankey diagram
        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=labels
            ),
            link=dict(
                source=wikip_df['source'],
                target=wikip_df['target'],
                value=wikip_df['n'],
                color=wikip_df['color']
            )
        )])

        fig.update_layout(
            title_text="Wikipedia Clickstream Navigation (first 100 rows, colored by type)",
            font_size=10
        )
        logging.info("Sankey diagram created successfully.")
    except Exception as e:
        logging.error(f"Error creating Sankey diagram: {e}")
        raise

    try:
        # saves the Sankey diagram to an HTML file
        output_path = os.path.join(OUTPUT_DIR, "wikipedia_sankey_colored.html")
        fig.write_html(output_path)
        logging.info(f"Sankey diagram saved to: {output_path}")
    except Exception as e:
        logging.error(f"Error saving the Sankey diagram to HTML: {e}")
        raise

# if __name__ == "__main__":
#     try:
#         # Loads the first 100 rows from Parquet
#         wikip_df = pd.read_parquet(PARQUET_PATH).head(100)
#         logging.info(f"First 100 rows loaded from {PARQUET_PATH}")
# 
#         # Ensure columns are correctly named
#         wikip_df.columns = ['prev', 'curr', 'type', 'n']
#         logging.info("Columns renamed to: ['prev', 'curr', 'type', 'n']")
# 
#         generate_wikipedia_sankey(wikip_df)
#     except Exception as e:
#         logging.error(f"Error in processing: {e}")