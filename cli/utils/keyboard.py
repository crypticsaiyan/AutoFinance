"""
Keyboard Navigation and Input Handler
"""
import sys
import tty
import termios
import select
from enum import Enum
from typing import Callable, Dict, Optional


class Key(Enum):
    """Key codes for navigation."""
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"
    ENTER = "enter"
    ESC = "esc"
    TAB = "tab"
    BACKSPACE = "backspace"
    DELETE = "delete"
    SPACE = "space"
    
    # Letter keys
    A = "a"
    B = "b"
    C = "c"
    D = "d"
    E = "e"
    F = "f"
    G = "g"
    H = "h"
    I = "i"
    J = "j"
    K = "k"
    L = "l"
    M = "m"
    N = "n"
    O = "o"
    P = "p"
    Q = "q"
    R = "r"
    S = "s"
    T = "t"
    U = "u"
    V = "v"
    W = "w"
    X = "x"
    Y = "y"
    Z = "z"
    
    # Function keys
    F1 = "f1"
    F2 = "f2"
    F3 = "f3"
    F4 = "f4"
    F5 = "f5"


class KeyboardHandler:
    """Handle keyboard input in raw mode."""
    
    def __init__(self):
        self.key_bindings: Dict[str, Callable] = {}
        self.running = False
        self.fd = sys.stdin.fileno()
        self.old_settings = None
    
    def bind(self, key: str, callback: Callable):
        """Bind a key to a callback function."""
        self.key_bindings[key.lower()] = callback
    
    def unbind(self, key: str):
        """Unbind a key."""
        self.key_bindings.pop(key.lower(), None)
    
    def _get_key(self) -> Optional[str]:
        """Get a single keypress."""
        if select.select([sys.stdin], [], [], 0)[0]:
            ch = sys.stdin.read(1)
            
            # Handle escape sequences
            if ch == '\x1b':
                # Check for more characters
                if select.select([sys.stdin], [], [], 0.1)[0]:
                    ch2 = sys.stdin.read(1)
                    if ch2 == '[':
                        ch3 = sys.stdin.read(1)
                        # Arrow keys
                        if ch3 == 'A':
                            return 'up'
                        elif ch3 == 'B':
                            return 'down'
                        elif ch3 == 'C':
                            return 'right'
                        elif ch3 == 'D':
                            return 'left'
                        # Function keys
                        elif ch3.isdigit():
                            ch4 = sys.stdin.read(1)
                            if ch3 == '1' and ch4 == '~':
                                return 'f1'
                            elif ch3 == '2' and ch4 == '~':
                                return 'f2'
                            elif ch3 == '3' and ch4 == '~':
                                return 'f3'
                            elif ch3 == '4' and ch4 == '~':
                                return 'f4'
                            elif ch3 == '5' and ch4 == '~':
                                return 'f5'
                return 'esc'
            
            # Handle special characters
            elif ch == '\r' or ch == '\n':
                return 'enter'
            elif ch == '\t':
                return 'tab'
            elif ch == '\x7f':
                return 'backspace'
            elif ch == ' ':
                return 'space'
            elif ch == '\x03':  # Ctrl+C
                return 'ctrl_c'
            else:
                return ch.lower()
        
        return None
    
    def start(self):
        """Start keyboard handler in raw mode."""
        self.running = True
        self.old_settings = termios.tcgetattr(self.fd)
        try:
            tty.setraw(self.fd)
        except Exception as e:
            print(f"Error setting raw mode: {e}")
    
    def stop(self):
        """Stop keyboard handler and restore terminal."""
        self.running = False
        if self.old_settings:
            try:
                termios.tcsetattr(self.fd, termios.TCSADRAIN, self.old_settings)
            except Exception as e:
                print(f"Error restoring terminal: {e}")
    
    def process_input(self) -> bool:
        """Process one keyboard input. Returns False if should quit."""
        key = self._get_key()
        
        if key == 'ctrl_c':
            return False
        
        if key and key in self.key_bindings:
            try:
                result = self.key_bindings[key]()
                if result is False:
                    return False
            except Exception as e:
                print(f"Error in key handler: {e}")
        
        return True


class InputField:
    """Text input field with editing capabilities."""
    
    def __init__(self, prompt: str = "", max_length: int = 100):
        self.prompt = prompt
        self.max_length = max_length
        self.text = ""
        self.cursor_pos = 0
    
    def insert(self, char: str):
        """Insert a character at cursor position."""
        if len(self.text) < self.max_length:
            self.text = self.text[:self.cursor_pos] + char + self.text[self.cursor_pos:]
            self.cursor_pos += 1
    
    def backspace(self):
        """Delete character before cursor."""
        if self.cursor_pos > 0:
            self.text = self.text[:self.cursor_pos - 1] + self.text[self.cursor_pos:]
            self.cursor_pos -= 1
    
    def delete(self):
        """Delete character at cursor."""
        if self.cursor_pos < len(self.text):
            self.text = self.text[:self.cursor_pos] + self.text[self.cursor_pos + 1:]
    
    def move_left(self):
        """Move cursor left."""
        if self.cursor_pos > 0:
            self.cursor_pos -= 1
    
    def move_right(self):
        """Move cursor right."""
        if self.cursor_pos < len(self.text):
            self.cursor_pos += 1
    
    def clear(self):
        """Clear the input."""
        self.text = ""
        self.cursor_pos = 0
    
    def get_text(self) -> str:
        """Get the current text."""
        return self.text
    
    def get_display(self) -> str:
        """Get display string with cursor."""
        display = self.prompt + self.text
        # Add cursor indicator
        if self.cursor_pos < len(self.text):
            display = display[:len(self.prompt) + self.cursor_pos] + \
                     "█" + \
                     display[len(self.prompt) + self.cursor_pos + 1:]
        else:
            display += "█"
        return display


class Navigation:
    """Navigation state manager."""
    
    def __init__(self, items: list):
        self.items = items
        self.selected_index = 0
    
    def up(self):
        """Move selection up."""
        if self.selected_index > 0:
            self.selected_index -= 1
    
    def down(self):
        """Move selection down."""
        if self.selected_index < len(self.items) - 1:
            self.selected_index += 1
    
    def select(self):
        """Get the selected item."""
        if 0 <= self.selected_index < len(self.items):
            return self.items[self.selected_index]
        return None
    
    def get_selected_index(self) -> int:
        """Get the current selection index."""
        return self.selected_index
    
    def set_items(self, items: list):
        """Update the items list."""
        self.items = items
        # Ensure selected index is still valid
        if self.selected_index >= len(items):
            self.selected_index = max(0, len(items) - 1)


# Example usage
if __name__ == "__main__":
    handler = KeyboardHandler()
    
    # Bind keys
    handler.bind('q', lambda: print("Quit pressed") or False)
    handler.bind('up', lambda: print("Up arrow"))
    handler.bind('down', lambda: print("Down arrow"))
    handler.bind('enter', lambda: print("Enter pressed"))
    
    print("Press keys... (q to quit)")
    handler.start()
    
    try:
        while handler.process_input():
            pass
    finally:
        handler.stop()
