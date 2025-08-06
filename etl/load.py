import pandas as pd
import os
def load_data():
    # file path
    processed_dir = 'data/processed/'
    
    # checks if the processed directory exists
    os.makedirs(processed_dir, exist_ok=True)
    
    # loads the transformed data
    wikip_df = pd.read_csv(os.path.join(processed_dir, 'clickstream-enwiki-2025-06-processed.csv'))
    shop_df = pd.read_csv(os.path.join(processed_dir, 'e-shop-clothing-2008-processed.csv'), sep = ',')

    return wikip_df, shop_df