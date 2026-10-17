import threading
from typing import List
from api.schemas import TicketResponse

_tickets: List[TicketResponse] = []
_lock = threading.Lock()

def agregar(ticket: TicketResponse) -> None:
    """
    Agrega un ticket a la cola de tickets (thread-safe).
    """
    with _lock:
        _tickets.append(ticket)

def listar_ordenada() -> List[TicketResponse]:
    """
    Devuelve la lista de tickets ordenada por prioridad descendente (más crítico primero).
    """
    with _lock:
        return sorted(_tickets, key=lambda t: t.prioridad, reverse=True)

def limpiar() -> None:
    """
    Limpia la cola de tickets.
    """
    with _lock:
        _tickets.clear()

def eliminar(ticket_id: str) -> bool:
    """
    Elimina un ticket de la cola por ID. Retorna True si se encontró y eliminó.
    """
    with _lock:
        for i, ticket in enumerate(_tickets):
            if ticket.id == ticket_id:
                _tickets.pop(i)
                return True
        return False
