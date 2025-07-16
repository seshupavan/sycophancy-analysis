import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

# 1. Load data
df = pd.read_csv('./conversations.csv')
user_df = df[df["Role"] == "USER"].copy()

# 2. TF-IDF vectorization
tfidf = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), min_df=3, max_features=20000)
X = tfidf.fit_transform(user_df["Text"].fillna(""))

# 3. KMeans clustering with k=5
k = 5
kmeans = KMeans(n_clusters=k, n_init=20, random_state=42).fit(X)
user_df['cluster'] = kmeans.labels_

# 4. Build summary for each cluster
terms = tfidf.get_feature_names_out()
summary = []
for i in range(k):
    center = kmeans.cluster_centers_[i]
    top_idx = center.argsort()[::-1][:10]
    top_terms = ", ".join(terms[idx] for idx in top_idx)
    subset = user_df[user_df['cluster'] == i]
    n_messages = subset.shape[0]
    n_conversations = subset['Conversation'].nunique()
    summary.append({
        'cluster': i,
        'top_terms': top_terms,
        'n_messages': n_messages,
        'n_conversations': n_conversations
    })

summary_df = pd.DataFrame(summary)


# After manual analysis i found cluster 0 and 3 better reflect affective conversations
target_clusters = [0, 3]
target_conversations = user_df[user_df['cluster'].isin(target_clusters)]['Conversation'].unique()
# 2. Filter all messages for those conversations
filtered_df = df[df['Conversation'].isin(target_conversations)]
# 3. Save to a new CSV file
filtered_df.to_csv('cluster_0_3_conversations.csv', index=False)

