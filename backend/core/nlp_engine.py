import pickle
from pathlib import Path
from typing import Dict, Tuple
from api.schemas import RolUsuario
from core.triage_rules import PESO_ROL, ETIQUETAS
import numpy as np

# Ruta robusta: busca modelo en múltiples ubicaciones
_MODEL_CANDIDATES = [
    Path(__file__).parent / "models" / "baseline.pkl",  # Ubicación esperada
    Path(__file__).parent.parent.parent / "backend" / "core" / "models" / "baseline.pkl",  # Fallback
]
MODEL_PATH = next((p for p in _MODEL_CANDIDATES if p.exists()), _MODEL_CANDIDATES[0])

class NLPEngine:
    def __init__(self):
        self.model = None
        self.metadata = None
        self.loaded = False
    
    def load(self):
        if not MODEL_PATH.exists():
            raise FileNotFoundError(f"Model not found at {MODEL_PATH}")
        
        with open(MODEL_PATH, 'rb') as f:
            artifact = pickle.load(f)
        self.model = artifact["model"]
        self.metadata = artifact["metadata"]
        self.loaded = True
    
    def predecir(self, titulo: str, texto: str, rol: RolUsuario) -> Tuple[int, float, Dict[str, float]]:
        """
        Predict priority using trained model.
        Returns: (priority: int, confidence: float, explicacion_xai: Dict[str, float])
        """
        if not self.loaded:
            raise RuntimeError("Model not loaded")
        
        # Combine title + text
        text_input = f"{titulo} {texto}"
        
        # Vectorize with same TF-IDF
        tfidf = self.metadata["vectorizer"].transform([text_input])
        tfidf_scaled = self.metadata["scaler"].transform(tfidf)
        
        # Add role weight feature (mismo escalado que en el entrenamiento).
        # Antes se restaba role_weight a sí mismo, así que la feature siempre valía 0
        # y el modelo ignoraba el rol por completo.
        role_weight = PESO_ROL[rol]
        role_mean = self.metadata.get("role_mean", 3.0)
        role_scaled = (role_weight - role_mean) / (self.metadata["role_std"] + 1e-8)
        
        X = np.hstack([tfidf_scaled.toarray(), [[role_scaled]]])
        
        # Predict
        priority_pred = self.model.predict(X)[0]
        confidence = self.model.predict_proba(X)[0].max()
        
        # Explicación: role weight + top TF-IDF features
        explicacion = {f"rol: {rol.value}": float(PESO_ROL[rol])}
        
        # Get top features from TF-IDF
        feature_names = self.metadata["vectorizer"].get_feature_names_out()
        top_indices = tfidf[0].toarray()[0].argsort()[-3:][::-1]
        for idx in top_indices:
            if tfidf[0,idx] > 0:
                explicacion[feature_names[idx]] = float(tfidf[0,idx])
        
        return int(priority_pred), float(confidence), explicacion

# Singleton instance
_engine = NLPEngine()

def load_model():
    _engine.load()

def predecir(titulo: str, texto: str, rol: RolUsuario) -> Tuple[int, float, Dict[str, float]]:
    return _engine.predecir(titulo, texto, rol)

def is_loaded() -> bool:
    return _engine.loaded
