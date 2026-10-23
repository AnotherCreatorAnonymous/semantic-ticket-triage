import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import numpy as np
from api.schemas import RolUsuario
from core.triage_rules import PESO_ROL

import os
# Buscar dataset relativo a este script o en la raíz esperada
DATASET_PATHS = [
    Path(__file__).parent.parent / "evaluation" / "sample_tickets.json",  # backend/../evaluation
    Path(__file__).parent.parent.parent / "evaluation" / "sample_tickets.json",  # ../evaluation
    Path("/evaluation") / "sample_tickets.json",  # Si está montado en /
]
DATASET_PATH = None
for path in DATASET_PATHS:
    if path.exists():
        DATASET_PATH = path
        break
if not DATASET_PATH:
    raise FileNotFoundError(f"Dataset no encontrado en: {DATASET_PATHS}")
MODEL_PATH = Path(__file__).parent.parent / "core" / "models" / "baseline.pkl"
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
    
    vectorizer = TfidfVectorizer(max_features=1000, ngram_range=(1, 2), lowercase=True, stop_words=None)
    tfidf_matrix = vectorizer.fit_transform(texts)
    
    role_weights = np.array([[PESO_ROL[RolUsuario(r)]] for r in roles])
    scaler = StandardScaler(with_mean=False)
    tfidf_scaled = scaler.fit_transform(tfidf_matrix)
    role_scaled = (role_weights - role_weights.mean()) / (role_weights.std() + 1e-8)
    
    X = np.hstack([tfidf_scaled.toarray(), role_scaled])
    y = np.array(priorities)
    return X, y, vectorizer, scaler, role_weights.mean(), role_weights.std()

def train_baseline():
    print("[1/4] Loading dataset...")
    tickets = load_dataset()
    print(f"      {len(tickets)} tickets loaded (shuffled)")
    
    print("[2/4] Preparing features...")
    X, y, vectorizer, scaler, role_mean, role_std = prepare_features(tickets)
    print(f"      Feature matrix: {X.shape}")
    unique, counts = np.unique(y, return_counts=True)
    print(f"      Priority dist: {dict(zip(unique, counts))}")
    
    print("[3/4] Stratified split (80/20)...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    print(f"      Train: {len(X_train)}, Test: {len(X_test)}")
    
    print("[4/4] Training LogisticRegression (max_iter=200)...")
    model = LogisticRegression(max_iter=200, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)
    
    train_acc = model.score(X_train, y_train)
    test_acc = model.score(X_test, y_test)
    
    print("\n=== METRICS ===")
    print(f"Train Accuracy: {train_acc:.1%}")
    print(f"Test Accuracy:  {test_acc:.1%}")
    print(f"Improvement vs Heuristic (24%): {(test_acc - 0.24):+.1%}")
    
    print(f"\nSaving to {MODEL_PATH.name}...")
    metadata = {
        "vectorizer": vectorizer,
        "scaler": scaler,
        "role_mean": float(role_mean),
        "role_std": float(role_std),
    }
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump({"model": model, "metadata": metadata}, f)
    print(f"Model size: {MODEL_PATH.stat().st_size / 1024:.1f} KB")
    print("\nSUCCESS: Model trained and saved")

if __name__ == "__main__":
    train_baseline()
