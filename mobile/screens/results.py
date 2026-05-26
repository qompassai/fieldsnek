"""
mobile/screens/results.py — Route results screen for Kivy (Android).

Uses _KivyAddressTable for the stop list, keeping business logic in this
view and delegating all rendering/interaction to the component.
"""

import math
import threading
import urllib.parse
import webbrowser

from kivy.app import App
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import AsyncImage
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.utils import get_color_from_hex


C_SURFACE = get_color_from_hex('#1A2535ff')
C_CARD = get_color_from_hex('#243044ff')
C_BLUE = get_color_from_hex('#0057A8ff')
C_NAVY = get_color_from_hex('#002855ff')
C_ORANGE = get_color_from_hex('#F26522ff')
C_WHITE = get_color_from_hex('#FFFFFFff')
C_GRAY = get_color_from_hex('#6B7280ff')
C_RED = get_color_from_hex('#EF4444ff')
_FM_GREEN = get_color_from_hex('#1A5F3Fff')

def _btn(text: str, bg=C_BLUE, **kw) -> Button:
    return Button(
        text=text,
        background_color=bg,
        color=C_WHITE,
        size_hint_y=None,
        height=dp(42),
        **kw,
    )

class ResultsScreen(Screen):
    """
    Displays the optimised route with an editable stop list, location
    preview, and map-launch actions.
    """

    def __init__(self, **kw):
        super().__init__(**kw)
        self._selected_idx: int | None = None
        self._layout_built = False



    def on_enter(self):
        if not self._layout_built:
            self._build()
            self._layout_built = True
        self._populate()



    def _build(self):
        root = BoxLayout(orientation='vertical', spacing=dp(8), padding=[dp(10), dp(6)])


        header = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
        back_btn = _btn('← Back', bg=C_NAVY, size_hint_x=None, width=dp(80))
        back_btn.bind(
            on_release=lambda *_: App.get_running_app().navigate('home', 'right')
        )
        header.add_widget(back_btn)
        self.summary_lbl = Label(
            text='Route', color=C_WHITE, font_size=dp(14), bold=True
        )
        header.add_widget(self.summary_lbl)
        settings_btn = _btn('', bg=C_NAVY, size_hint_x=None, width=dp(44))
        settings_btn.bind(
            on_release=lambda *_: App.get_running_app().navigate('settings')
        )
        header.add_widget(settings_btn)
        root.add_widget(header)


        map_row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))
        maps_btn = _btn(' Google Maps', bg=C_BLUE)
        maps_btn.bind(on_release=lambda *_: self._open_maps_all())
        map_row.add_widget(maps_btn)
        fm_all_btn = _btn(' FieldMaps', bg=_FM_GREEN)
        fm_all_btn.bind(on_release=lambda *_: self._open_fieldmaps_first())
        map_row.add_widget(fm_all_btn)
        root.add_widget(map_row)


        sv_card = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(220),
            padding=[dp(8), dp(4)],
            spacing=dp(4),
        )
        sv_header = BoxLayout(size_hint_y=None, height=dp(32), spacing=dp(8))
        sv_header.add_widget(
            Label(
                text='[b]Street View[/b]',
                markup=True,
                color=C_WHITE,
                font_size=dp(14),
                size_hint_x=1,
            )
        )
        sv_open_btn = _btn(
            ' Open', bg=C_CARD, size_hint_x=None, width=dp(80), height=dp(32)
        )
        sv_open_btn.bind(on_release=lambda *_: self._open_sv_browser())
        sv_header.add_widget(sv_open_btn)
        sv_card.add_widget(sv_header)

        self.sv_addr_lbl = Label(
            text='Tap a stop to preview',
            color=C_GRAY,
            font_size=dp(11),
            size_hint_y=None,
            height=dp(20),
        )
        sv_card.add_widget(self.sv_addr_lbl)

        self.sv_image = AsyncImage(
            source='',
            allow_stretch=True,
            keep_ratio=True,
            size_hint_y=None,
            height=dp(160),
            nocache=True,
        )
        sv_card.add_widget(self.sv_image)
        root.add_widget(sv_card)


        add_row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))
        self.add_input = TextInput(
            hint_text='Add a stop…',
            multiline=False,
            background_color=C_CARD,
            foreground_color=C_WHITE,
            hint_text_color=C_GRAY,
            cursor_color=C_WHITE,
            font_size=dp(13),
        )
        self.add_input.bind(on_text_validate=lambda *_: self._add_stop())
        add_row.add_widget(self.add_input)
        add_btn = _btn('+ Add', size_hint_x=None, width=dp(70))
        add_btn.bind(on_release=lambda *_: self._add_stop())
        add_row.add_widget(add_btn)
        root.add_widget(add_row)


        scroll = ScrollView(size_hint=(1, 1))
        self.address_table = _KivyAddressTable(
            on_select=self._on_table_select,
            on_delete=self._on_table_delete,
        )
        scroll.add_widget(self.address_table)
        root.add_widget(scroll)


        resolve_btn = _btn(' Re-optimize Route', bg=C_ORANGE)
        resolve_btn.font_size = dp(15)
        resolve_btn.height = dp(50)
        resolve_btn.bind(on_release=lambda *_: self._re_solve())
        root.add_widget(resolve_btn)

        self.add_widget(root)

    def _populate(self):
        app = App.get_running_app()
        result = app.route_result
        if not result:
            return
        from core.exporter import format_duration

        dur = format_duration(result.total_duration_seconds)
        self.summary_lbl.text = f'{len(result.ordered_addresses)} stops · {dur}'
        self.address_table.set_addresses(result.ordered_addresses)
        if result.ordered_addresses:
            self._select_stop(0)

    def _on_table_select(self, _addresses: list[str], idx: int):
        self._select_stop(idx)

    def _on_table_delete(self, addresses: list[str]):
        """Sync app state to match the updated address list."""
        self._sync_locations(addresses)

    def _sync_locations(self, addresses: list[str]):
        """Keep app.locations in step with the edited address list."""
        app = App.get_running_app()
        result = app.route_result
        if not result:
            return
        result.ordered_addresses = list(addresses)
        old_locs = {loc['address']: loc for loc in (app.locations or [])}
        app.locations = [old_locs[a] for a in addresses if a in old_locs]
        from core.exporter import format_duration

        dur = format_duration(result.total_duration_seconds)
        self.summary_lbl.text = f'{len(addresses)} stops · {dur}'



    def _select_stop(self, idx: int):
        self._selected_idx = idx
        app = App.get_running_app()
        result = app.route_result
        if not result or idx >= len(result.ordered_addresses):
            return
        addr = result.ordered_addresses[idx]
        self.sv_addr_lbl.text = f'Stop {idx + 1}: {addr}'
        threading.Thread(
            target=self._load_sv,
            args=(idx, addr, app.locations),
            daemon=True,
        ).start()

    def _load_sv(self, idx: int, addr: str, locs: list[dict]):
        """
        Fetch a location preview on a background thread, then schedule
        the UI update back on the main thread via a named inner function
        (avoids function calls in lambda defaults — Ruff B006).

        Priority:
          1. Google Street View Static API (requires API key)
          2. Free OSM tile (no key required)
        """
        from config.settings import GOOGLE_MAPS_API_KEY
        from core.exporter import build_streetview_url

        lat = lng = None
        for loc in locs:
            if loc['address'] == addr:
                lat, lng = loc.get('lat'), loc.get('lng')
                break

        def _schedule(image_url: str, source: str) -> None:
            """Push the image update to the Kivy main thread."""
            Clock.schedule_once(lambda _dt: self._set_sv(image_url, idx, addr, source))

        key = GOOGLE_MAPS_API_KEY
        if key and lat is not None and lng is not None:
            try:
                _schedule(
                    build_streetview_url(
                        lat, lng, addr, api_key=key, width=600, height=300
                    ),
                    'Street View',
                )
                return
            except Exception:
                pass

        if lat is not None and lng is not None:
            zoom = 16
            tile_x = int((lng + 180) / 360 * 2**zoom)
            lat_rad = math.radians(lat)
            tile_y = int(
                (1 - math.log(math.tan(lat_rad) + 1 / math.cos(lat_rad)) / math.pi)
                / 2
                * 2**zoom
            )
            _schedule(
                f'https://tile.openstreetmap.org/{zoom}/{tile_x}/{tile_y}.png',
                'OpenStreetMap',
            )
        else:
            Clock.schedule_once(
                lambda _dt: setattr(
                    self.sv_addr_lbl,
                    'text',
                    f'Stop {idx + 1}: {addr} · (location unknown)',
                )
            )

    def _set_sv(self, image_url: str, idx: int, addr: str, source: str):
        self.sv_image.source = image_url
        self.sv_image.reload()
        self.sv_addr_lbl.text = f'Stop {idx + 1}: {addr} · {source}'



    def _add_stop(self):
        addr = self.add_input.text.strip()
        if not addr:
            return
        app = App.get_running_app()
        result = app.route_result
        if result:
            result.ordered_addresses.append(addr)
            self.add_input.text = ''
            self.address_table.set_addresses(result.ordered_addresses)



    def _re_solve(self):
        app = App.get_running_app()
        result = app.route_result
        if not result:
            return
        home = app.home_screen
        home._stop_list = list(result.ordered_addresses)
        home._refresh_list()
        app.navigate('home', 'right')
        Clock.schedule_once(lambda _dt: home._start_solve(), 0.3)



    def _open_maps_all(self):
        app = App.get_running_app()
        result = app.route_result
        if not result:
            return
        from core.exporter import build_maps_url, build_maps_url_chunked

        addrs = result.ordered_addresses
        if len(addrs) <= 10:
            webbrowser.open(build_maps_url(addrs))
        else:
            for chunk_url in build_maps_url_chunked(addrs):
                webbrowser.open(chunk_url)

    def _open_fieldmaps_first(self):
        self._open_fieldmaps_stop(0)

    def _open_fieldmaps_stop(self, idx: int):
        app = App.get_running_app()
        result = app.route_result
        if not result or idx >= len(result.ordered_addresses):
            return
        from config.settings import ARCGIS_ITEM_ID
        from core.exporter import build_fieldmaps_url

        addr = result.ordered_addresses[idx]
        lat = lng = None
        for loc in app.locations:
            if loc['address'] == addr:
                lat, lng = loc.get('lat'), loc.get('lng')
                break
        webbrowser.open(
            build_fieldmaps_url(addr, lat, lng, item_id=ARCGIS_ITEM_ID or None)
        )

    def _open_sv_browser(self):
        if self._selected_idx is None:
            return
        app = App.get_running_app()
        result = app.route_result
        if not result:
            return
        addr = result.ordered_addresses[self._selected_idx]
        for loc in app.locations:
            if loc['address'] == addr and loc.get('lat'):
                lat, lng = loc['lat'], loc['lng']
                webbrowser.open(
                    f'https://www.google.com/maps/@{lat},{lng},3a,90y,0h,90t/data=!3m4!1e1'
                )
                return
        webbrowser.open(
            f'https://www.google.com/maps/search/{urllib.parse.quote_plus(addr)}'
        )



