import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns
import os
import logging

# configures logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[
    logging.StreamHandler(),  # logs to console
    logging.FileHandler('generate_wikipedia_sankey.log', mode='a')  # logs to a file
])

PARQUET_PATH = "data/processed/wikip_cleaned.parquet"  # output from ETL
OUTPUT_DIR = "data/outputs"



def generate_sankey(df, source_col, target_col, title):
    """
    Generates a Sankey diagram for the flow between source_col and target_col.
    Assumes df already has mapped categorical labels (no numeric codes).
    """
    try:
        logging.info(f"Generating Sankey diagram for {title}...")

        # create a copy of the filtered data
        df_filtered = df.loc[:, [source_col, target_col, 'session_id']].copy()

        # calculate flows (number of sessions per source-target pair)
        flows = df_filtered.groupby([source_col, target_col]).size().reset_index(name='n')
        if flows.empty:
            logging.warning(f"No flows found for {title}.")
            return

        # build unique node list and indices
        all_nodes = list(pd.unique(flows[source_col].tolist() + flows[target_col].tolist()))
        node_index = {label: idx for idx, label in enumerate(all_nodes)}

        # map source/target labels to indices
        flows['source'] = flows[source_col].map(node_index)
        flows['target'] = flows[target_col].map(node_index)

        # extract lists for Sankey diagram
        sources = flows['source'].tolist()
        targets = flows['target'].tolist()
        values = flows['n'].tolist()

        # create Sankey diagram
        fig = go.Figure(go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=all_nodes
            ),
            link=dict(
                source=sources,
                target=targets,
                value=values
            )
        ))

        fig.update_layout(
            title_text=title,
            font_size=10
        )

        # saves and displays the figure
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        output_path = os.path.join(OUTPUT_DIR, f"{title.replace(' ', '_').lower()}.html")
        fig.write_html(output_path)
        logging.info(f"Sankey diagram saved to: {output_path}")
        fig.show()

    except Exception as e:
        logging.error(f"Error generating Sankey diagram for {title}: {e}")


def create_heatmap(data, title, x_label, y_label):
    """
    Creates and displays a heatmap for the given data.
    """
    plt.figure(figsize=(10, 8))
    sns.heatmap(data, annot=True, cmap="Blues", cbar_kws={'label': 'Interaction Count'})
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.show()


def create_shopping_visualizations():
    """
    Creates Sankey diagrams and heatmaps for visualizing shopping sessions.
    """
    try:
        logging.info("Loading data...")
        file_path = 'data/processed/e-shop-clothing-2008-processed.csv'
        df = pd.read_csv(file_path)
        logging.info("Data loaded successfully.")
    except Exception as e:
        logging.error(f"Error loading data from CSV: {e}")
        return

    # categorical mappings
    country_mapping = {1:'Australia', 2:'Austria', 3:'Belgium', 4:'British Virgin Islands',
                       5:'Cayman Islands', 6:'Christmas Island', 7:'Croatia', 8:'Cyprus',
                       9:'Czech Republic', 10:'Denmark', 11:'Estonia', 12:'unidentified',
                       13:'Faroe Islands', 14:'Finland', 15:'France', 16:'Germany',
                       17:'Greece', 18:'Hungary', 19:'Iceland', 20:'India', 21:'Ireland',
                       22:'Italy', 23:'Latvia', 24:'Lithuania', 25:'Luxembourg', 26:'Mexico',
                       27:'Netherlands', 28:'Norway', 29:'Poland', 30:'Portugal', 31:'Romania',
                       32:'Russia', 33:'San Marino', 34:'Slovakia', 35:'Slovenia', 36:'Spain',
                       37:'Sweden', 38:'Switzerland', 39:'Ukraine', 40:'United Arab Emirates',
                       41:'United Kingdom', 42:'USA', 43:'biz (*.biz)', 44:'com (*.com)',
                       45:'int (*.int)', 46:'net (*.net)', 47:'org (*.org)'}

    category_mapping = {1:'Trousers', 2:'Skirts', 3:'Blouses', 4:'Sale'}

    colour_mapping = {1:'Beige', 2:'Black', 3:'Blue', 4:'Brown', 5:'Burgundy', 6:'Gray',
                      7:'Green', 8:'Navy Blue', 9:'Of Many Colors', 10:'Olive', 11:'Pink',
                      12:'Red', 13:'Violet', 14:'White'}

    location_mapping = {1:'Top Left', 2:'Top Middle', 3:'Top Right',
                        4:'Bottom Left', 5:'Bottom Middle', 6:'Bottom Right'}

    # maps numeric codes to text readable categorical labels
    df['country'] = df['country'].map(country_mapping)
    df['page_1_main_category'] = df['page_1_main_category'].map(category_mapping)
    df['colour'] = df['colour'].map(colour_mapping)
    df['location'] = df['location'].map(location_mapping)

    try:
        # Heatmaps
        logging.info("Creating heatmap for Country vs. Main Category...")
        country_category_data = df.groupby(['country', 'page_1_main_category']).size().unstack(fill_value=0)
        create_heatmap(country_category_data, 'Country vs. Main Category', 'Main Category', 'Country')

        logging.info("Creating heatmap for Main Category vs. Clothing Model...")
        category_model_data = df.groupby(['page_1_main_category', 'page_2_clothing_model']).size().unstack(fill_value=0)
        create_heatmap(category_model_data, 'Main Category vs. Clothing Model', 'Clothing Model', 'Main Category')

        logging.info("Creating heatmap for Location vs. Main Category...")
        location_category_data = df.groupby(['location', 'page_1_main_category']).size().unstack(fill_value=0)
        create_heatmap(location_category_data, 'Location vs. Main Category', 'Main Category', 'Location')

        logging.info("Creating heatmap for Colour vs. Main Category...")
        colour_category_data = df.groupby(['colour', 'page_1_main_category']).size().unstack(fill_value=0)
        create_heatmap(colour_category_data, 'Colour vs. Main Category', 'Main Category', 'Colour')

        logging.info("Creating heatmap for Price vs. Main Category...")
        price_category_data = df.groupby(['price_2', 'page_1_main_category']).size().unstack(fill_value=0)
        create_heatmap(price_category_data, 'Price vs. Main Category', 'Main Category', 'Price')

        # creates sankey Diagrams
        logging.info("Generating Sankey diagrams...")
        generate_sankey(df, 'country', 'page_1_main_category', 'Country to Main Category')
        generate_sankey(df, 'location', 'page_1_main_category', 'Location to Main Category')
        generate_sankey(df, 'colour', 'page_1_main_category', 'Colour to Main Category')
        generate_sankey(df, 'price_2', 'page_1_main_category', 'Price to Main Category')

    except Exception as e:
        logging.error(f"Error in creating visualizations: {e}")

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

