import ast
import ctypes
import json
import sys
import threading
import time
import tkinter as tk
from tkinter import messagebox, ttk
INPUT_KEYBOARD = 1
KEYEVENTF_KEYUP = 2
KEYEVENTF_SCANCODE = 8
SHIFT_SCANCODE = 42
ENTER_SCANCODE = 28
TAB_SCANCODE = 15
SHIFT_TAB_ACTION = '<SHIFT_TAB>'
KEY_HOLD_SECONDS = 0
ENTER_HOLD_SECONDS = 0
SCANCODE_BY_CHARACTER = {'a': (30, False), 'b': (48, False), 'c': (46, False), 'd': (32, False), 'e': (18, False), 'f': (33, False), 'g': (34, False), 'h': (35, False), 'i': (23, False), 'j': (36, False), 'k': (37, False), 'l': (38, False), 'm': (50, False), 'n': (49, False), 'o': (24, False), 'p': (25, False), 'q': (16, False), 'r': (19, False), 's': (31, False), 't': (20, False), 'u': (22, False), 'v': (47, False), 'w': (17, False), 'x': (45, False), 'y': (21, False), 'z': (44, False), '1': (2, False), '2': (3, False), '3': (4, False), '4': (5, False), '5': (6, False), '6': (7, False), '7': (8, False), '8': (9, False), '9': (10, False), '0': (11, False), ' ': (57, False), '-': (12, False), '=': (13, False), '[': (26, False), ']': (27, False), '\\': (43, False), ';': (39, False), "'": (40, False), ',': (51, False), '.': (52, False), '/': (53, False), '`': (41, False), '!': (2, True), '@': (3, True), '#': (4, True), '$': (5, True), '%': (6, True), '^': (7, True), '&': (8, True), '*': (9, True), '(': (10, True), ')': (11, True), '_': (12, True), '+': (13, True), '{': (26, True), '}': (27, True), '|': (43, True), ':': (39, True), '"': (40, True), '<': (51, True), '>': (52, True), '?': (53, True), '~': (41, True)}
ULONG_PTR = ctypes.c_ulonglong if ctypes.sizeof(ctypes.c_void_p) == 8 else ctypes.c_ulong

class MouseInput(ctypes.Structure):
    _fields_ = [('dx', ctypes.c_long), ('dy', ctypes.c_long), ('mouseData', ctypes.c_ulong), ('dwFlags', ctypes.c_ulong), ('time', ctypes.c_ulong), ('dwExtraInfo', ULONG_PTR)]

class KeyboardInput(ctypes.Structure):
    _fields_ = [('wVk', ctypes.c_ushort), ('wScan', ctypes.c_ushort), ('dwFlags', ctypes.c_ulong), ('time', ctypes.c_ulong), ('dwExtraInfo', ULONG_PTR)]

class HardwareInput(ctypes.Structure):
    _fields_ = [('uMsg', ctypes.c_ulong), ('wParamL', ctypes.c_short), ('wParamH', ctypes.c_ushort)]

class InputUnion(ctypes.Union):
    _fields_ = [('mi', MouseInput), ('ki', KeyboardInput), ('hi', HardwareInput)]

class Input(ctypes.Structure):
    _fields_ = [('type', ctypes.c_ulong), ('union', InputUnion)]

def build_typing_actions(text: str, target_supports_smart_tab: bool) -> list[str]:
    text = text.replace('\r\n', '\n').replace('\r', '\n').replace('\t', '    ')
    if not target_supports_smart_tab:
        return list(text)
    actions: list[str] = []
    lines = text.split('\n')
    previous_indent_level = 0
    previous_content = ''
    for line_index, line in enumerate(lines):
        if line_index > 0:
            actions.append('\n')
        leading_spaces = len(line) - len(line.lstrip(' '))
        desired_indent_level = leading_spaces // 4
        remaining_spaces = leading_spaces % 4
        content = line[leading_spaces:]
        if line_index == 0:
            actions.extend(' ' * leading_spaces)
        else:
            assumed_indent_level = previous_indent_level
            auto_indent = previous_content.rstrip().endswith(':')
            if auto_indent:
                assumed_indent_level += 1
            if desired_indent_level < assumed_indent_level:
                shift_tab_count = assumed_indent_level - desired_indent_level
                actions.extend([SHIFT_TAB_ACTION] * shift_tab_count)
            elif desired_indent_level > assumed_indent_level:
                spaces_to_add = (desired_indent_level - assumed_indent_level) * 4
                actions.extend(' ' * spaces_to_add)
            if remaining_spaces:
                actions.extend(' ' * remaining_spaces)
        actions.extend(content)
        previous_indent_level = desired_indent_level
        previous_content = content
    return actions

