"""
Tests de precisión para la capa de triaje híbrida.
Valida que NO hay falsos positivos críticos y que SÍ detecta incidentes reales.

Objetivo: asegurar que:
1. Palabras genéricas ("pagar", "memoria", "dispositivo") NO generen prioridad crítica (5)
2. Incidentes reales ("ransomware", "cuenta hackeada") SÍ sean detectados como críticos
3. Ambas funciones (calcular_prioridad y ajustar_prediccion_ml) son consistentes
"""
from api.schemas import RolUsuario
from core.triage_rules import calcular_prioridad, detectar_incidentes, ajustar_prediccion_ml


class TestFalsosPositivos:
    """Asegurar que palabras genéricas NO generan prioridad crítica."""

    def test_pagar_licencia_no_es_critico(self):
        """'Pagar' en contexto legítimo no debe ser crítico."""
        prioridad, _ = calcular_prioridad(
            "Necesito pagar licencia de software",
            "La licencia del antivirus necesita renovación. Puedo pagar por tarjeta.",
            RolUsuario.EMPLEADO
        )
        assert prioridad < 5, f"Esperado < 5, obtuvo {prioridad} para 'pagar licencia'"

    def test_memoria_usb_defectuosa_no_es_critico(self):
        """'Memoria/USB' sin contexto de seguridad no debe ser crítico."""
        prioridad, _ = calcular_prioridad(
            "Mi memoria USB dejó de funcionar",
            "Tengo una memoria USB que ya no se detecta. Necesito recuperar archivos.",
            RolUsuario.EMPLEADO
        )
        assert prioridad < 5, f"Esperado < 5, obtuvo {prioridad} para 'memoria USB defectuosa'"

    def test_impresora_desconocida_no_es_critico(self):
        """'Impresora' sola no debe ser crítica."""
        prioridad, _ = calcular_prioridad(
            "La impresora no imprime",
            "Intento conectar la impresora pero no funciona.",
            RolUsuario.EMPLEADO
        )
        assert prioridad < 5, f"Esperado < 5, obtuvo {prioridad} para 'problema impresora'"

    def test_dispositivo_desconocido_generico_no_es_critico(self):
        """'Dispositivo' sin contexto específico no debe ser crítico."""
        prioridad, _ = calcular_prioridad(
            "Encontré un dispositivo en mi escritorio",
            "Hay algo raro en mi escritorio. No sé qué es.",
            RolUsuario.EMPLEADO
        )
        assert prioridad < 5, f"Esperado < 5, obtuvo {prioridad} para 'dispositivo genérico'"


class TestDeteccionReales:
    """Asegurar que incidentes REALES se detectan correctamente."""

    def test_ransomware_explicito_es_critico(self):
        """Ransomware mencionado explícitamente debe ser crítico (5)."""
        prioridad, _ = calcular_prioridad(
            "RANSOMWARE en mi equipo",
            "Se detectó ransomware. Los archivos están cifrados.",
            RolUsuario.EMPLEADO
        )
        assert prioridad == 5, f"Esperado 5, obtuvo {prioridad} para 'ransomware explícito'"

    def test_archivos_cifrados_ransom_es_critico(self):
        """Archivos cifrados + pedir pago debe ser crítico."""
        prioridad, _ = calcular_prioridad(
            "Archivos bloqueados",
            "Todos mis archivos ahora tienen extensión .lock. Hay una nota pidiéndome pagar bitcoin.",
            RolUsuario.EMPLEADO
        )
        assert prioridad == 5, f"Esperado 5, obtuvo {prioridad} para 'archivos cifrados + rescate'"

    def test_cuenta_hackeada_es_critico(self):
        """Cuenta comprometida debe ser crítico."""
        prioridad, _ = calcular_prioridad(
            "Mi cuenta fue hackeada",
            "Me hackearon la cuenta. Veo correos que yo no envié.",
            RolUsuario.EMPLEADO
        )
        assert prioridad == 5, f"Esperado 5, obtuvo {prioridad} para 'cuenta hackeada'"

    def test_fuga_datos_es_critico(self):
        """Filtración de datos debe ser crítico."""
        prioridad, _ = calcular_prioridad(
            "Datos de clientes filtrados",
            "La base de datos está públicamente accesible en internet sin contraseña.",
            RolUsuario.ADMIN_TI
        )
        assert prioridad == 5, f"Esperado 5, obtuvo {prioridad} para 'fuga datos'"

    def test_caida_masiva_es_alta(self):
        """Caída masiva de servicio debe ser alta (4+)."""
        prioridad, _ = calcular_prioridad(
            "Toda la empresa sin internet",
            "Nadie en la oficina puede conectarse. El sistema está caído.",
            RolUsuario.ADMIN_TI
        )
        assert prioridad >= 4, f"Esperado >= 4, obtuvo {prioridad} para 'caída masiva'"


class TestConsistencia:
    """Asegurar que calcular_prioridad() y ajustar_prediccion_ml() son coherentes."""

    def test_ransomware_mismo_resultado_ambas_funciones(self):
        """Ambas funciones deben devolver 5 para ransomware."""
        titulo = "RANSOMWARE detectado"
        texto = "Hay ransomware. Los archivos están cifrados."
        rol = RolUsuario.EMPLEADO

        prioridad_calc, _ = calcular_prioridad(titulo, texto, rol)
        prioridad_ajustada, _ = ajustar_prediccion_ml(3, titulo, texto, rol, {})

        assert prioridad_calc == 5, f"calcular_prioridad = {prioridad_calc}, esperado 5"
        assert prioridad_ajustada == 5, f"ajustar_prediccion_ml = {prioridad_ajustada}, esperado 5"

    def test_ticket_rutinario_respeta_rango(self):
        """Ambas funciones deben respetar rango de rol para tickets rutinarios."""
        titulo = "Mi monitor no enciende"
        texto = "El monitor está apagado y no responde."
        rol = RolUsuario.EMPLEADO

        prioridad_calc, _ = calcular_prioridad(titulo, texto, rol)
        prioridad_ajustada, _ = ajustar_prediccion_ml(1, titulo, texto, rol, {})

        # Rango para empleado: (1,2)
        assert 1 <= prioridad_calc <= 2, f"calcular_prioridad = {prioridad_calc}, esperado en (1,2)"
        assert 1 <= prioridad_ajustada <= 2, f"ajustar_prediccion_ml = {prioridad_ajustada}, esperado en (1,2)"


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
