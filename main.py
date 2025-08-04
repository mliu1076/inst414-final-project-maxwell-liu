from etl.extract import extract_data
from etl.transform import transform_data
from etl.load import load_data
from analysis.evaluate_model import analyze_shopping, analyze_wikipedia
# executes etl process from etl .py files
extract_data()
transform_data()
wikip_df, shop_df = load_data()

analyze_wikipedia(wikip_df)
analyze_shopping(shop_df)