def normalize_python_indentation(content: str) -> str:
    lines = [line.expandtabs(4).rstrip() for line in content.splitlines()]
    indent_stack = [0]
    normalized_lines: list[str] = []
    for line in lines:
        stripped = line.lstrip(' ')
        if not stripped:
            normalized_lines.append('')
            continue
        leading_spaces = len(line) - len(stripped)
        if leading_spaces > indent_stack[-1]:
            indent_stack.append(leading_spaces)
        else:
            while len(indent_stack) > 1 and leading_spaces < indent_stack[-1]:
                indent_stack.pop()
            if leading_spaces != indent_stack[-1]:
                indent_stack.append(leading_spaces)
        normalized_lines.append(' ' * ((len(indent_stack) - 1) * 4) + stripped)
    return '\n'.join(normalized_lines).rstrip() + '\n'

def add_space_before_newlines(actions: list[str]) -> list[str]:
    adjusted_actions: list[str] = []
    line_has_non_space_text = False
    for action in actions:
        if action == '\n':
            if line_has_non_space_text:
                adjusted_actions.append(' ')
            adjusted_actions.append(action)
            line_has_non_space_text = False
            continue
        adjusted_actions.append(action)
        if action != ' ' and action != SHIFT_TAB_ACTION:
            line_has_non_space_text = True
    return adjusted_actions

def format_content(content: str, file_type: str) -> str:
    if file_type == 'json':
        parsed = json.loads(content)
        return json.dumps(parsed, indent=4) + '\n'
    if file_type == 'python':
        ast.parse(content)
        return normalize_python_indentation(content)
    raise ValueError(f'Unsupported file type: {file_type}')

