import pandas as pd
import joblib

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

print("=" * 50)
print("SMART COMMUNITY AI - MODEL TRAINING")
print("=" * 50)

try:

    # Load Dataset
    print("\nLoading dataset...")

    df = pd.read_csv("complaints.csv")

    print("Dataset Loaded Successfully")
    print(f"Rows: {df.shape[0]}")
    print(f"Columns: {df.shape[1]}")

    print("\nColumns Found:")
    print(df.columns.tolist())

    # Check Required Columns
    required_columns = ["complaint", "category"]

    for col in required_columns:
        if col not in df.columns:
            raise ValueError(
                f"Missing required column: {col}"
            )

    # Remove Empty Values
    df = df.dropna(
        subset=["complaint", "category"]
    )

    print("\nSample Records:")
    print(df.head())

    print("\nCategory Distribution:")
    print(df["category"].value_counts())

    # Features and Labels
    X = df["complaint"]
    y = df["category"]

    print("\nCreating TF-IDF Features...")

    vectorizer = TfidfVectorizer(
        stop_words="english",
        max_features=1000
    )

    X_vectorized = vectorizer.fit_transform(X)

    print(
        f"Feature Matrix Shape: {X_vectorized.shape}"
    )

    print("\nTraining Model...")

    model = LogisticRegression(
        max_iter=2000,
        random_state=42
    )

    model.fit(
        X_vectorized,
        y
    )

    print("Model Training Complete")

    # Save Artifacts
    joblib.dump(
        model,
        "model.pkl"
    )

    joblib.dump(
        vectorizer,
        "vectorizer.pkl"
    )

    print("\nSaving Files...")
    print("model.pkl saved")
    print("vectorizer.pkl saved")

    print("\nAvailable Categories:")

    for category in sorted(df["category"].unique()):
        print(f"- {category}")

    print("\nSUCCESS!")
    print("=" * 50)

except Exception as e:

    print("\nERROR OCCURRED")
    print(str(e))