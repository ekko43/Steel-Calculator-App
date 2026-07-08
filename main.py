"""
================================================================================
  STEEL SECTION ADEQUACY CHECKER — Android (Kivy) front end
  Uses the untouched steel_checker_core.py for all data and formulas.
================================================================================
"""
import math

import steel_checker_core as core

from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.properties import StringProperty, BooleanProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen, ScreenManager, NoTransition
from kivy.uix.popup import Popup
from kivy.uix.recycleview import RecycleView
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.textinput import TextInput

# ─────────────────────────────────────────────
#  THEME
# ─────────────────────────────────────────────
BG      = "1e1e2e"
PANEL   = "313244"
FIELD   = "45475a"
TEXT    = "cdd6f4"
SUBTEXT = "a6adc8"
ACCENT  = "89b4fa"
GREEN   = "a6e3a1"
RED     = "f38ba8"
YELLOW  = "f9e2af"

def _kv_rgba(hexstr, a=1):
    r, g, b = (int(hexstr[i:i + 2], 16) / 255 for i in (0, 2, 4))
    return f"{r}, {g}, {b}, {a}"


Window.clearcolor = tuple(int(BG[i:i + 2], 16) / 255 for i in (0, 2, 4)) + (1,)

KV = f"""
#:import dp kivy.metrics.dp

<SectionLabel@Label>:
    color: {_kv_rgba(TEXT)}
    font_size: '15sp'
    size_hint_y: None
    height: self.texture_size[1] + dp(10)
    text_size: self.width, None
    halign: 'left'
    valign: 'middle'

<TitleLabel@Label>:
    color: {_kv_rgba(ACCENT)}
    font_size: '20sp'
    bold: True
    size_hint_y: None
    height: dp(40)

<FieldInput@TextInput>:
    multiline: False
    size_hint_y: None
    height: dp(46)
    font_size: '16sp'
    background_color: {_kv_rgba(FIELD)}
    foreground_color: {_kv_rgba(TEXT)}
    cursor_color: {_kv_rgba(ACCENT)}
    padding: [dp(10), dp(12), dp(10), dp(12)]
    hint_text_color: {_kv_rgba(SUBTEXT)}

<AccentButton@Button>:
    background_normal: ''
    background_down: ''
    background_color: {_kv_rgba(ACCENT)}
    color: 0.12, 0.12, 0.18, 1
    bold: True
    size_hint_y: None
    height: dp(48)
    font_size: '16sp'

<GhostButton@Button>:
    background_normal: ''
    background_down: ''
    background_color: {_kv_rgba(FIELD)}
    color: {_kv_rgba(TEXT)}
    size_hint_y: None
    height: dp(48)
    font_size: '15sp'

<PanelBox@BoxLayout>:
    canvas.before:
        Color:
            rgba: {_kv_rgba(PANEL)}
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(12)]
    padding: dp(12)
    spacing: dp(8)
    orientation: 'vertical'
    size_hint_y: None
    height: self.minimum_height

<SectionRow>:
    size_hint_y: None
    height: dp(46)
    canvas.before:
        Color:
            rgba: (0.35,0.45,0.75,0.35) if root.selected else (0,0,0,0)
        Rectangle:
            pos: self.pos
            size: self.size
"""
Builder.load_string(KV)


def rgba(hexstr, a=1):
    return tuple(int(hexstr[i:i + 2], 16) / 255 for i in (0, 2, 4)) + (a,)


# ─────────────────────────────────────────────
#  SECTION PICKER POPUP (search + list)
# ─────────────────────────────────────────────
class SectionRow(RecycleDataViewBehavior, Button):
    index = None
    selected = BooleanProperty(False)
    section_name = StringProperty("")
    callback = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ""
        self.background_down = ""
        self.background_color = rgba(PANEL)
        self.color = rgba(TEXT)
        self.size_hint_y = None
        self.height = dp(44)

    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        self.section_name = data.get("text", "")
        self.text = self.section_name
        self.callback = data.get("callback")
        return super().refresh_view_attrs(rv, index, data)

    def on_release(self):
        if self.callback:
            self.callback(self.section_name)


