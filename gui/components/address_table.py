"""
gui/components/address_table.py — Scrollable, reorderable stop list widget.

A self-contained CTkFrame that replaces the raw tk.Listbox in HomeView and
the inline row-building loop in ResultsView. Both views instantiate one
AddressTable and communicate through callbacks — no business logic lives here.

Usage (HomeView):
    self.table = AddressTable(
        parent,
        on_select=self._on_stop_selected,
        on_delete=self._on_stop_deleted,
        on_reorder=self._on_stops_reordered,
    )
    self.table.pack(fill="both", expand=True)
    self.table.set_addresses(["123 Main St", "456 Elm St"])

Callbacks receive the updated address list as their only argument so callers
never need to call get_addresses() in response to a mutation event.
"""

import customtkinter as ctk
from typing import Callable, Optional


_BLUE    = "#0057A8"
_BLUE = '#0057A8'
_NAVY = '#002855'
_ORANGE = '#F26522'
_WHITE = '#FFFFFF'
_GRAY = '#6B7280'
_SURFACE = '#1A2535'
_RED = '#EF4444'
_ROW_A = '#1A2535'
_ROW_B = '#1F2D42'
_HDR = '#9DB8D6'
_INPUT = '#243044'

class AddressTable(ctk.CTkFrame):
    """
    Scrollable, reorderable stop list widget for the FieldSnek desktop GUI.

    Parameters
    ----------
    parent : tk widget
        Parent container.
    on_select : callable(addresses, selected_idx) | None
        Called when the user clicks an address row.
        Receives the full list and the clicked index.
    on_delete : callable(addresses) | None
        Called after a stop is removed.  Receives the updated list.
    on_reorder : callable(addresses) | None
        Called after a stop is moved up or down.  Receives the updated list.
    show_header : bool
        Whether to render the #/Address/Actions column header row.
    """

    def __init__(
        self,
        parent,
        on_select: Optional[Callable] = None,
        on_delete: Optional[Callable] = None,
        on_reorder: Optional[Callable] = None,
        show_header: bool = True,
    ):
        super().__init__(parent, fg_color=_SURFACE, corner_radius=8)
        self._on_select = on_select
        self._on_delete = on_delete
        self._on_reorder = on_reorder
        self._show_header = show_header

        self._addresses: list[str] = []
        self._selected_idx: Optional[int] = None
        self._row_widgets: list[dict] = []

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._scroll = ctk.CTkScrollableFrame(
            self,
            fg_color=_SURFACE,
            corner_radius=6,
        )
        self._scroll.grid(row=0, column=0, sticky='nsew', padx=2, pady=2)
        self._scroll.grid_columnconfigure(0, weight=0, minsize=40)
        self._scroll.grid_columnconfigure(1, weight=1)
        self._scroll.grid_columnconfigure(2, weight=0, minsize=100)

        if self._show_header:
            self._build_header()



    def _build_header(self):
        for col, (txt, width) in enumerate([
            (' #', 40),
            ('Address', 300),
            ('Actions', 100),
        ]):
            ctk.CTkLabel(
                self._scroll,
                text=txt,
                font=ctk.CTkFont(size=12, weight='bold'),
                text_color=_HDR,
                width=width,
                anchor='w',
            ).grid(row=0, column=col, padx=(6, 4), pady=(6, 2), sticky='w')



    def set_addresses(self, addresses: list[str]) -> None:
        """Replace the entire list and re-render all rows."""
        self._addresses = list(addresses)
        self._selected_idx = None
        self._refresh()

    def get_addresses(self) -> list[str]:
        """Return a copy of the current ordered address list."""
        return list(self._addresses)

    def append(self, address: str) -> None:
        """Add a stop to the bottom of the list."""
        address = address.strip()
        if not address:
            return
        self._addresses.append(address)
        self._refresh()

    def delete(self, idx: int) -> None:
        """Remove the stop at *idx* and fire on_delete."""
        if not 0 <= idx < len(self._addresses):
            return
        self._addresses.pop(idx)
        if self._selected_idx is not None:
            if self._selected_idx == idx:
                self._selected_idx = None
            elif self._selected_idx > idx:
                self._selected_idx -= 1
        self._refresh()
        if self._on_delete:
            self._on_delete(list(self._addresses))

    def move(self, idx: int, direction: int) -> None:
        """
        Shift the stop at *idx* by *direction* positions (+1 down, -1 up).
        Fires on_reorder with the updated list.
        """
        new_idx = idx + direction
        if not (
            0 <= idx < len(self._addresses) and 0 <= new_idx < len(self._addresses)
        ):
            return
        addrs = self._addresses
        addrs[idx], addrs[new_idx] = addrs[new_idx], addrs[idx]
        if self._selected_idx == idx:
            self._selected_idx = new_idx
        elif self._selected_idx == new_idx:
            self._selected_idx = idx
        self._refresh()
        if self._on_reorder:
            self._on_reorder(list(self._addresses))

    def select(self, idx: int) -> None:
        """Programmatically select a row (highlights it, fires on_select)."""
        if not 0 <= idx < len(self._addresses):
            return
        self._selected_idx = idx
        self._highlight(idx)
        if self._on_select:
            self._on_select(list(self._addresses), idx)

    def clear(self) -> None:
        """Remove all stops without firing any callback."""
        self._addresses.clear()
        self._selected_idx = None
        self._refresh()



    def _refresh(self):
        """Destroy all row widgets and rebuild from self._addresses."""
        for rw in self._row_widgets:
            for widget in rw.values():
                try:
                    widget.destroy()
                except Exception:
                    pass
        self._row_widgets.clear()

        if not self._addresses:
            self._render_empty()
            return

        header_offset = 1 if self._show_header else 0

        for i, addr in enumerate(self._addresses):
            grid_row = i + header_offset
            is_selected = i == self._selected_idx
            self._render_row(i, grid_row, addr, is_selected)

    def _render_empty(self):
        """Show a placeholder when the list is empty."""
        lbl = ctk.CTkLabel(
            self._scroll,
            text='No stops added yet.',
            font=ctk.CTkFont(size=12),
            text_color=_GRAY,
            anchor='center',
        )
        header_offset = 1 if self._show_header else 0
        lbl.grid(row=header_offset, column=0, columnspan=3, pady=24)
        self._row_widgets.append({'empty': lbl})

    def _render_row(self, idx: int, grid_row: int, addr: str, selected: bool):
        widgets: dict = {}
        text_color = _ORANGE if selected else _WHITE


        num_lbl = ctk.CTkLabel(
            self._scroll,
            text=f' {idx + 1}',
            font=ctk.CTkFont(size=13, weight='bold'),
            text_color=_ORANGE,
            width=40,
            anchor='w',
        )
        num_lbl.grid(row=grid_row, column=0, padx=(6, 2), pady=3, sticky='w')
        widgets['num'] = num_lbl


        addr_lbl = ctk.CTkLabel(
            self._scroll,
            text=addr,
            font=ctk.CTkFont(size=12),
            text_color=text_color,
            anchor='w',
            wraplength=320,
        )
        addr_lbl.grid(row=grid_row, column=1, padx=(2, 4), pady=3, sticky='w')
        addr_lbl.bind('<Button-1>', lambda _e, i=idx: self._click_row(i))
        addr_lbl.bind(
            '<Enter>',
            lambda _e, lbl=addr_lbl, i=idx: lbl.configure(
                text_color=_ORANGE if i != self._selected_idx else _ORANGE
            ),
        )
        addr_lbl.bind(
            '<Leave>',
            lambda _e, lbl=addr_lbl, i=idx: lbl.configure(
                text_color=_ORANGE if i == self._selected_idx else _WHITE
            ),
        )
        widgets['addr'] = addr_lbl


        act = ctk.CTkFrame(self._scroll, fg_color='transparent')
        act.grid(row=grid_row, column=2, padx=4, pady=2, sticky='e')

        ctk.CTkButton(
            act,
            text='',
            width=28,
            height=26,
            fg_color='#3B1A1A',
            hover_color=_RED,
            text_color=_WHITE,
            font=ctk.CTkFont(size=11),
            command=lambda i=idx: self.delete(i),
        ).pack(side='left', padx=2)

        ctk.CTkButton(
            act,
            text='▲',
            width=28,
            height=26,
            fg_color='#243044',
            hover_color=_NAVY,
            text_color=_WHITE,
            font=ctk.CTkFont(size=10),
            command=lambda i=idx: self.move(i, -1),
        ).pack(side='left', padx=2)

        ctk.CTkButton(
            act,
            text='▼',
            width=28,
            height=26,
            fg_color='#243044',
            hover_color=_NAVY,
            text_color=_WHITE,
            font=ctk.CTkFont(size=10),
            command=lambda i=idx: self.move(i, +1),
        ).pack(side='left', padx=2)

        widgets['act'] = act
        self._row_widgets.append(widgets)



    def _click_row(self, idx: int):
        self._selected_idx = idx
        self._highlight(idx)
        if self._on_select:
            self._on_select(list(self._addresses), idx)

    def _highlight(self, selected_idx: int):
        """Update text colours without a full re-render."""
        for i, rw in enumerate(self._row_widgets):
            lbl = rw.get('addr')
            if lbl:
                lbl.configure(text_color=_ORANGE if i == selected_idx else _WHITE)
