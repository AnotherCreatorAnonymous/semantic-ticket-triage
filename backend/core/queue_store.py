from typing import List
from api.schemas import TicketResponse

_tickets: List[TicketResponse] = []

def agregar(ticket: TicketResponse) -> None:
    """
    Agrega un ticket a la cola de tickets.
    """
    _tickets.append(ticket)

def listar_ordenada() -> List[TicketResponse]:
    """
    Devuelve la lista de tickets ordenada por prioridad descendente (más crítico primero).
    """
    return sorted(_tickets, key=lambda t: t.prioridad, reverse=True)

def limpiar() -> None:
    """
    Limpia la cola de tickets.
    """
    _tickets.clear()