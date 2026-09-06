"""
Model package providing hybrid e-commerce recommendation services.
"""

from model.data_loader import load_and_preprocess_data
from model.recommender import (
    HybridRecommender,
    get_recommender,
    get_popular_recommendations,
    get_content_based_recommendations,
    get_collaborative_recommendations,
    get_hybrid_recommendations
)

__all__ = [
    "load_and_preprocess_data",
    "HybridRecommender",
    "get_recommender",
    "get_popular_recommendations",
    "get_content_based_recommendations",
    "get_collaborative_recommendations",
    "get_hybrid_recommendations"
]
