import json
import pandas as pd
import os
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load bars from JSON file
def load_bars(file_path="bar-recs/bars.json"):
    abs_path = os.path.join(os.path.dirname(__file__), "../bar-recs/bars.json")
    with open(file_path, 'r') as f: bars = json.load(f) # open bars.json

    bar_data = []
    for name, attributes in bars.items():
        bar_data.append({
            "Name": name,
            "Type": attributes[0],
            "Occasion": attributes[1],
            "Area": attributes[2],
            "Reservation": attributes[3],
            "Cost": attributes[4],
            "Rating": attributes[5]
        })
    return pd.DataFrame(bar_data)

# Combine relavent characteristics
def combine_features(row):
    return f"{row['Type']} {row['Occasion']} {row['Area']} {row['Cost']}"

# Preprocess data
def preprocess_bars(bars_df):
    bars_df["Combined"] = bars_df.apply(combine_features, axis=1)
    return bars_df

# Compute cosine similarity matrix
def compute_sim_matrix(bars_df):
    count_vectorizer = CountVectorizer()
    count_matrix = count_vectorizer.fit_transform(bars_df['Combined'])
    return cosine_similarity(count_matrix)

# Recommend bars based on user preference
def recommend_bars(user_bars, bars_df, cosine_sim):
    user_bar_indices = [bars_df.index[bars_df['Name'] == bar].tolist()[0] for bar in user_bars]
    sim_scores = cosine_sim[user_bar_indices].mean(axis=0)
    ranked_indices = sim_scores.argsort()[::-1]

    # get recommendations
    recommendations = [
        {
            "name": bars_df.iloc[i]["Name"],
            "type": bars_df.iloc[i]["Type"],
            "occasion": bars_df.iloc[i]["Occasion"],
            "area": bars_df.iloc[i]["Area"],
            "reservation": bars_df.iloc[i]["Reservation"],
            "cost": bars_df.iloc[i]["Cost"]
        }
        for i in ranked_indices if i not in user_bar_indices
    ]
    return recommendations[:5] # list top 5