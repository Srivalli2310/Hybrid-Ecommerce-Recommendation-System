"""
Hybrid Recommendation Engine module.
Implements Popularity-Based, Content-Based, Collaborative Filtering,
and Hybrid recommendations extracted from notebooks/E-commerce.ipynb.
"""

import os
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from model.data_loader import load_and_preprocess_data


DISPLAY_COLUMNS = ["Name", "ReviewCount", "Brand", "ImageUrl", "Rating", "ProdId"]


class HybridRecommender:
    """
    Production-ready wrapper for the recommendation algorithms
    defined in notebooks/E-commerce.ipynb.
    """

    def __init__(self, data=None, data_path=None):
        """
        Initializes the recommender with dataset and precomputes
        matrices for instant recommendation lookups.
        """
        if data is not None:
            self.data = data.copy()
        else:
            self.data = load_and_preprocess_data(data_path)

        self._fit()

    def _fit(self):
        """Precomputes rating aggregations, TF-IDF similarities, and user-item matrices."""
        # 1. Popularity / Rating-based (Notebook cells 34-36)
        avg_ratings = self.data.groupby(
            ["Name", "ReviewCount", "Brand", "ImageUrl", "ProdId"],
            as_index=False
        )["Rating"].mean()

        top_rated = avg_ratings.sort_values(
            by=["Rating", "ReviewCount"],
            ascending=[False, False]
        )
        self.popular_items = top_rated.copy()
        self.popular_items["Rating"] = self.popular_items["Rating"].round(1)
        self.popular_items["ReviewCount"] = self.popular_items["ReviewCount"].astype(int)

        # 2. Content-Based TF-IDF (Notebook cells 41-42, 52)
        self.tfidf_vectorizer = TfidfVectorizer(stop_words="english", max_features=5000)
        self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(self.data["Tags"].astype(str))

        # Create quick index lookup mapping by name (exact and normalized)
        self.name_to_index = {}
        for idx, name in enumerate(self.data["Name"]):
            if pd.notna(name) and str(name).strip():
                clean_name = str(name).strip()
                if clean_name not in self.name_to_index:
                    self.name_to_index[clean_name] = idx
                lower_name = clean_name.lower()
                if lower_name not in self.name_to_index:
                    self.name_to_index[lower_name] = idx

        # 3. Collaborative Filtering Matrix (Notebook cells 56-57, 66)
        self.user_item_matrix = self.data.pivot_table(
            index="Id",
            columns="ProdId",
            values="Rating",
            aggfunc="mean"
        ).fillna(0)

    def _format_result(self, df, top_n, as_dict=False):
        """Formats and limits the recommendation dataframe."""
        cols = [c for c in DISPLAY_COLUMNS if c in df.columns]
        result = df[cols].drop_duplicates(subset=["Name"]).head(top_n).copy()
        if as_dict:
            return result.to_dict(orient="records")
        return result

    def get_popular(self, top_n=10, as_dict=False):
        """
        Returns top trending/popular products based on rating and review count.
        (From notebook cells 34-39)
        """
        return self._format_result(self.popular_items, top_n, as_dict=as_dict)

    def get_content_based(self, item_name, top_n=10, as_dict=False):
        """
        Returns content-based recommendations similar to the given item name
        using TF-IDF cosine similarity on tags.
        (From notebook cells 42-52)
        """
        if not item_name or not isinstance(item_name, str):
            return [] if as_dict else pd.DataFrame(columns=DISPLAY_COLUMNS)

        clean_name = item_name.strip()
        item_index = self.name_to_index.get(clean_name)
        if item_index is None:
            item_index = self.name_to_index.get(clean_name.lower())

        if item_index is None:
            # Try partial substring match as fallback
            matches = self.data[self.data["Name"].astype(str).str.contains(clean_name, case=False, na=False, regex=False)]
            if not matches.empty:
                item_index = matches.index[0]

        if item_index is None:
            # Item not present
            return [] if as_dict else pd.DataFrame(columns=DISPLAY_COLUMNS)

        item_vec = self.tfidf_matrix[item_index]
        sim_scores = cosine_similarity(item_vec, self.tfidf_matrix).flatten()
        similar_items = list(enumerate(sim_scores))
        similar_items = sorted(similar_items, key=lambda x: x[1], reverse=True)

        # Exclude the item itself
        top_similar = similar_items[1: top_n + 1]
        recommended_indices = [x[0] for x in top_similar]

        rec_df = self.data.iloc[recommended_indices]
        return self._format_result(rec_df, top_n, as_dict=as_dict)

    def get_collaborative(self, target_user_id, top_n=10, as_dict=False):
        """
        Returns user-based collaborative filtering recommendations
        for the given target_user_id.
        (From notebook cells 56-66)
        """
        if target_user_id is None:
            return [] if as_dict else pd.DataFrame(columns=DISPLAY_COLUMNS)

        try:
            target_user_id = float(target_user_id)
        except (ValueError, TypeError):
            pass

        if target_user_id not in self.user_item_matrix.index:
            return [] if as_dict else pd.DataFrame(columns=DISPLAY_COLUMNS)

        target_user_index = self.user_item_matrix.index.get_loc(target_user_id)
        target_vec = self.user_item_matrix.iloc[[target_user_index]]
        user_similarities = cosine_similarity(target_vec, self.user_item_matrix).flatten()

        # Sort users by similarity in descending order (excluding target user)
        similar_users_indices = user_similarities.argsort()[::-1][1:]

        recommended_items = []
        target_ratings = self.user_item_matrix.iloc[target_user_index]

        for user_idx in similar_users_indices:
            rated_by_similar_user = self.user_item_matrix.iloc[user_idx]
            # Recommend items rated positively by similar user but not yet rated by target user
            candidates = (rated_by_similar_user > 0) & (target_ratings == 0)
            candidate_cols = self.user_item_matrix.columns[candidates].tolist()

            for pid in candidate_cols:
                if pid not in recommended_items:
                    recommended_items.append(pid)
                if len(recommended_items) >= top_n:
                    break
            if len(recommended_items) >= top_n:
                break

        if not recommended_items:
            return [] if as_dict else pd.DataFrame(columns=DISPLAY_COLUMNS)

        rec_details = self.data[self.data["ProdId"].isin(recommended_items)]
        return self._format_result(rec_details, top_n, as_dict=as_dict)

    def get_hybrid(self, target_user_id=None, item_name=None, top_n=10, as_dict=False):
        """
        Combines content-based and collaborative filtering recommendations,
        with popularity-based fallback for cold start.
        (From notebook cells 67-69)
        """
        cb_df = pd.DataFrame(columns=DISPLAY_COLUMNS)
        cf_df = pd.DataFrame(columns=DISPLAY_COLUMNS)

        if item_name:
            cb_df = self.get_content_based(item_name, top_n=top_n, as_dict=False)

        if target_user_id is not None:
            cf_df = self.get_collaborative(target_user_id, top_n=top_n, as_dict=False)

        # Merge and drop duplicates (from notebook cell 68)
        if not cb_df.empty and not cf_df.empty:
            merged = pd.concat([cb_df, cf_df]).drop_duplicates(subset=["Name"])
        elif not cb_df.empty:
            merged = cb_df
        elif not cf_df.empty:
            merged = cf_df
        else:
            merged = pd.DataFrame(columns=DISPLAY_COLUMNS)

        # Cold-start fallback: if recommendations are fewer than top_n, supplement with popular items
        if merged.empty:
            merged = self.get_popular(top_n=top_n, as_dict=False)
        elif len(merged) < top_n:
            popular = self.get_popular(top_n=top_n, as_dict=False)
            merged = pd.concat([merged, popular]).drop_duplicates(subset=["Name"])

        return self._format_result(merged, top_n, as_dict=as_dict)


# Global lazy singleton instance for lightweight imports
_default_recommender = None


def get_recommender(data_path=None):
    """Returns or creates the default HybridRecommender singleton."""
    global _default_recommender
    if _default_recommender is None:
        _default_recommender = HybridRecommender(data_path=data_path)
    return _default_recommender


def get_popular_recommendations(top_n=10, as_dict=False):
    """Convenience function for popular/trending items."""
    return get_recommender().get_popular(top_n=top_n, as_dict=as_dict)


def get_content_based_recommendations(item_name, top_n=10, as_dict=False):
    """Convenience function for content-based recommendations."""
    return get_recommender().get_content_based(item_name=item_name, top_n=top_n, as_dict=as_dict)


def get_collaborative_recommendations(target_user_id, top_n=10, as_dict=False):
    """Convenience function for collaborative filtering recommendations."""
    return get_recommender().get_collaborative(target_user_id=target_user_id, top_n=top_n, as_dict=as_dict)


def get_hybrid_recommendations(target_user_id=None, item_name=None, top_n=10, as_dict=False):
    """Convenience function for hybrid recommendations."""
    return get_recommender().get_hybrid(target_user_id=target_user_id, item_name=item_name, top_n=top_n, as_dict=as_dict)
