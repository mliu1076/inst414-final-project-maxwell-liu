import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report

# Create a directory to store charts if it doesn't exist
file_path = 'data/outputs/'

os.makedirs(file_path, exist_ok=True)

def analyze_wikipedia(wikipedia_df):
    print("=== Wikipedia Clickstream Analysis ===")

    # referrer type analysis
    type_counts = wikipedia_df['type'].value_counts()
    print("\nReferrer Type Distribution:\n", type_counts)

    # transition frequency analysis
    top_transitions = wikipedia_df[['prev', 'curr', 'n']].sort_values(by='n', ascending=False).head(10)
    print("\nTop Transitions (prev → curr):\n", top_transitions)

    # visualize referrer types
    plt.figure(figsize=(8, 6))
    sns.countplot(data=wikipedia_df, x='type', order=type_counts.index)
    plt.title("Wikipedia Clickstream - Referrer Type Distribution")
    plt.xlabel("Type")
    plt.ylabel("Frequency")
    plt.tight_layout()
    chart_path = os.path.join(file_path, "wikipedia_referrer_type.png")
    plt.savefig(chart_path)
    plt.close()
    print(f"Saved chart: {chart_path}")

def analyze_shopping(shopping_df):
    print("=== Online Shopping Clickstream Analysis ===")

    # session pathing analysis
    session_clicks = (
    shopping_df
    .groupby('session_id')
    .agg(max_order=('order', 'max'))
    .sort_values(by='max_order', ascending=False)
    .head(10)
    )
    print("\nTop sessions with most clicks:\n", session_clicks)

    # product and category popularity
    top_categories = shopping_df['page_1_main_category'].value_counts().head(10)
    top_products = shopping_df['page_2_clothing_model'].value_counts().head(10)

    print("\nMost Popular Categories:\n", top_categories)
    print("\nMost Popular Products:\n", top_products)

    # visualize top categories
    plt.figure(figsize=(10, 6))
    top_categories.plot(kind='barh', title='Top Product Categories', color='skyblue')
    plt.xlabel("Number of Visits")
    plt.tight_layout()
    chart_path = os.path.join(file_path, "top_product_categories.png")
    plt.savefig(chart_path)
    plt.close()
    print(f"Saved chart: {chart_path}")

    # predictive modeling: predict main category based on order and page number
    if {'order', 'page', 'page_1_main_category'}.issubset(shopping_df.columns):
        model_df = shopping_df[['order', 'page', 'page_1_main_category']].dropna()
        model_df['page_1_main_category'] = model_df['page_1_main_category'].astype('category')
        X = model_df[['order', 'page']]
        y = model_df['page_1_main_category'].cat.codes

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        clf = RandomForestClassifier(n_estimators=100, random_state=42)
        clf.fit(X_train, y_train)
        y_pred = clf.predict(X_test)

        print("\n=== Classification Report for Predicting Main Category ===")
        print(classification_report(y_test, y_pred))