class _KivyAddressTable(BoxLayout):
    """
    Kivy-native stop list widget (mirrors desktop AddressTable API).

    Renders one row per address with a tap-to-select button, a delete
    button, and a FieldMaps shortcut.  All mutation goes through
    set_addresses() so the parent view stays authoritative over the data.
    """

    def __init__(self, on_select=None, on_delete=None, **kw):
        super().__init__(
            orientation='vertical',
            spacing=dp(4),
            size_hint_y=None,
            padding=[0, dp(4)],
            **kw,
        )
        self.bind(minimum_height=self.setter('height'))
        self._on_select = on_select
        self._on_delete = on_delete
        self._addresses: list[str] = []



    def set_addresses(self, addresses: list[str]) -> None:
        self._addresses = list(addresses)
        self._refresh()

    def get_addresses(self) -> list[str]:
        return list(self._addresses)



    def _refresh(self):
        self.clear_widgets()
        for i, addr in enumerate(self._addresses):
            self.add_widget(self._make_row(i, addr))

    def _make_row(self, idx: int, addr: str):
        row = BoxLayout(
            size_hint_y=None,
            height=dp(48),
            spacing=dp(6),
            padding=[dp(4), dp(2)],
        )
        row.add_widget(
            Label(
                text=f'[b]{idx + 1}[/b]',
                markup=True,
                color=C_ORANGE,
                size_hint_x=None,
                width=dp(28),
                font_size=dp(14),
            )
        )
        addr_btn = Button(
            text=addr,
            color=C_WHITE,
            halign='left',
            valign='middle',
            background_color=C_SURFACE,
            font_size=dp(12),
        )
        addr_btn.text_size = (None, None)
        addr_btn.bind(on_release=lambda _b, i=idx: self._handle_select(i))
        row.add_widget(addr_btn)

        del_btn = Button(
            text='',
            background_color=C_RED,
            color=C_WHITE,
            size_hint_x=None,
            width=dp(36),
        )
        del_btn.bind(on_release=lambda _b, i=idx: self._handle_delete(i))
        row.add_widget(del_btn)

        fm_btn = Button(
            text='',
            background_color=_FM_GREEN,
            color=C_WHITE,
            size_hint_x=None,
            width=dp(36),
        )
        fm_btn.bind(on_release=lambda _b, i=idx: self._handle_fieldmaps(i))
        row.add_widget(fm_btn)

        return row



    def _handle_select(self, idx: int):
        if self._on_select:
            self._on_select(list(self._addresses), idx)

    def _handle_delete(self, idx: int):
        if 0 <= idx < len(self._addresses):
            self._addresses.pop(idx)
            self._refresh()
            if self._on_delete:
                self._on_delete(list(self._addresses))

    def _handle_fieldmaps(self, idx: int):
        """Delegate FieldMaps launch to the parent screen via the app."""
        screen = App.get_running_app().root.get_screen('results')
        screen._open_fieldmaps_stop(idx)
