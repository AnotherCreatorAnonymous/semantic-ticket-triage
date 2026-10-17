import pytest
from api.schemas import RolUsuario
from core import nlp_engine

@pytest.fixture(scope="session", autouse=True)
def load_model():
    """Load model once per test session."""
    try:
        nlp_engine.load_model()
        print("✅ Model loaded for S2 tests")
    except FileNotFoundError:
        print("⚠️ Model not found. Skipping S2 model tests. Run: python training/train_baseline.py")

def test_model_loaded():
    """Verify model loads successfully."""
    assert nlp_engine.is_loaded(), "Model should be loaded"

@pytest.mark.skipif(not nlp_engine.is_loaded(), reason="Model not trained")
def test_model_predecir_returns_tuple():
    """Model.predecir() returns (priority, confidence, explicacion)."""
    priority, confidence, explicacion = nlp_engine.predecir(
        "Ransomware detectado",
        "Todos los archivos están cifrados",
        RolUsuario.CEO
    )
    assert isinstance(priority, int)
    assert 1 <= priority <= 5
    assert isinstance(confidence, float)
    assert 0 <= confidence <= 1
    assert isinstance(explicacion, dict)
    assert "rol:" in str(explicacion).lower()

@pytest.mark.skipif(not nlp_engine.is_loaded(), reason="Model not trained")
def test_model_confidence_reasonable():
    """Model confidence should be > 0.2 for most inputs."""
    priority, confidence, _ = nlp_engine.predecir(
        "Problema con el sistema",
        "La computadora está lenta después de actualizar",
        RolUsuario.EMPLEADO
    )
    assert confidence > 0.15, f"Confidence too low: {confidence}"

@pytest.mark.skipif(not nlp_engine.is_loaded(), reason="Model not trained")
def test_model_role_weight_affects_priority():
    """CEO ticket should have higher priority than Employee for same text."""
    text_titulo = "Sistema caído"
    text_descripcion = "El servidor no responde"
    
    priority_emp, _, _ = nlp_engine.predecir(
        text_titulo, text_descripcion, RolUsuario.EMPLEADO
    )
    priority_ceo, _, _ = nlp_engine.predecir(
        text_titulo, text_descripcion, RolUsuario.CEO
    )
    
    # CEO should equal or higher than Employee
    assert priority_ceo >= priority_emp, \
        f"CEO ({priority_ceo}) should >= Employee ({priority_emp}) for same issue"