def generate_wikipedia_heatmap(wikip_df, top_n=25):
    """
    Generates a heatmap showing the interactions between Wikipedia pages, limited to the top N articles.
    Filters out zero interactions for a cleaner visualization.

    Parameters:
    - wikip_df: DataFrame with columns ['prev', 'curr', 'type', 'n']
    - top_n: The number of top articles to consider (based on interaction frequency).
    """
    try:
        # limits to the top N most frequent interactions
        top_interactions = wikip_df.groupby(['prev', 'curr'])['n'].sum().reset_index()
        top_interactions = top_interactions.nlargest(top_n, 'n')

        # creates a pivot table
        heatmap_data = top_interactions.pivot_table(index='prev', columns='curr', values='n', aggfunc='sum', fill_value=0)


        # creates heatmap
        plt.figure(figsize=(16, 14)) 
        ax = sns.heatmap(heatmap_data, cmap='YlGnBu', annot=True, fmt='.0f', cbar=True, linewidths=0.5, square=True,
                         annot_kws={'size': 6}, cbar_kws={'label': 'Interaction Count'}) # low font 'size' to fit numbers 

        # rotates axis labels
        plt.xticks(rotation=90, ha='right', fontsize=12)
        plt.yticks(rotation=0, fontsize=12)

        # adds title and labels
        plt.title("Wikipedia Clickstream Interaction Heatmap (Top N Articles)", fontsize=16)
        plt.xlabel("Current Article (curr)", fontsize=12)
        plt.ylabel("Previous Article (prev)", fontsize=12)

        # saves heatmap
        output_path = os.path.join(OUTPUT_DIR, "wikipedia_clickstream_heatmap_top_n_filtered.png")
        plt.savefig(output_path, bbox_inches='tight')
        logging.info(f"Filtered Heatmap saved to: {output_path}")

        plt.show()

    except Exception as e:
        logging.error(f"Error generating heatmap: {e}")
        raise
if __name__ == "__main__":
    try:
        # loads the first 100 rows of wikipedia dataset from Parquet
        wikip_df = pd.read_parquet(PARQUET_PATH).head(100)
        logging.info(f"First 100 rows loaded from {PARQUET_PATH}")

        # checks if columns are correctly named
        wikip_df.columns = ['prev', 'curr', 'type', 'n']
        logging.info("Columns renamed to: ['prev', 'curr', 'type', 'n']")

        generate_wikipedia_sankey(wikip_df)
        generate_wikipedia_heatmap(wikip_df) 
        create_shopping_visualizations()
    except Exception as e:
        logging.error(f"Error in processing: {e}")