class SectionRV(RecycleView):
    pass


class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior, RecycleBoxLayout):
    pass


class SectionPicker(BoxLayout):
    """A button that opens a searchable popup list of section names."""

    def __init__(self, names, on_select, placeholder="Select section", **kwargs):
        super().__init__(orientation="vertical", size_hint_y=None, height=dp(46), **kwargs)
        self.names = sorted(names)
        self.on_select_cb = on_select
        self.placeholder = placeholder
        self.chosen = None
        from kivy.uix.button import Button as KButton
        self.btn = KButton(
            text=placeholder,
            size_hint_y=None,
            height=dp(46),
            background_normal="",
            background_down="",
            background_color=rgba(FIELD),
            color=rgba(TEXT),
            font_size="15sp",
        )
        self.btn.bind(on_release=self.open_popup)
        self.add_widget(self.btn)

    def open_popup(self, *a):
        content = BoxLayout(orientation="vertical", spacing=dp(6), padding=dp(8))
        search = FieldInputPlain(hint_text="Search section...")
        content.add_widget(search)

        rv = SectionRV(size_hint=(1, 1))
        rv.viewclass = "SectionRow"
        box = SelectableRecycleBoxLayout(
            default_size=(None, dp(44)),
            default_size_hint=(1, None),
            size_hint_y=None,
            orientation="vertical",
        )
        box.bind(minimum_height=box.setter("height"))
        rv.add_widget(box)

        popup = Popup(
            title=self.placeholder,
            content=content,
            size_hint=(0.9, 0.85),
            title_color=rgba(ACCENT),
            separator_color=rgba(ACCENT),
            background_color=rgba(BG),
        )

        def do_select(name):
            self.chosen = name
            self.btn.text = name
            popup.dismiss()
            if self.on_select_cb:
                self.on_select_cb(name)

        rv.data = [{"text": n, "callback": do_select} for n in self.names]

        def filter_list(instance, text):
            t = text.strip().upper()
            filtered = [n for n in self.names if t in n.upper()] if t else self.names
            rv.data = [{"text": n, "callback": do_select} for n in filtered]

        search.bind(text=filter_list)
        popup.open()


class FieldInputPlain(TextInput):
    def __init__(self, **kwargs):
        super().__init__(
            multiline=False,
            size_hint_y=None,
            height=dp(46),
            font_size="16sp",
            background_color=rgba(FIELD),
            foreground_color=rgba(TEXT),
            cursor_color=rgba(ACCENT),
            padding=[dp(10), dp(12), dp(10), dp(12)],
            **kwargs,
        )


# ─────────────────────────────────────────────
#  CALCULATION (mirrors the original PyQt5 GUI logic, using core.py)
# ─────────────────────────────────────────────
def compute_compression(A_mm2, rx_mm, ry_mm, Lc_mm, K, Pu_N, Pa_N, label):
    KLx = K * Lc_mm / rx_mm
    KLy = K * Lc_mm / ry_mm
    KLr = max(KLx, KLy)

    Fcr = core.critical_stress(KLr)
    Fe = math.pi ** 2 * core.E / KLr ** 2
    Pn = Fcr * (A_mm2 * 1e-6)

    phi_Pn = core.PHI_C * Pn
    Pn_asd = Pn / core.OMEGA_C

    r = {
        "label": label,
        "A": A_mm2, "rx": rx_mm, "ry": ry_mm, "Lc": Lc_mm, "K": K,
        "KLx": KLx, "KLy": KLy, "KLr": KLr,
        "Fe": Fe / 1e6, "Fcr": Fcr / 1e6, "Pn": Pn / 1e3,
        "phi_Pn": phi_Pn / 1e3, "Pn_asd": Pn_asd / 1e3,
        "Pu": Pu_N / 1e3 if Pu_N > 0 else None,
        "Pa": Pa_N / 1e3 if Pa_N > 0 else None,
    }
    if r["Pu"] is not None:
        r["dcr_lrfd"] = Pu_N / phi_Pn
        r["ok_lrfd"] = r["dcr_lrfd"] <= 1.0
    if r["Pa"] is not None:
        r["dcr_asd"] = Pa_N / Pn_asd
        r["ok_asd"] = r["dcr_asd"] <= 1.0
    return r


