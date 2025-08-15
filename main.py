import pandas as pd
from etl.extract import extract_data
from etl.transform import transform_data
from etl.load import load_data
from vis.visualizations import generate_wikipedia_sankey
from analysis.evaluate_model import analyze_shopping, analyze_wikipedia
# executes etl process from etl .py files
extract_data()
transform_data()
wiki_parquet, shop_df = load_data()
wikip_df = pd.read_parquet(wiki_parquet).head(100)

# checks column names
wikip_df.columns = ['prev', 'curr', 'type', 'n']

generate_wikipedia_sankey(wikip_df)
analyze_wikipedia(wikip_df)
analyze_shopping(shop_df)