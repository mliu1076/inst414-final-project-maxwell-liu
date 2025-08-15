import pandas as pd
import plotly.graph_objects as go
import os


PARQUET_PATH = "data/processed/wikip_cleaned.parquet"  # Output from ETL
OUTPUT_DIR = "data/outputs"

def generate_wikipedia_sankey(wikip_df):
    """
    Generates a Sankey diagram showing the navigation flow between Wikipedia pages.

    Parameters:
    - wikip_df: DataFrame with columns ['prev', 'curr', 'type', 'n']
    """

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # checks if columns exist
    required_cols = {'prev', 'curr', 'type', 'n'}
    if not required_cols.issubset(wikip_df.columns):
        raise ValueError(f"DataFrame must contain the following columns: {required_cols}")

    # get all unique labels and map them to indices
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

    # build Sankey diagram
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

    # save file
    output_path = os.path.join(OUTPUT_DIR, "wikipedia_sankey_colored.html")
    fig.write_html(output_path)
    print(f"Sankey diagram saved to: {output_path}")


# if __name__ == "__main__":
#     # loads the first 100 rows from Parquet
#     wikip_df = pd.read_parquet(PARQUET_PATH).head(100)

#     # Ensure columns are correctly named
#     wikip_df.columns = ['prev', 'curr', 'type', 'n']

#     generate_wikipedia_sankey(wikip_df)