def type_native_keystrokes(text: str, characters_per_second: int, stop_event: threading.Event, target_supports_smart_tab: bool, target_window: int) -> None:
    delay_seconds = 1 / characters_per_second
    if sys.platform != 'win32':
        raise RuntimeError('Native keystroke typing is currently supported on Windows only.')
    user32 = ctypes.WinDLL('user32', use_last_error=True)
    user32.SendInput.argtypes = (ctypes.c_uint, ctypes.POINTER(Input), ctypes.c_int)
    user32.SendInput.restype = ctypes.c_uint
    user32.GetForegroundWindow.restype = ctypes.c_void_p
    actions = add_space_before_newlines(build_typing_actions(text, target_supports_smart_tab))

    def scan_code_input(scan_code: int, key_up: bool=False) -> Input:
        flags = KEYEVENTF_SCANCODE | (KEYEVENTF_KEYUP if key_up else 0)
        return Input(INPUT_KEYBOARD, InputUnion(ki=KeyboardInput(0, scan_code, flags, 0, 0)))

    def send_inputs(inputs: ctypes.Array[Input]) -> None:
        sent = user32.SendInput(len(inputs), inputs, ctypes.sizeof(Input))
        if sent != len(inputs):
            error_code = ctypes.get_last_error()
            raise ctypes.WinError(error_code)

    def send_single_input(input_event: Input) -> None:
        inputs = (Input * 1)(input_event)
        send_inputs(inputs)

    def send_scan_code(scan_code: int, shifted: bool) -> None:
        hold_seconds = ENTER_HOLD_SECONDS if scan_code == ENTER_SCANCODE else KEY_HOLD_SECONDS
        if shifted:
            send_single_input(scan_code_input(SHIFT_SCANCODE))
            time.sleep(KEY_HOLD_SECONDS)
        send_single_input(scan_code_input(scan_code))
        time.sleep(hold_seconds)
        send_single_input(scan_code_input(scan_code, key_up=True))
        if shifted:
            time.sleep(KEY_HOLD_SECONDS)
            send_single_input(scan_code_input(SHIFT_SCANCODE, key_up=True))

    def send_shift_tab() -> None:
        send_single_input(scan_code_input(SHIFT_SCANCODE))
        time.sleep(KEY_HOLD_SECONDS)
        send_single_input(scan_code_input(TAB_SCANCODE))
        time.sleep(KEY_HOLD_SECONDS)
        send_single_input(scan_code_input(TAB_SCANCODE, key_up=True))
        time.sleep(KEY_HOLD_SECONDS)
        send_single_input(scan_code_input(SHIFT_SCANCODE, key_up=True))

    def send_character(character: str, index: int) -> None:
        if character == '\n':
            send_scan_code(ENTER_SCANCODE, False)
            return
        if character == SHIFT_TAB_ACTION:
            send_shift_tab()
            return
        if character == '\t':
            raise ValueError('Tabs must be converted to spaces before typing.')
        if not character.isascii():
            raise ValueError(f'Unsupported non-ASCII character at index {index}: {character!r}')
        lookup_character = character.lower() if character.isalpha() else character
        if lookup_character not in SCANCODE_BY_CHARACTER:
            raise ValueError(f'Unsupported ASCII character at index {index}: {character!r}')
        scan_code, shifted = SCANCODE_BY_CHARACTER[lookup_character]
        send_scan_code(scan_code, shifted or character.isupper())
    for index, character in enumerate(actions):
        if stop_event.is_set():
            return
        current_window = user32.GetForegroundWindow()
        if current_window != target_window:
            stop_event.set()
            return
        send_character(character, index)
        if stop_event.wait(delay_seconds):
            return

class EditorTab:

    def __init__(self, root: tk.Tk, parent: ttk.Notebook, tab_number: int) -> None:
        self.root = root
        self.tab_number = tab_number
        self.frame = tk.Frame(parent)
        self.line_numbers = tk.Text(self.frame, width=4, padx=4, takefocus=0, border=0, background='#f0f0f0', foreground='#666666', state='disabled', wrap='none')
        self.line_numbers.pack(side='left', fill='y')
        self.scrollbar = tk.Scrollbar(self.frame)
        self.scrollbar.pack(side='right', fill='y')
        self.text = tk.Text(self.frame, wrap='word', undo=True)
        self.text.pack(side='left', fill='both', expand=True)
        self.text.config(yscrollcommand=self.sync_scrollbar)
        self.scrollbar.config(command=self.scroll_both)
        self.text.bind('<Tab>', self.insert_spaces_for_tab)
        self.text.bind('<KeyRelease>', self.schedule_line_number_update)
        self.text.bind('<ButtonRelease-1>', self.schedule_line_number_update)
        self.text.bind('<Configure>', self.schedule_line_number_update)
        self.update_line_numbers()

    def update_line_numbers(self) -> None:
        line_count = int(self.text.index('end-1c').split('.')[0])
        numbers = '\n'.join((str(i) for i in range(1, line_count + 1)))
        self.line_numbers.config(state='normal')
        self.line_numbers.delete('1.0', 'end')
        self.line_numbers.insert('1.0', numbers)
        self.line_numbers.config(state='disabled')

    def schedule_line_number_update(self, _event: tk.Event | None=None) -> None:
        self.root.after_idle(self.update_line_numbers)

    def sync_scrollbar(self, first: float, last: float) -> None:
        self.scrollbar.set(first, last)
        self.line_numbers.yview_moveto(first)

    def scroll_both(self, *args: object) -> None:
        self.text.yview(*args)
        self.line_numbers.yview(*args)

    def insert_spaces_for_tab(self, _event: tk.Event) -> str:
        self.text.insert('insert', '    ')
        self.schedule_line_number_update()
        return 'break'

