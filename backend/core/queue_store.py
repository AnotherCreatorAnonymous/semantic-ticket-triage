import threading
from typing import Callable, List, Set, Union
from api.schemas import TicketResponse

_tickets: List[TicketResponse] = []
_lock = threading.Lock()
_listeners: Set[Callable[[str, Union[TicketResponse, str]], None]] = set()

def register_listener(listener: Callable[[str, Union[TicketResponse, str]], None]) -> None:
    """
    Registra un callback para ser notificado de cambios en la cola.
    """
    with _lock:
        _listeners.add(listener)

def unregister_listener(listener: Callable[[str, Union[TicketResponse, str]], None]) -> None:
    """
    Elimina un callback previamente registrado.
    """
    with _lock:
        _listeners.discard(listener)

def _notify(action: str, item: Union[TicketResponse, str]) -> None:
    with _lock:
        listeners_snapshot = list(_listeners)
    for listener in listeners_snapshot:
        try:
            listener(action, item)
        except Exception:
            pass

def agregar(ticket: TicketResponse) -> None:
    """
    Agrega un ticket a la cola de tickets (thread-safe) y notifica a los listeners.
    """
    with _lock:
        _tickets.append(ticket)
    _notify("added", ticket)

def listar_ordenada() -> List[TicketResponse]:
    """
    Devuelve la lista de tickets ordenada por fecha de creación descendente (más recientes primero).
    """
    with _lock:
        return sorted(_tickets, key=lambda t: t.creado_en, reverse=True)


def limpiar() -> None:
    """
    Limpia la cola de tickets y notifica a los listeners.
    """
    with _lock:
        _tickets.clear()
    _notify("cleared", "all")

def eliminar(ticket_id: str) -> bool:
    """
    Elimina un ticket de la cola por ID. Retorna True si se encontró y eliminó.
    """
    found = False
    with _lock:
        for i, ticket in enumerate(_tickets):
            if ticket.id == ticket_id:
                _tickets.pop(i)
                found = True
                break
    if found:
        _notify("deleted", ticket_id)
    return found