def result_to_markup(r):
    def line(label, val, unit=""):
        return f"[color={SUBTEXT}]{label}:[/color] [color={TEXT}]{val}{(' ' + unit) if unit else ''}[/color]"

    out = []
    out.append(f"[b][color={ACCENT}]{r['label']}[/color][/b]")
    out.append(line("Gross area A", f"{r['A']:.0f}", "mm²"))
    out.append(line("rx / ry", f"{r['rx']:.1f} / {r['ry']:.1f}", "mm"))
    out.append(line("Lc / K", f"{r['Lc']:.0f} mm / {r['K']:.2f}"))
    out.append(line("Governing KL/r", f"{r['KLr']:.1f}"))
    out.append(line("Fe / Fcr", f"{r['Fe']:.1f} / {r['Fcr']:.1f}", "MPa"))
    out.append(line("Nominal strength Pn", f"{r['Pn']:.1f}", "kN"))
    out.append("")
    out.append(f"[b][color={YELLOW}]LRFD[/color][/b]")
    out.append(line("phi_c Pn", f"{r['phi_Pn']:.1f}", "kN"))
    if r["Pu"] is not None:
        out.append(line("Pu", f"{r['Pu']:.1f}", "kN"))
        out.append(line("DCR", f"{r['dcr_lrfd']:.3f}"))
        c = GREEN if r["ok_lrfd"] else RED
        tag = "ADEQUATE" if r["ok_lrfd"] else "INADEQUATE"
        out.append(f"[b][color={c}]{tag}[/color][/b]")
    else:
        out.append(f"[color={SUBTEXT}](capacity only, no Pu given)[/color]")
    out.append("")
    out.append(f"[b][color={YELLOW}]ASD[/color][/b]")
    out.append(line("Pn / Omega_c", f"{r['Pn_asd']:.1f}", "kN"))
    if r["Pa"] is not None:
        out.append(line("Pa", f"{r['Pa']:.1f}", "kN"))
        out.append(line("DCR", f"{r['dcr_asd']:.3f}"))
        c = GREEN if r["ok_asd"] else RED
        tag = "ADEQUATE" if r["ok_asd"] else "INADEQUATE"
        out.append(f"[b][color={c}]{tag}[/color][/b]")
    else:
        out.append(f"[color={SUBTEXT}](capacity only, no Pa given)[/color]")
    out.append("─" * 40)
    return "\n".join(out)


MENU = [
    ("W / Wide Flange", "W"),
    ("WT Section", "WT"),
    ("HSS Rectangular", "HSS_RECT"),
    ("HSS Round", "HSS_RND"),
    ("Single Angle (L)", "L"),
    ("Double Angle (2L)", "2L"),
    ("Channel (C)", "C"),
    ("Built-up: Channel + W", "BU_CW"),
    ("Built-up: Plate W-Shape", "BU_PW"),
]


def to_float(txt, default=0.0):
    try:
        return float(txt.strip())
    except Exception:
        return default