class App:

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title('type-4-me')
        self.root.geometry('640x360')
        toolbar = tk.Frame(self.root)
        toolbar.pack(fill='x', padx=12, pady=(12, 0))
        self.start_typing_button = tk.Button(toolbar, text='Start Typing', command=self.schedule_typing)
        self.start_typing_button.pack(side='left')
        self.stop_typing_button = tk.Button(toolbar, text='Stop', command=self.stop_typing, state='disabled')
        self.stop_typing_button.pack(side='left', padx=(6, 0))
        self.file_type = tk.StringVar(value='python')
        self.file_type_dropdown = ttk.Combobox(toolbar, textvariable=self.file_type, values=('python', 'json'), state='readonly', width=8)
        self.file_type_dropdown.pack(side='left', padx=(12, 0))
        self.format_button = tk.Button(toolbar, text='Format', command=self.format_active_tab)
        self.format_button.pack(side='left', padx=(6, 0))
        self.typing_after_id: str | None = None
        self.typing_stop_event = threading.Event()
        self.typing_thread: threading.Thread | None = None
        self.target_supports_smart_tab = tk.BooleanVar(value=False)
        self.smart_tab_checkbox = tk.Checkbutton(toolbar, text='target supports smart-tab', variable=self.target_supports_smart_tab)
        self.smart_tab_checkbox.pack(side='left', padx=(12, 0))
        self.characters_per_second = tk.IntVar(value=250)
        tk.Label(toolbar, text='CPS').pack(side='left', padx=(12, 4))
        self.cps_slider = tk.Scale(toolbar, from_=1, to=350, orient='horizontal', variable=self.characters_per_second, command=self.update_cps_label, showvalue=False, length=120)
        self.cps_slider.pack(side='left')
        self.cps_value_label = tk.Label(toolbar, text=str(self.characters_per_second.get()))
        self.cps_value_label.pack(side='left', padx=(4, 0))
        self.typing_status = tk.Label(toolbar, text='')
        self.typing_status.pack(side='left', padx=(8, 0))
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=12, pady=12)
        self.notebook.bind('<<NotebookTabChanged>>', self.focus_active_tab)
        self.tabs: list[EditorTab] = []
        self.add_tab()
        self.root.bind('<Control-n>', self.add_tab)
        self.root.bind('<Control-w>', self.close_active_tab)
        self.root.bind('<Control-Tab>', self.select_next_tab)
        self.root.bind('<Control-Shift-Tab>', self.select_previous_tab)

    def next_available_tab_number(self) -> int:
        used_numbers = {tab.tab_number for tab in self.tabs}
        tab_number = 1
        while tab_number in used_numbers:
            tab_number += 1
        return tab_number

    def add_tab(self, _event: tk.Event | None=None) -> str:
        tab_number = self.next_available_tab_number()
        tab = EditorTab(self.root, self.notebook, tab_number)
        self.tabs.append(tab)
        self.notebook.add(tab.frame, text=f'Tab {tab_number}')
        self.notebook.select(tab.frame)
        tab.text.focus_set()
        return 'break'

    def close_active_tab(self, _event: tk.Event | None=None) -> str:
        if not self.tabs:
            return 'break'
        current_frame = self.notebook.nametowidget(self.notebook.select())
        for index, tab in enumerate(self.tabs):
            if tab.frame == current_frame:
                self.notebook.forget(tab.frame)
                tab.frame.destroy()
                del self.tabs[index]
                break
        if self.tabs:
            self.focus_active_tab()
        else:
            self.add_tab()
        return 'break'

    def active_tab(self) -> EditorTab:
        current_frame = self.notebook.nametowidget(self.notebook.select())
        for tab in self.tabs:
            if tab.frame == current_frame:
                return tab
        raise RuntimeError('No active tab')

    def focus_active_tab(self, _event: tk.Event | None=None) -> None:
        if not self.tabs or not self.notebook.select():
            return
        tab = self.active_tab()
        tab.update_line_numbers()
        tab.text.focus_set()

    def update_cps_label(self, _value: str) -> None:
        self.cps_value_label.config(text=str(self.characters_per_second.get()))

    def format_active_tab(self) -> None:
        tab = self.active_tab()
        content = tab.text.get('1.0', 'end-1c')
        file_type = self.file_type.get()
        try:
            formatted = format_content(content, file_type)
        except Exception as error:
            messagebox.showerror('Format failed', str(error))
            return
        tab.text.delete('1.0', 'end')
        tab.text.insert('1.0', formatted)
        tab.update_line_numbers()
        tab.text.focus_set()

    def schedule_typing(self) -> None:
        tab = self.active_tab()
        content = tab.text.get('1.0', 'end-1c')
        characters_per_second = self.characters_per_second.get()
        target_supports_smart_tab = self.target_supports_smart_tab.get()
        self.typing_stop_event.clear()
        self.start_typing_button.config(state='disabled')
        self.stop_typing_button.config(state='normal')
        self.cps_slider.config(state='disabled')
        self.smart_tab_checkbox.config(state='disabled')
        self.typing_status.config(text='Typing starts in 3 seconds...')
        self.typing_after_id = self.root.after(3000, lambda: self.start_typing(content, characters_per_second, target_supports_smart_tab))

    def start_typing(self, content: str, characters_per_second: int, target_supports_smart_tab: bool) -> None:
        self.typing_after_id = None
        if self.typing_stop_event.is_set():
            self.finish_typing('Stopped')
            return
        target_window = self.foreground_window()
        self.typing_status.config(text='Typing...')
        self.typing_thread = threading.Thread(target=self.typing_worker, args=(content, characters_per_second, target_supports_smart_tab, target_window, self.typing_stop_event), daemon=True)
        self.typing_thread.start()

    def foreground_window(self) -> int:
        if sys.platform != 'win32':
            return 0
        user32 = ctypes.WinDLL('user32', use_last_error=True)
        user32.GetForegroundWindow.restype = ctypes.c_void_p
        return user32.GetForegroundWindow()

    def typing_worker(self, content: str, characters_per_second: int, target_supports_smart_tab: bool, target_window: int, stop_event: threading.Event) -> None:
        try:
            type_native_keystrokes(content, characters_per_second, stop_event, target_supports_smart_tab, target_window)
        except Exception as error:
            self.root.after(0, lambda error=error: self.typing_failed(error))
            return
        status = 'Stopped' if stop_event.is_set() else 'Done'
        self.root.after(0, lambda: self.finish_typing(status))

    def typing_failed(self, error: Exception) -> None:
        messagebox.showerror('Typing failed', str(error))
        self.finish_typing('')

    def stop_typing(self) -> None:
        self.typing_stop_event.set()
        if self.typing_after_id is not None:
            self.root.after_cancel(self.typing_after_id)
            self.typing_after_id = None
            self.finish_typing('Stopped')
        else:
            self.typing_status.config(text='Stopping...')

    def finish_typing(self, status: str) -> None:
        self.start_typing_button.config(state='normal')
        self.stop_typing_button.config(state='disabled')
        self.cps_slider.config(state='normal')
        self.smart_tab_checkbox.config(state='normal')
        self.typing_status.config(text=status)
        if status:
            self.root.after(1500, lambda: self.typing_status.config(text=''))

    def select_next_tab(self, _event: tk.Event) -> str:
        if not self.tabs:
            return 'break'
        current = self.notebook.index('current')
        self.notebook.select((current + 1) % len(self.tabs))
        self.focus_active_tab()
        return 'break'

    def select_previous_tab(self, _event: tk.Event) -> str:
        if not self.tabs:
            return 'break'
        current = self.notebook.index('current')
        self.notebook.select((current - 1) % len(self.tabs))
        self.focus_active_tab()
        return 'break'

    def run(self) -> None:
        self.root.mainloop()

def main() -> None:
    """Open a minimal tabbed text-entry UI."""
    App().run()
if __name__ == '__main__':
    main()
