import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import logging
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
# testing purposes
# import sys
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# from etl.load import load_data

# creates a directory to store charts if it doesn't exist
file_path = 'data/outputs/'
os.makedirs(file_path, exist_ok=True)

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# sets up error logging
logging.basicConfig(
    filename=os.path.join(LOG_DIR, "analysis.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


file_path = "data/outputs/"
os.makedirs(file_path, exist_ok=True)


def analyze_wikipedia(wikipedia_df):
    """
    Perform analysis on the Wikipedia clickstream dataset.

    This function generates descriptive statistics, visualizations,
    and performs sequence modeling using a Markov chain approach
    to understand browsing transitions. Saves generated plots and 
    transition probability CSV file to the `data/outputs/` directory
    and prints statistics.   

    Parameters
    - wikipedia_df : the Wikipedia dataframe
    """

    try:
        if wikipedia_df.empty:
            logging.error("Wikipedia dataset is empty.")
            return

        required_cols = {'prev', 'curr', 'type', 'n'}
        if not required_cols.issubset(wikipedia_df.columns):
            logging.error(f"Missing required columns in Wikipedia dataset. Required: {required_cols}")
            return

        logging.info("=== Wikipedia Clickstream Analysis ===")

        # referrer type analysis
        type_counts = wikipedia_df['type'].value_counts()
        logging.info(f"Referrer Type Distribution:\n{type_counts}")

        # top transitions
        top_transitions = wikipedia_df[['prev', 'curr', 'n']].sort_values(by='n', ascending=False).head(10)
        logging.info("Top Transitions (prev -> curr):\n%s", top_transitions.to_string(index=False))

        # visualization
        try:
            plt.figure(figsize=(8, 6))
            sns.countplot(data=wikipedia_df, x='type', order=type_counts.index)
            plt.title("Wikipedia Clickstream - Referrer Type Distribution")
            plt.xlabel("Type")
            plt.ylabel("Frequency")
            plt.tight_layout()
            chart_path = os.path.join(file_path, "wikipedia_referrer_type.png")
            plt.savefig(chart_path)
            plt.close()
            logging.info(f"Saved chart: {chart_path}")
        except Exception as viz_err:
            logging.error(f"Visualization error in analyze_wikipedia: {viz_err}")

        # sequence modeling (Markov chain style)
        try:
            wikipedia_df = wikipedia_df.sort_values(by=['prev', 'curr'])
            transitions = wikipedia_df.groupby(['prev', 'curr'])['n'].sum().reset_index()

            transition_probs = (
                transitions.groupby('prev')
                .apply(lambda x: x.assign(probability=x['n'] / x['n'].sum()))
                .reset_index(drop=True)
            )

            output_path = os.path.join(file_path, "wikipedia_transition_probs.csv")
            transition_probs.to_csv(output_path, index=False)
            logging.info(f"Saved Wikipedia transition probabilities to {output_path}")
        except Exception as seq_err:
            logging.error(f"Sequence modeling error in analyze_wikipedia: {seq_err}")

    except Exception as e:
        logging.exception(f"Unexpected error in analyze_wikipedia: {e}")


def analyze_shopping(shopping_df):
    """
    Perform analysis on the online shopping clickstream dataset.

    This function generates descriptive statistics, visualizations,
    builds a classification model to predict product categories,
    and performs sequence modeling using a Markov chain approach
    to capture user browsing patterns. Saves generated plots, 
    classification report, and transition probability CSV file 
    to the `data/outputs/` directory and prints statistics.

    Parameters

    shopping_df : shopping dataframe
    """
    try:
        if shopping_df.empty:
            logging.error("Shopping dataset is empty.")
            return

        logging.info("=== Online Shopping Clickstream Analysis ===")

        # session pathing analysis
        if {'session_id', 'order'}.issubset(shopping_df.columns):
            session_clicks = (
                shopping_df
                .groupby('session_id')
                .agg(max_order=('order', 'max'))
                .sort_values(by='max_order', ascending=False)
                .head(10)
            )
            logging.info(f"Top sessions with most clicks:\n{session_clicks}")
        else:
            logging.warning("Missing 'session_id' or 'order' columns for session pathing analysis.")

        # product and category popularity
        if 'page_1_main_category' in shopping_df.columns:
            top_categories = shopping_df['page_1_main_category'].value_counts().head(10)
            logging.info(f"Most Popular Categories:\n{top_categories}")

            try:
                plt.figure(figsize=(10, 6))
                top_categories.plot(kind='barh', title='Top Product Categories', color='skyblue')
                plt.xlabel("Number of Visits")
                plt.tight_layout()
                chart_path = os.path.join(file_path, "top_product_categories.png")
                plt.savefig(chart_path)
                plt.close()
                logging.info(f"Saved chart: {chart_path}")
            except Exception as viz_err:
                logging.error(f"Visualization error in analyze_shopping: {viz_err}")
        else:
            logging.warning("'page_1_main_category' column missing for category analysis.")

        if 'page_2_clothing_model' in shopping_df.columns:
            top_products = shopping_df['page_2_clothing_model'].value_counts().head(10)
            logging.info(f"Most Popular Products:\n{top_products}")

        # predictive modeling
        if {'order', 'page', 'page_1_main_category'}.issubset(shopping_df.columns):
            try:
                model_df = shopping_df[['order', 'page', 'page_1_main_category']].dropna()
                model_df['page_1_main_category'] = model_df['page_1_main_category'].astype('category')
                X = model_df[['order', 'page']]
                y = model_df['page_1_main_category'].cat.codes

                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
                clf = RandomForestClassifier(n_estimators=100, random_state=42)
                clf.fit(X_train, y_train)
                y_pred = clf.predict(X_test)

                logging.info("=== Classification Report for Predicting Main Category ===")
                logging.info("\n" + classification_report(y_test, y_pred))
            except Exception as model_err:
                logging.error(f"Error in classification modeling: {model_err}")
        else:
            logging.warning("Missing columns for predictive modeling.")

        # sequence modeling
        try:
            logging.info("=== Sequence Modeling on Shopping Dataset ===")
            shopping_df = shopping_df.sort_values(by=['session_id', 'order'])
            shopping_df['next_category'] = shopping_df.groupby('session_id')['page_1_main_category'].shift(-1)

            transitions = (
                shopping_df.dropna(subset=['next_category'])
                .groupby(['page_1_main_category', 'next_category'])
                .size()
                .reset_index(name='count')
            )

            transition_probs = (
                transitions.groupby('page_1_main_category')
                .apply(lambda x: x.assign(probability=x['count'] / x['count'].sum()))
                .reset_index(drop=True)
            )

            output_path = os.path.join(file_path, "shopping_transition_probs.csv")
            transition_probs.to_csv(output_path, index=False)
            logging.info(f"Saved shopping transition probabilities to {output_path}")
        except Exception as seq_err:
            logging.error(f"Sequence modeling error in analyze_shopping: {seq_err}")

    except Exception as e:
        logging.exception(f"Unexpected error in analyze_shopping: {e}")


# testing purposes
# if __name__ == "__main__":
#     wiki_parquet, shop_df = load_data()
#     wikip_df = pd.read_parquet(wiki_parquet).head(100)
#     analyze_wikipedia(wikip_df)
#     analyze_shopping(shop_df)