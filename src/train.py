# ================================================================
#  train.py
#  Handles: train/test split, scaling, training 3 models,
#           cross validation, saving models to disk
#  Usage  : from train import run_training
# ================================================================

import pandas as pd
import numpy as np
import pickle
import joblib
import warnings
warnings.filterwarnings("ignore")

from sklearn.model_selection import TimeSeriesSplit, cross_val_score
from sklearn.preprocessing  import StandardScaler
from sklearn.linear_model   import LogisticRegression
from sklearn.ensemble       import RandomForestClassifier
import xgboost as xgb


def split_data(df_feat: pd.DataFrame, feature_cols: list):
    """
    Chronological 80/20 split — preserves time order.
    This is better than random split for time-series parking data
    because it simulates real deployment (predict future from past).
    """
    df_model = df_feat.sort_values("Timestamp")

    split_index = int(len(df_model) * 0.8)

    train_df = df_model.iloc[:split_index]
    test_df  = df_model.iloc[split_index:]

    X_train = train_df[feature_cols]
    y_train = train_df["occupied"]
    X_test  = test_df[feature_cols]
    y_test  = test_df["occupied"]

    print("Chronological split complete!")
    print(f"   Training rows : {len(train_df)}")
    print(f"   Testing rows  : {len(test_df)}")
    print(f"   Train occupancy : {y_train.mean()*100:.1f}%")
    print(f"   Test  occupancy : {y_test.mean()*100:.1f}%")

    return X_train, X_test, y_train, y_test


def scale_features(X_train, X_test):
    """
    StandardScaler fitted on training data only.
    Applying scaler to test data AFTER fitting on train
    prevents data leakage.
    """
    scaler         = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled  = scaler.transform(X_test)

    print("Features scaled!")
    print("   Scaler fitted on training data only")
    return scaler, X_train_scaled, X_test_scaled


def train_models(X_train, y_train, X_train_scaled):
    """
    Train all 3 models.
    - Logistic Regression uses scaled features
    - Random Forest and XGBoost use raw features (tree models)
    """
    # Model 1 — Logistic Regression
    print("\nTraining Model 1 — Logistic Regression...")
    lr_model = LogisticRegression(max_iter=1000, random_state=42)
    lr_model.fit(X_train_scaled, y_train)
    print("   Done!")

    # Model 2 — Random Forest
    print("Training Model 2 — Random Forest...")
    rf_model = RandomForestClassifier(
        n_estimators=100, max_depth=10,
        min_samples_split=5, random_state=42, n_jobs=-1
    )
    rf_model.fit(X_train, y_train)
    print("   Done!")

    # Model 3 — XGBoost
    print("Training Model 3 — XGBoost...")
    xgb_model = xgb.XGBClassifier(
        n_estimators=200, max_depth=6,
        learning_rate=0.05, subsample=0.8,
        colsample_bytree=0.8, random_state=42,
        eval_metric="logloss", verbosity=0
    )
    xgb_model.fit(X_train, y_train)
    print("   Done!")

    print("\nAll 3 models trained!")
    return lr_model, rf_model, xgb_model


def cross_validate(xgb_model, X_train, y_train):
    """
    Time-series cross validation on XGBoost.
    TimeSeriesSplit respects temporal order — no future leakage.
    Returns mean F1 score and std.
    """
    tscv = TimeSeriesSplit(n_splits=5)

    scores = cross_val_score(
        xgb_model, X_train, y_train,
        cv=tscv, scoring="f1"
    )

    print("\nTime Series Cross Validation (XGBoost)")
    print("=" * 40)
    for i, score in enumerate(scores, 1):
        print(f"   Fold {i}: {score:.4f}")
    print(f"\n   Mean F1 : {scores.mean():.4f}")
    print(f"   Std Dev  : {scores.std():.4f}")

    return scores


def save_models(lr_model, rf_model, xgb_model,
                scaler, feature_cols, model_dir: str):
    """Save all models, scaler, and feature column names to disk."""

    # Save models with pickle
    models_to_save = {
        "logistic_regression" : lr_model,
        "random_forest"       : rf_model,
        "xgboost"             : xgb_model,
    }
    for name, model in models_to_save.items():
        path = f"{model_dir}{name}.pkl"
        with open(path, "wb") as f:
            pickle.dump(model, f)
        print(f"Saved: {path}")

    # Save scaler
    with open(f"{model_dir}scaler.pkl", "wb") as f:
        pickle.dump(scaler, f)
    print(f"Saved: {model_dir}scaler.pkl")

    # Save feature cols
    with open(f"{model_dir}feature_cols.pkl", "wb") as f:
        pickle.dump(feature_cols, f)
    print(f"Saved: {model_dir}feature_cols.pkl")

    # Save best model with joblib (used by Streamlit app)
    best_model = xgb_model
    joblib.dump(best_model, f"{model_dir}best_model.pkl")
    print(f"Saved: {model_dir}best_model.pkl")

    joblib.dump(feature_cols, f"{model_dir}feature_cols.pkl")
    print(f"\nAll models saved to {model_dir}")


def run_training(df_feat: pd.DataFrame, feature_cols: list,
                 model_dir: str):
    """
    Full training pipeline:
    split → scale → train → cross validate → save
    Returns all trained models and split data.
    """
    print("\n" + "=" * 50)
    print("  MODEL TRAINING")
    print("=" * 50)

    X_train, X_test, y_train, y_test = split_data(df_feat, feature_cols)
    scaler, X_train_scaled, X_test_scaled = scale_features(X_train, X_test)
    lr_model, rf_model, xgb_model = train_models(
        X_train, y_train, X_train_scaled
    )
    cross_validate(xgb_model, X_train, y_train)
    save_models(lr_model, rf_model, xgb_model,
                scaler, feature_cols, model_dir)

    return (lr_model, rf_model, xgb_model, scaler,
            X_train, X_test, X_train_scaled, X_test_scaled,
            y_train, y_test)
