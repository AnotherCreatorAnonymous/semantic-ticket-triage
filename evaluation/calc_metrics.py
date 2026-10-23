import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from sklearn.metrics import precision_recall_fscore_support, confusion_matrix, accuracy_score
import numpy as np
from api.schemas import RolUsuario
from core.triage_rules import calcular_prioridad
from core.nlp_engine import predecir, is_loaded, load_model

DATASET_PATH = Path(__file__).parent / "sample_tickets.json"

def load_dataset():
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        tickets = json.load(f)
    import random
    random.seed(42)
    random.shuffle(tickets)
    return tickets

def evaluate_heuristic(tickets):
    print("\n=== HEURISTIC (S1) ===")
    y_true = [t["prioridad"] for t in tickets]
    y_pred = []
    
    for t in tickets:
        priority, _ = calcular_prioridad(t["titulo"], t["texto"], RolUsuario(t["rol_usuario"]))
        y_pred.append(priority)
    
    acc = accuracy_score(y_true, y_pred)
    precision, recall, f1, _ = precision_recall_fscore_support(y_true, y_pred, average="weighted", zero_division=0)
    
    print(f"Accuracy: {acc:.3f}")
    print(f"Precision (weighted): {precision:.3f}")
    print(f"Recall (weighted): {recall:.3f}")
    print(f"F1 (weighted): {f1:.3f}")
    
    cm = confusion_matrix(y_true, y_pred, labels=[1,2,3,4,5])
    print(f"Confusion Matrix:\n{cm}")
    
    return {"accuracy": acc, "precision": precision, "recall": recall, "f1": f1}

def evaluate_model(tickets):
    print("\n=== MODEL (S2 BASELINE) ===")
    if not is_loaded():
        print("Model not loaded. Trying to load...")
        try:
            load_model()
        except Exception as e:
            print(f"⚠️ Could not load model: {e}")
            print("Train model first: python training/train_baseline.py")
            return None
    
    y_true = [t["prioridad"] for t in tickets]
    y_pred = []
    
    for t in tickets:
        priority, _, _ = predecir(t["titulo"], t["texto"], RolUsuario(t["rol_usuario"]))
        y_pred.append(priority)
    
    acc = accuracy_score(y_true, y_pred)
    precision, recall, f1, _ = precision_recall_fscore_support(y_true, y_pred, average="weighted", zero_division=0)
    
    print(f"Accuracy: {acc:.3f}")
    print(f"Precision (weighted): {precision:.3f}")
    print(f"Recall (weighted): {recall:.3f}")
    print(f"F1 (weighted): {f1:.3f}")
    
    cm = confusion_matrix(y_true, y_pred, labels=[1,2,3,4,5])
    print(f"Confusion Matrix:\n{cm}")
    
    return {"accuracy": acc, "precision": precision, "recall": recall, "f1": f1}

if __name__ == "__main__":
    print("Loading dataset...")
    tickets = load_dataset()
    print(f"Loaded {len(tickets)} tickets")
    
    heuristic_metrics = evaluate_heuristic(tickets)
    model_metrics = evaluate_model(tickets)
    
    if model_metrics:
        print("\n=== COMPARISON ===")
        print(f"Heuristic F1: {heuristic_metrics['f1']:.3f}")
        print(f"Model F1:     {model_metrics['f1']:.3f}")
        print(f"Improvement:  {(model_metrics['f1'] - heuristic_metrics['f1']):.3f}")