# ─────────────────────────────────────────────
#  MAIN SCREEN
# ─────────────────────────────────────────────
class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        from kivy.uix.scrollview import ScrollView
        from kivy.uix.spinner import Spinner
        from kivy.uix.gridlayout import GridLayout
        from kivy.uix.label import Label

        self.results_log = []
        self.picked = {}     # per-type chosen section widgets
        self.sep_group = None
        self.symmetric_toggle = None
        self.bottom_box = None

        root = BoxLayout(orientation="vertical")
        scroll = ScrollView()
        self.col = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(10), padding=dp(12))
        self.col.bind(minimum_height=self.col.setter("height"))
        scroll.add_widget(self.col)
        root.add_widget(scroll)
        self.add_widget(root)

        self.col.add_widget(Label(
            text="Steel Section Checker",
            color=rgba(ACCENT), bold=True, font_size="22sp",
            size_hint_y=None, height=dp(44),
        ))
        self.col.add_widget(Label(
            text="AISC 360-22  |  LRFD & ASD  |  SI Units  |  Compression only",
            color=rgba(SUBTEXT), font_size="12sp",
            size_hint_y=None, height=dp(22),
        ))

        # --- Section type ---
        type_panel = self._panel()
        type_panel.add_widget(self._label("Section type"))
        self.type_spinner = Spinner(
            text=MENU[0][0], values=[m[0] for m in MENU],
            size_hint_y=None, height=dp(46),
            background_normal="", background_down="",
            background_color=rgba(FIELD), color=rgba(TEXT),
        )
        self.type_spinner.bind(text=self.on_type_change)
        type_panel.add_widget(self.type_spinner)
        self.col.add_widget(type_panel)

        # --- Common inputs ---
        common_panel = self._panel()
        common_panel.add_widget(self._label("Common inputs"))
        grid = GridLayout(cols=2, size_hint_y=None, spacing=dp(6))
        grid.bind(minimum_height=grid.setter("height"))
        self.in_Lc = self._labeled_input(grid, "Unbraced length Lc (mm)")
        self.in_K = self._labeled_input(grid, "Effective length factor K", default="1.0")
        self.in_Pu = self._labeled_input(grid, "Factored load Pu (kN)  [0=skip]", default="0")
        self.in_Pa = self._labeled_input(grid, "Service load Pa (kN)  [0=skip]", default="0")
        common_panel.add_widget(grid)
        self.col.add_widget(common_panel)

        # --- Dynamic section-specific area ---
        self.dynamic_panel = self._panel()
        self.col.add_widget(self.dynamic_panel)
        self.build_dynamic_area("W")

        # --- Buttons ---
        btn_row = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        calc_btn = Builder.load_string("AccentButton:\n    text: 'Calculate'")
        calc_btn.bind(on_release=self.on_calculate)
        clear_btn = Builder.load_string("GhostButton:\n    text: 'Clear Log'")
        clear_btn.bind(on_release=self.on_clear)
        btn_row.add_widget(calc_btn)
        btn_row.add_widget(clear_btn)
        self.col.add_widget(btn_row)

        # --- Results log ---
        self.results_label = Label(
            text="", markup=True, size_hint_y=None,
            text_size=(Window.width - dp(40), None),
            halign="left", valign="top", font_size="14sp",
        )
        self.results_label.bind(texture_size=lambda *a: setattr(
            self.results_label, "height", self.results_label.texture_size[1]))
        self.col.add_widget(self.results_label)

    # ---- small builders ----
    def _panel(self):
        return Builder.load_string("PanelBox:")

    def _label(self, text):
        lbl = Builder.load_string(f"SectionLabel:\n    text: {text!r}")
        return lbl

    def _labeled_input(self, grid, hint, default=""):
        from kivy.uix.label import Label
        grid.add_widget(Label(
            text=hint, color=rgba(SUBTEXT), font_size="12sp",
            size_hint_y=None, height=dp(46), halign="left", valign="middle",
            text_size=(dp(150), dp(46)),
        ))
        ti = FieldInputPlain(text=default)
        grid.add_widget(ti)
        return ti

    # ---- dynamic area per section type ----
    def on_type_change(self, spinner, text):
        key = next(m[1] for m in MENU if m[0] == text)
        self.build_dynamic_area(key)

    def build_dynamic_area(self, key):
        self.dynamic_panel.clear_widgets()
        self.current_key = key
        self.dynamic_panel.add_widget(self._label(f"[b]{key}[/b] inputs"))

        if key in ("W", "WT", "HSS_RECT", "HSS_RND", "L", "C"):
            names = list(core.SECTIONS[key].keys())
            picker = SectionPicker(names, on_select=lambda n: None, placeholder=f"Select {key} section")
            self.dynamic_panel.add_widget(picker)
            self.picked = {"main": picker}

        elif key == "2L":
            names = list(core.SECTIONS["2L"].keys())
            picker = SectionPicker(names, on_select=lambda n: None, placeholder="Select 2L section")
            self.dynamic_panel.add_widget(picker)
            self.dynamic_panel.add_widget(self._label("Back-to-back separation"))
            sep_row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
            self.sep_buttons = []
            for i, mm in enumerate(("0 mm", "3 mm", "9 mm")):
                tb = ToggleButton(
                    text=mm, group="sep", state="down" if i == 0 else "normal",
                    background_normal="", background_down="",
                    background_color=rgba(ACCENT) if i == 0 else rgba(FIELD),
                    color=(0.1, 0.1, 0.15, 1) if i == 0 else rgba(TEXT),
                )
                sep_row.add_widget(tb)
                self.sep_buttons.append(tb)
            self.dynamic_panel.add_widget(sep_row)
            self.picked = {"main": picker}

        elif key == "BU_CW":
            w_names = list(core.W_DB.keys())
            c_names = list(core.C_DB.keys())
            w_picker = SectionPicker(w_names, on_select=lambda n: None, placeholder="Select W component")
            c_picker = SectionPicker(c_names, on_select=lambda n: None, placeholder="Select C component")
            self.dynamic_panel.add_widget(w_picker)
            self.dynamic_panel.add_widget(c_picker)
            grid = self._grid1()
            self.in_gap = self._labeled_input(grid, "Gap between W & C (mm)", default="0")
            self.dynamic_panel.add_widget(grid)
            self.picked = {"w": w_picker, "c": c_picker}

        elif key == "BU_PW":
            grid = self._grid1()
            self.in_bf_top = self._labeled_input(grid, "Top flange width bf_top (mm)")
            self.in_tf_top = self._labeled_input(grid, "Top flange thickness tf_top (mm)")
            self.in_hw = self._labeled_input(grid, "Web clear height hw (mm)")
            self.in_tw = self._labeled_input(grid, "Web thickness tw (mm)")
            self.dynamic_panel.add_widget(grid)

            sym_btn = ToggleButton(
                text="Symmetric (bottom = top flange)", state="down",
                size_hint_y=None, height=dp(44),
                background_normal="", background_down="",
                background_color=rgba(ACCENT), color=(0.1, 0.1, 0.15, 1),
            )
            self.dynamic_panel.add_widget(sym_btn)
            self.symmetric_toggle = sym_btn

            self.bottom_box = self._grid1()
            self.in_bf_bot = self._labeled_input(self.bottom_box, "Bottom flange width bf_bot (mm)")
            self.in_tf_bot = self._labeled_input(self.bottom_box, "Bottom flange thickness tf_bot (mm)")
            self.bottom_box.opacity = 0
            self.bottom_box.disabled = True
            self.bottom_box.size_hint_y = None
            self.bottom_box.height = 0
            self.dynamic_panel.add_widget(self.bottom_box)

            def toggle_sym(instance, value):
                is_sym = instance.state == "down"
                instance.background_color = rgba(ACCENT) if is_sym else rgba(FIELD)
                instance.color = (0.1, 0.1, 0.15, 1) if is_sym else rgba(TEXT)
                self.bottom_box.disabled = is_sym
                self.bottom_box.opacity = 0 if is_sym else 1
                self.bottom_box.height = 0 if is_sym else self.bottom_box.minimum_height

            sym_btn.bind(state=toggle_sym)

    def _grid1(self):
        from kivy.uix.gridlayout import GridLayout
        g = GridLayout(cols=2, size_hint_y=None, spacing=dp(6))
        g.bind(minimum_height=g.setter("height"))
        return g

    # ---- calculate ----
    def on_calculate(self, *a):
        key = self.current_key
        Lc = to_float(self.in_Lc.text)
        K = to_float(self.in_K.text, 1.0)
        Pu = to_float(self.in_Pu.text) * 1e3
        Pa = to_float(self.in_Pa.text) * 1e3

        if Lc <= 0:
            self._append_error("Enter a valid unbraced length Lc (mm) > 0.")
            return

        try:
            if key in ("W", "WT", "HSS_RECT", "HSS_RND", "L", "C"):
                name = self.picked["main"].chosen
                if not name:
                    self._append_error("Please select a section first.")
                    return
                A, rx, ry, label = self._props_standard(key, name)
                r = compute_compression(A, rx, ry, Lc, K, Pu, Pa, label)

            elif key == "2L":
                name = self.picked["main"].chosen
                if not name:
                    self._append_error("Please select a section first.")
                    return
                sep_choice = next(tb.text for tb in self.sep_buttons if tb.state == "down")
                s = float(sep_choice.split()[0])
                A, rx, ry, label = self._props_2L(name, s)
                r = compute_compression(A, rx, ry, Lc, K, Pu, Pa, label)

            elif key == "BU_CW":
                w_name = self.picked["w"].chosen
                c_name = self.picked["c"].chosen
                if not w_name or not c_name:
                    self._append_error("Please select both the W and C components.")
                    return
                gap = to_float(self.in_gap.text, 0.0)
                A, rx, ry, desc = core.builtup_channel_W(w_name, c_name, gap)
                r = compute_compression(A, rx, ry, Lc, K, Pu, Pa, desc)

            elif key == "BU_PW":
                bf_top = to_float(self.in_bf_top.text)
                tf_top = to_float(self.in_tf_top.text)
                hw = to_float(self.in_hw.text)
                tw = to_float(self.in_tw.text)
                if min(bf_top, tf_top, hw, tw) <= 0:
                    self._append_error("Fill in all top-flange / web dimensions (> 0).")
                    return
                if self.symmetric_toggle.state == "down":
                    bf_bot = tf_bot = None
                else:
                    bf_bot = to_float(self.in_bf_bot.text)
                    tf_bot = to_float(self.in_tf_bot.text)
                    if min(bf_bot, tf_bot) <= 0:
                        self._append_error("Fill in bottom-flange dimensions (> 0), or toggle Symmetric.")
                        return
                A, rx, ry, desc = core.builtup_plate_W(bf_top, tf_top, hw, tw, bf_bot, tf_bot)
                r = compute_compression(A, rx, ry, Lc, K, Pu, Pa, desc)

            else:
                return

            self.results_log.insert(0, result_to_markup(r))
            self.results_label.text = "\n\n".join(self.results_log)

        except ZeroDivisionError:
            self._append_error("Calculation error: a dimension was zero.")
        except Exception as e:
            self._append_error(f"Error: {e}")

    def _append_error(self, msg):
        self.results_log.insert(0, f"[color={RED}][b]{msg}[/b][/color]\n" + "─" * 40)
        self.results_label.text = "\n\n".join(self.results_log)

    def _props_standard(self, key, name):
        props = core.SECTIONS[key][name]
        if key == "HSS_RND":
            A = core._to_float(props[0])
            r = core._to_float(props[1])
            rx = ry = r
        elif key == "L":
            A = core._to_float(props[0])
            rz = core._to_float(props[1])
            rx = core._to_float(props[2])
            ry = rz
        else:
            A = core._to_float(props[0])
            rx = core._to_float(props[1])
            ry = core._to_float(props[2])
        return A, rx, ry, f"{key}  {name}"

    def _props_2L(self, name, s):
        props = core.SECTIONS["2L"][name]
        A = core._to_float(props[0])
        rx = core._to_float(props[1])
        ry_0 = core._to_float(props[2])
        ry_3 = core._to_float(props[3])
        ry_9 = core._to_float(props[4])
        if ry_3 is None and ry_9 is None:
            ry = ry_0
        elif s <= 0 or ry_3 is None:
            ry = ry_0
        elif s <= 6 or ry_9 is None:
            ry = ry_3
        else:
            ry = ry_9
        return A, rx, ry, f"2L  {name}  (sep={s:.0f}mm)"

    def on_clear(self, *a):
        self.results_log = []
        self.results_label.text = ""


class SteelCheckerApp(App):
    def build(self):
        self.title = "Steel Section Checker"
        sm = ScreenManager(transition=NoTransition())
        sm.add_widget(MainScreen(name="main"))
        return sm


if __name__ == "__main__":
    SteelCheckerApp().run()
