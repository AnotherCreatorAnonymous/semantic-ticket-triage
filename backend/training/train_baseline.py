import json
import joblib
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import numpy as np
from api.schemas import RolUsuario
from core.triage_rules import PESO_ROL

DATASET_PATH = Path(__file__).parent.parent / "evaluation" / "sample_tickets.json"
MODEL_PATH = Path(__file__).parent / "models" / "baseline.joblib"
MODEL_PATH.parent.mkdir(exist_ok=True)

def load_dataset():
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        tickets = json.load(f)
    import random
    random.seed(42)
    random.shuffle(tickets)
    return tickets

def prepare_features(tickets):
    texts = [f"{t['titulo']} {t['texto']}" for t in tickets]
    roles = [t["rol_usuario"] for t in tickets]
    priorities = [t["prioridad"] for t in tickets]
    
    vectorizer = TfidfVectorizer(max_features=1000, ngram_range=(1, 2), lowercase=True, stop_words="spanish")
    tfidf_matrix = vectorizer.fit_transform(texts)
    
    role_weights = np.array([[PESO_ROL[RolUsuario(r)]] for r in roles])
    scaler = StandardScaler(with_mean=False)
    tfidf_scaled = scaler.fit_transform(tfidf_matrix)
    role_scaled = (role_weights - role_weights.mean()) / (role_weights.std() + 1e-8)
    
    X = np.hstack([tfidf_scaled.toarray(), role_scaled])
    y = np.array(priorities)
    return X, y, vectorizer, scaler, role_weights.std()

def train_baseline():
    print("Loading dataset...")
    tickets = load_dataset()
    print(f"Loaded {len(tickets)} tickets (shuffled)")
    
    print("Preparing features...")
    X, y, vectorizer, scaler, role_std = prepare_features(tickets)
    print(f"Feature matrix shape: {X.shape}")
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    print(f"Train: {len(X_train)}, Test: {len(X_test)}")
    
    print("Training LogisticRegression...")
    model = LogisticRegression(max_iter=200, multi_class="multinomial", random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)
    
    print(f"Train accuracy: {model.score(X_train, y_train):.3f}")
    print(f"Test accuracy: {model.score(X_test, y_test):.3f}")
    
    print(f"Saving model to {MODEL_PATH}")
    metadata = {"vectorizer": vectorizer, "scaler": scaler, "role_std": float(role_std)}
    joblib.dump({"model": model, "metadata": metadata}, MODEL_PATH)
    print("✅ Model saved")

if __name__ == "__main__":
    train_baseline()
