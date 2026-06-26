# Module path_step_monitor.py
# Acts as a central logging and event hub for pathfinding step visualization.
import sys

_log_callbacks = []
_node_callbacks = []
_is_silenced = False

def set_silenced(silenced):
    """Mutes or unmutes all logging and node callbacks."""
    global _is_silenced
    _is_silenced = silenced

def is_silenced():
    """Returns True if callbacks are currently muted."""
    return _is_silenced

def register_log_callback(callback):
    """Registers a callback function to receive text log updates."""
    if callback not in _log_callbacks:
        _log_callbacks.append(callback)

def register_node_callback(callback):
    """Registers a callback function to receive cell visualization updates (e.g., node open, close)."""
    if callback not in _node_callbacks:
        _node_callbacks.append(callback)

def clear_callbacks():
    """Clears all registered callbacks."""
    global _log_callbacks, _node_callbacks
    _log_callbacks = []
    _node_callbacks = []
    global _is_silenced
    _is_silenced = False

def log_step(step_description):
    """
    Broadcasts a step description string to all registered log callbacks.
    Also prints to console for debugging.
    """
    if _is_silenced:
        return
    try:
        print(f"[PATHFINDER] {step_description}")
    except UnicodeEncodeError:
        # Fallback to safe printing if the terminal doesn't support UTF-8 (e.g. standard Windows cmd)
        try:
            safe_text = step_description.encode(sys.stdout.encoding, errors='replace').decode(sys.stdout.encoding)
            print(f"[PATHFINDER] {safe_text}")
        except Exception:
            print(f"[PATHFINDER] {step_description.encode('ascii', errors='replace').decode('ascii')}")

    for callback in _log_callbacks:
        try:
            callback(step_description)
        except Exception as e:
            try:
                print(f"Error in step monitor log callback: {e}")
            except Exception:
                pass


def log_node_state(x, y, state):
    """
    Broadcasts a cell's state update to all registered node callbacks.
    States can be 'open', 'closed', 'current', 'path', 'reset'.
    """
    if _is_silenced:
        return
    for callback in _node_callbacks:
        try:
            callback(x, y, state)
        except Exception as e:
            print(f"Error in step monitor node callback: {e}")
