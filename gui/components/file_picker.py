"""
gui/components/file_picker.py — CSV/Excel file picker widget for OnTrack desktop GUI.

A self-contained CTkFrame that handles file selection, validation, and
feedback. Calls on_file(path: str) when a valid file is chosen.

Usage (HomeView):
    self.picker = FilePicker(
        parent,
        on_file=self._on_file_selected,
        on_clear=self._on_file_cleared,
    )
    self.picker.pack(fill="x", padx=12, pady=(0, 8))
"""

import os
import tkinter as tk
from tkinter import filedialog
from typing import Callable, Optional

import customtkinter as ctk

_BLUE = '#0057A8'
_NAVY = '#002855'
_ORANGE = '#F26522'
_WHITE = '#FFFFFF'
_GRAY = '#6B7280'
_SURFACE = '#1A2535'
_CARD = '#243044'
_RED = '#EF4444'
_GREEN = '#22C55E'
_HDR = '#9DB8D6'

_VALID_EXTENSIONS = {'.csv', '.xlsx', '.xls'}


class FilePicker(ctk.CTkFrame):
    """
    File picker widget for CSV/Excel address files.

    Parameters
    ----------
    parent : tk widget
        Parent container.
    on_file : callable(path: str) | None
        Called with the absolute path when a valid file is selected.
    on_clear : callable() | None
        Called when the user clears the current selection.
    label : str
        Button label text.
    """

    def __init__(
        self,
        parent,
        on_file: Optional[Callable[[str], None]] = None,
        on_clear: Optional[Callable[[], None]] = None,
        label: str = '📂  Choose File',
        **kwargs,
    ):
        super().__init__(parent, fg_color=_SURFACE, corner_radius=8, **kwargs)
        self._on_file = on_file
        self._on_clear = on_clear
        self._label = label
        self._path: Optional[str] = None

        self._build()

    # ── Layout ─────────────────────────────────────────────────────────────

    def _build(self) -> None:
        self.grid_columnconfigure(0, weight=0)  # button
        self.grid_columnconfigure(1, weight=1)  # filename label
        self.grid_columnconfigure(2, weight=0)  # clear button

        # ── Pick button ──
        self._pick_btn = ctk.CTkButton(
            self,
            text=self._label,
            width=140,
            height=36,
            fg_color=_BLUE,
            hover_color=_NAVY,
            text_color=_WHITE,
            corner_radius=6,
            font=ctk.CTkFont(size=13),
            command=self._open_dialog,
        )
        self._pick_btn.grid(row=0, column=0, padx=(8, 6), pady=8, sticky='w')

        # ── Filename display ──
        self._file_var = tk.StringVar(value='No file selected')
        self._file_lbl = ctk.CTkLabel(
            self,
            textvariable=self._file_var,
            font=ctk.CTkFont(size=12),
            text_color=_GRAY,
            anchor='w',
        )
        self._file_lbl.grid(row=0, column=1, padx=(0, 6), pady=8, sticky='ew')

        # ── Clear button (hidden until a file is selected) ──
        self._clear_btn = ctk.CTkButton(
            self,
            text='✕',
            width=30,
            height=30,
            fg_color='#3B1A1A',
            hover_color=_RED,
            text_color=_WHITE,
            corner_radius=6,
            font=ctk.CTkFont(size=11),
            command=self._clear,
        )
        # Not gridded until a file is loaded

        # ── Validation error label ──
        self._error_var = tk.StringVar(value='')
        self._error_lbl = ctk.CTkLabel(
            self,
            textvariable=self._error_var,
            font=ctk.CTkFont(size=11),
            text_color=_RED,
            anchor='w',
        )
        self._error_lbl.grid(
            row=1, column=0, columnspan=3, padx=10, pady=(0, 6), sticky='w'
        )

    # ── Public API ─────────────────────────────────────────────────────────

    @property
    def path(self) -> Optional[str]:
        """Absolute path of the currently selected file, or None."""
        return self._path

    def set_file(self, path: str) -> None:
        """Programmatically set a file path (validates and fires on_file)."""
        self._apply(path)

    def clear(self) -> None:
        """Programmatically clear the selection without firing on_clear."""
        self._reset_ui()
        self._path = None

    # ── Interaction ────────────────────────────────────────────────────────

    def _open_dialog(self) -> None:
        path = filedialog.askopenfilename(
            title='Select address file',
            filetypes=[
                ('Supported files', '*.csv *.xlsx *.xls'),
                ('CSV files', '*.csv'),
                ('Excel files', '*.xlsx *.xls'),
                ('All files', '*.*'),
            ],
        )
        if not path:
            return
        self._apply(path)

    def _apply(self, path: str) -> None:
        """Validate *path* and update UI; fire on_file if valid."""
        error = self._validate(path)
        if error:
            self._error_var.set(error)
            self._file_var.set(os.path.basename(path))
            self._file_lbl.configure(text_color=_RED)
            return

        self._path = path
        self._error_var.set('')
        self._file_var.set(os.path.basename(path))
        self._file_lbl.configure(text_color=_GREEN)

        # Show clear button
        self._clear_btn.grid(row=0, column=2, padx=(0, 8), pady=8, sticky='e')

        if self._on_file:
            self._on_file(path)

    def _clear(self) -> None:
        self._reset_ui()
        self._path = None
        if self._on_clear:
            self._on_clear()

    # ── Validation ─────────────────────────────────────────────────────────

    @staticmethod
    def _validate(path: str) -> str:
        """Return an error string, or '' if the file is acceptable."""
        if not os.path.isfile(path):
            return 'File not found.'
        ext = os.path.splitext(path)[1].lower()
        if ext not in _VALID_EXTENSIONS:
            return f"Unsupported file type '{ext}'. Use .csv or .xlsx."
        if os.path.getsize(path) == 0:
            return 'File is empty.'
        return ''

    # ── Helpers ────────────────────────────────────────────────────────────

    def _reset_ui(self) -> None:
        self._file_var.set('No file selected')
        self._file_lbl.configure(text_color=_GRAY)
        self._error_var.set('')
        self._clear_btn.grid_forget()
