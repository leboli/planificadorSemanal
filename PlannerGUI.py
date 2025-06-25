import flet as ft
from entities.fixedActivity import fixedActivity
from entities.variableActivity import variableActivity
from entities.dailyUtility import dailyUtility
from planner import planner
from ast import literal_eval

# Translation dictionaries
dicts = {
    "en": {
        "language": "Language",
        "time_unit": "Time unit/Time slot size",
        "one_hour": "1 hour",
        "thirty_min": "30 minutes",
        "fifteen_min": "15 minutes",
        "activities": "Activities",
        "add": "Add",
        "edit": "Edit",
        "solve": "SOLVE",
        "type": "Type",
        "fixed": "fixed",
        "variable": "variable",
        "name": "Name",
        "assigned_schedule": "Assigned schedule (as HH:MM-hh:mm,[HH:MM-hh:mm,...] in 24hr format)",
        "advanced_options": "Advanced options",
        "penalties": "Penalties",
        "min_weekly_ts": "Min weekly time units",
        "max_weekly_ts": "Max weekly time units",
        "utility": "Utility (constant)",
        "min_adj": "Min adjacent time units",
        "max_adj": "Max adjacent time units",
        "configure_pw_util": "Configure piecewise daily utility",
        "allowed_window": "Allowed window (as HH:MM-hh:mm,[HH:MM-hh:mm,...] in 24hr format)",
        "confirm": "Confirm",
        "cancel": "Cancel",
    },
    "es": {
        "language": "Idioma",
        "time_unit": "Unidad de tiempo/Tamaño de ranura",
        "one_hour": "1 hora",
        "thirty_min": "30 minutos",
        "fifteen_min": "15 minutos",
        "activities": "Actividades",
        "add": "Agregar",
        "edit": "Editar",
        "solve": "RESOLVER",
        "type": "Tipo",
        "fixed": "fija",
        "variable": "variable",
        "name": "Nombre",
        "assigned_schedule": "Horario asignado (como HH:MM-hh:mm,[HH:MM-hh:mm,...] en formato 24hrs)",
        "advanced_options": "Opciones avanzadas",
        "penalties": "Penalizaciones",
        "min_weekly_ts": "Mín unidades de tiempo semanales",
        "max_weekly_ts": "Máx unidades de tiempo semanales",
        "utility": "Utilidad (constante)",
        "min_adj": "Mín unidades de tiempo adyacentes",
        "max_adj": "Máx unidades de tiempo adyacentes",
        "configure_pw_util": "Configurar utilidad diaria por partes",
        "allowed_window": "Ventana permitida (como HH:MM-hh:mm,[HH:MM-hh:mm,...] en formato 24hrs)",
        "confirm": "Confirmar",
        "cancel": "Cancelar",
    }
}


# Global state
current_lang = "en"
number_of_ts = 168
Test = True
if Test:
    fac1 = fixedActivity("fac1", [1, 24, 48], {})
    fac2 = fixedActivity("fac2", list(range(1, 169)), {fac1: "5"})
    fac3 = fixedActivity("fac3", [], {})
    vac1 = variableActivity(
        "vac1",
        [dailyUtility([1, 24], [3, 6]) for _ in range(7)],
        5, 20,
        list(range(1, 169)),
        1, 10,
        {}
    )
    vac2 = variableActivity(
        "vac2",
        [dailyUtility([], []) for _ in range(7)],
        0, 0,
        [],
        0, 0,
        {}
    )
    vac3 = variableActivity(
        "vac3",
        [
            dailyUtility([10, 15, 20], [100, 50, 0]) if day < 3
            else dailyUtility([5, 10], [20, 10])
            for day in range(7)
        ],
        12, 36,
        [2, 3, 4, 10, 11, 12, 50],
        2, 8,
        {fac1: "2", fac2: "10"}
    )
    vac4 = variableActivity(
        "vac4_invalid",
        [dailyUtility([], []) for _ in range(7)],
        50, 10,
        [1, 2, 3],
        1, 2,
        {}
    )
    vac5 = variableActivity(
        "vac5_fragmented",
        [dailyUtility([5], [25]) for _ in range(7)],
        10, 10,
        [i for i in range(1, 169) if i % 10 == 0],
        1, 1,
        {}
    )

activities: list = [fac1,fac2,fac3,vac1,vac2,vac3,vac4,vac5] if Test else []
selected_index: int = -1
daydic = {1:"mon", 2:"tue", 3:"wed", 4:"thu", 5:"fri", 6:"sat", 7:"sun"} if current_lang=="en" else {1:"lun", 2:"mar", 3:"mié", 4:"jue", 5:"vie", 6:"sáb", 7:"dom"}

# UI references for enabling/disabling
lang_dd = None
tu_dd = None
activities_table = None
add_btn = None
edit_btn = None
solve_btn = None


# ─────────────────────────────────────────────────────────────────────────────
def GUI(page: ft.Page):
    global lang_dd, tu_dd, activities_table, add_btn, edit_btn, solve_btn

    page.title = "Scheduler"
    page.window_width = 1200
    page.window_height = 800
    page.scroll = ft.ScrollMode.ADAPTIVE
    page._form_inputs = {}

    # --- Top controls --------------------------------------------------------
    lang_dd = ft.Dropdown(
        options=[ft.dropdown.Option("en"), ft.dropdown.Option("es")],
        value=current_lang,
        on_change=on_language_change,
        alignment=ft.alignment.top_right,
    )
    tu_dd = ft.Dropdown(
        options=[
            ft.dropdown.Option(dicts[current_lang]["one_hour"]),
            ft.dropdown.Option(dicts[current_lang]["thirty_min"]),
            ft.dropdown.Option(dicts[current_lang]["fifteen_min"]),
        ],
        value=dicts[current_lang]["one_hour"],
        on_change=on_time_unit_change,
        alignment=ft.alignment.top_left,
    )
    top_row = ft.Row([tu_dd, ft.Container(expand=1), lang_dd], height=50)

    # --- Activities table ---------------------------------------------------
    activities_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text(dicts[current_lang]["name"],size=15)),
            ft.DataColumn(ft.Text(dicts[current_lang]["type"],size=15))
        ],
        rows=[],
        width=400,
    )
    refresh_activities(page)

    add_btn = ft.ElevatedButton(dicts[current_lang]["add"], on_click=open_add_dialog)
    edit_btn = ft.ElevatedButton(dicts[current_lang]["edit"], on_click=open_edit_dialog, disabled=True)
    solve_btn = ft.ElevatedButton(
        dicts[current_lang]["solve"],
        on_click=lambda e: print("solving"),
        bgcolor=ft.Colors.PINK_ACCENT_200,
        expand=True
    )

    # --- Info panel (new!) --------------------------------------------------
    selected_info_panel = ft.Column([], visible=False, scroll="auto",expand=True)

    # --- Left column: activities + info -------------------------------------
    activities_column = ft.Column([
        ft.Row([
        ft.Container(
            content=ft.Text(dicts[current_lang]["activities"],
                            size=20, text_align=ft.TextAlign.CENTER, weight=ft.FontWeight.BOLD),
            expand=True
        )]),
        ft.Row([ft.Container(
            content=ft.Column([activities_table], scroll="auto", expand=True),
            height=400,
            bgcolor=ft.Colors.GREY_700,
            padding=5,
            border_radius=10, 
            expand=True,
        )]),
        ft.Row([add_btn, edit_btn]),
    ], expand=True)

    activities_panel = ft.Row([ft.Container(
        content=ft.Row([activities_column]),
        bgcolor=ft.Colors.GREY_900,
        padding=20,
        expand=True,
        border_radius=10, border=ft.border.all(3, ft.Colors.INDIGO_700)
    )])

    right_panel = ft.Container(expand=1)

    # --- Assemble page ------------------------------------------------------
    body = ft.Column([
        top_row,
        ft.Row([
            ft.Column([activities_panel, 
                        ft.Row([ft.Container(content=solve_btn, expand=True)]),
                        ft.Row([ft.Container(selected_info_panel, margin=ft.margin.only(top=10), padding=5,border=ft.border.all(1, ft.Colors.BLUE_200), border_radius=5,expand=True)])],
                        width=400),
            right_panel
        ], expand=True),
    ], expand=True)

    page.selected_info_panel = selected_info_panel

    page.add(body)

# ─────────────────────────────────────────────────────────────────────────────
def on_language_change(e: ft.ControlEvent):
    global current_lang
    global daydic
    current_lang = e.control.value
    daydic = {1:"mon", 2:"tue", 3:"wed", 4:"thu", 5:"fri", 6:"sat", 7:"sun"} if current_lang=="en" else {1:"lun", 2:"mar", 3:"mié", 4:"jue", 5:"vie", 6:"sáb", 7:"dom"}
    e.page.controls.clear()
    GUI(e.page)
    e.page.update()

def on_time_unit_change(e: ft.ControlEvent):
    global number_of_ts
    val = e.control.value
    if val == dicts[current_lang]["one_hour"]:
        number_of_ts = 168
    elif val == dicts[current_lang]["thirty_min"]:
        number_of_ts = 336
    else:
        number_of_ts = 672
    e.page.update()

# ─────────────────────────────────────────────────────────────────────────────
def refresh_activities(page):
    global activities_table
    activities_table.rows.clear()
    for idx, act in enumerate(activities):
        activities_table.rows.append(
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(act.name)),
                    ft.DataCell(ft.Text(dicts[current_lang][
                        "fixed" if isinstance(act, fixedActivity) else "variable"
                    ]))
                ],
                selected=False,
                on_select_changed=lambda e, i=idx: select_activity(i, page)
            )
        )
    page.update()

def select_activity(index: int, page: ft.Page):
    global selected_index, edit_btn
    selected_index = index
    edit_btn.disabled = False

    # toggle row highlighting
    for i, row in enumerate(activities_table.rows):
        row.selected = (i == index)

    # build & show the info panel
    act = activities[index]
    fields = build_activity_info(act)
    panel: ft.Column = page.selected_info_panel
    panel.controls = fields
    panel.visible = True

    page.update()

# ─────────────────────────────────────────────────────────────────────────────
def build_activity_info(act):
    """Turn a fixedActivity or variableActivity into a list of Text controls."""
    info = []
    info.append(ft.Text(f"Name: {act.name}", weight=ft.FontWeight.BOLD))
    typ = "Fixed" if isinstance(act, fixedActivity) else "Variable"
    info.append(ft.Text(f"Type: {typ}"))

    def daydic_to_strarray(dic,minus_one=False):
        print("=================================================" \
        +str(dic)+
        "================================================")
        return [
            f"{daydic[d].capitalize()}: {dic[d-1] if minus_one else (dic[daydic[d].capitalize()] if daydic[d].capitalize() in dic else None)}"
            for d in range(1, len(dic)+1)
        ]


    if isinstance(act, fixedActivity):
        sched = inverse_parse_window(act.assigned_ts, number_of_ts)
        schedule_str = "\n".join(
            daydic_to_strarray(sched)
        )
        info.append(
            ft.Text(f"Assigned schedule:\n{schedule_str}")
        )        
    else:
        info.append(ft.Text(f"Min weekly: {act.min_ts}"))
        info.append(ft.Text(f"Max weekly: {act.max_ts}"))
        info.append(ft.Text(f"Min adjacent: {act.min_adjacent_ts}"))
        info.append(ft.Text(f"Max adjacent: {act.max_adjacent_ts}"))

        allowed_str = "\n".join(
            daydic_to_strarray(
                inverse_parse_window(act.allowed_ts, number_of_ts)
            )
        )
        info.append(
            ft.Text(f"Allowed window:\n{allowed_str}")
        )        
        utility_str = "\n".join(
            daydic_to_strarray(act.utility,minus_one=True)
        )
        info.append(
            ft.Text(f"Utility:\n{utility_str}")
        )        

    # Penalties
    if getattr(act, "penalties", None):
        info.append(ft.Text("Penalties:\n"))
        for a in act.penalties:
            info.append(ft.Text(f"{(a.name+': '+act.penalties[a])}"))
            info.append(ft.Text("\n"))


    return info

# ─────────────────────────────────────────────────────────────────────────────


def open_add_dialog(e: ft.ControlEvent):
    page = e.page
    form_stack, controls = build_activity_form(page, None)

    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text(f"{dicts[current_lang]['add']} Activity"),
        content=ft.Container(form_stack, width=600),
        actions=[
            ft.TextButton(dicts[current_lang]["cancel"], on_click=close_dialog),
            ft.TextButton(dicts[current_lang]["confirm"], on_click=lambda ev: confirm_add_edit(dlg)),
        ]
    )
    # add dialog action buttons to controls list
    controls.extend(dlg.actions)

    page.dialog = dlg
    page.open(dlg)
    page.update()

def open_edit_dialog(e: ft.ControlEvent):
    page = e.page
    form_stack, controls = build_activity_form(page, activities[selected_index])

    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text(f"{dicts[current_lang]['edit']} Activity"),
        content=ft.Container(form_stack, width=600),
        actions=[
            ft.TextButton(dicts[current_lang]["cancel"], on_click=close_dialog),
            ft.TextButton(dicts[current_lang]["confirm"], on_click=lambda ev: confirm_add_edit(dlg, True)),
        ]
    )
    controls.extend(dlg.actions)

    page.dialog = dlg
    page.open(dlg)
    page.update()


def close_dialog(e: ft.ControlEvent):
    page = e.page
    page.close(page.dialog)
    page.update()


def parse_window(num_slots, entries_dict):
        slots_per_day = num_slots // 7
        slot_minutes = (7*24*60) // num_slots
        idxs = []
        for day, entry in entries_dict.items():
            raw = entry.value.strip()
            if not raw: continue
            for period in raw.split(','):
                try:
                    start, end = period.split('-')
                    h1,m1 = map(int, start.split(':'))
                    h2,m2 = map(int, end.split(':'))
                except ValueError:
                    continue
                s_min = h1*60 + m1; e_min = h2*60 + m2
                s_idx = (day-1)*slots_per_day + s_min // slot_minutes
                e_idx = (day-1)*slots_per_day + e_min // slot_minutes
                idxs += list(range(s_idx, e_idx+1))
        return sorted(set(idxs))

def inverse_parse_window(indices, num_slots):
    slots_per_day = num_slots // 7
    minutes_per_slot = (24 * 60) // slots_per_day  # minutes per slot

    # Bucket indices by day
    days = {d: [] for d in range(1, 8)}
    for idx in sorted(indices):
        if 1 <= idx <= num_slots:
            day = (idx - 1) // slots_per_day + 1
            days[day].append(idx)

    def slot_to_minutes_in_day(slot_idx):
        # slot position within its day (0-based)
        slot_in_day = (slot_idx - 1) % slots_per_day
        start_min = slot_in_day * minutes_per_slot
        end_min = start_min + minutes_per_slot - 1
        return start_min, end_min

    def minutes_to_str(m):
        h, mm = divmod(m, 60)
        return f"{h:02d}:{mm:02d}"

    schedule = {}
    for day, idxs in days.items():
        if not idxs:
            continue
        # Group into contiguous runs
        runs = []
        run_start = prev = idxs[0]
        for curr in idxs[1:]:
            if curr == prev + 1:
                prev = curr
            else:
                runs.append((run_start, prev))
                run_start = prev = curr
        runs.append((run_start, prev))

        # Format each run into "HH:MM-HH:MM"
        parts = []
        for s, e in runs:
            s_min, _ = slot_to_minutes_in_day(s)
            _, e_min = slot_to_minutes_in_day(e)
            parts.append(f"{minutes_to_str(s_min)}-{minutes_to_str(e_min)}")

        schedule[daydic[day].capitalize()] = ",".join(parts)

    return schedule





def build_activity_form(page, act=None):
    # --- 1) Compute initial values ---
    init_type    = "fixed" if not act or isinstance(act, fixedActivity) else "variable"
    init_name    = act.name if act else ""
    init_sched   = {} if not act or isinstance(act, variableActivity) else inverse_parse_window(act.assigned_ts, number_of_ts)
    init_pen     = act.penalties.copy() if act else {}
    init_min     = 0 if not act or isinstance(act, fixedActivity) else act.min_ts
    init_max     = number_of_ts if not act or isinstance(act, fixedActivity) else act.max_ts
    init_util_cte= act.util_cte if act and hasattr(act, "util_cte") else 0
    init_adj_min = 1 if not act or isinstance(act, fixedActivity) else act.min_adjacent_ts
    init_adj_max = number_of_ts if not act or isinstance(act, fixedActivity) else act.max_adjacent_ts
    init_util    = act.utility if act and hasattr(act, "utility") else []
    init_win     = inverse_parse_window(act.allowed_ts,number_of_ts) if act and hasattr(act, "allowed_ts") else {}

    # --- 2) Build all form controls ---
    type_dd      = ft.Dropdown(
        label=dicts[current_lang]["type"],
        options=[
            ft.dropdown.Option(dicts[current_lang]["fixed"], data="fixed"),
            ft.dropdown.Option(dicts[current_lang]["variable"], data="variable")
        ],
        value=init_type
    )
    name_tf      = ft.TextField(label=dicts[current_lang]["name"], value=init_name)
    sched_fields = {
        d: ft.TextField(label=daydic[d].capitalize(), value=init_sched.get(d, ""))
        for d in range(1,8)
    }
    var_min      = ft.TextField(label=dicts[current_lang]["min_weekly_ts"], value=str(init_min))
    var_max      = ft.TextField(label=dicts[current_lang]["max_weekly_ts"], value=str(init_max))
    util_tf      = ft.TextField(label=dicts[current_lang]["utility"], value=str(init_util_cte))
    var_adj_min  = ft.TextField(label=dicts[current_lang]["min_adj"], value=str(init_adj_min))
    var_adj_max  = ft.TextField(label=dicts[current_lang]["max_adj"], value=str(init_adj_max))
    win_fields   = {
        d: ft.TextField(label=daydic[d].capitalize(), value=init_win[d] if d in init_win else "")
        for d in range(1,8)
    }
    penalties_fixed = {
        a: ft.TextField(label=a.name, value=str(init_pen[a] if a in init_pen else ""))
        for a in activities
    }
    penalties_var   = {
        a: ft.TextField(label=a.name, value=str(init_pen[a] if a in init_pen else ""))
        for a in activities
    }

    # --- 3) Panels (initially hidden) ---
    sched_panel = ft.Column(
        [ft.Text(dicts[current_lang]["assigned_schedule"])] +
        list(sched_fields.values()),
        visible=False
    )
    fix_adv = ft.Column(
        [ft.Text(dicts[current_lang]["penalties"])] +
        list(penalties_fixed.values()),
        visible=False
    )
    var_adv = ft.Column(
        [
            var_adj_min, var_adj_max,
            ft.ElevatedButton(dicts[current_lang]["configure_pw_util"], on_click=lambda e: open_pw_panel()),
            ft.Text(dicts[current_lang]["allowed_window"]),
            *list(win_fields.values()),
            ft.Text(dicts[current_lang]["penalties"]),
            *list(penalties_var.values())
        ],
        visible=False
    )

    # --- 4) Piecewise panel (overlay) ---
    field_width=100
    slot_max = number_of_ts // 7

    # Data structures to hold per-day rows
    day_rows = {d: [] for d in range(1, 8)}
    day_columns = {}  # will hold ft.Column for each day

    def rebuild_day_column(day):
        """Rebuild the ft.Column for a given day from its rows."""
        col = ft.Column([ft.Text(daydic[day].capitalize(), weight=ft.FontWeight.BOLD)], spacing=10)
        for idx, (from_tf, to_tf, util_tf) in enumerate(day_rows[day]):
            col.controls.append(
                ft.Row([from_tf, to_tf, util_tf], spacing=10)
            )
        return col

    def on_to_change(day, row_idx):
        def handler(e):
            # parse the new "To" input
            try:
                v = int(e.control.value)
            except:
                v = slot_max
            # clamp to (from + 1) … slot_max
            from_val = int(day_rows[day][row_idx][0].value)
            v = max(v, from_val + 1)
            v = min(v, slot_max)
            e.control.value = str(v)

            # clear and remove any rows after this one
            rows = day_rows[day]
            for f_tf, t_tf, u_tf in rows[row_idx+1:]:
                f_tf.value = ""
                t_tf.value = str(slot_max)
                u_tf.value = ""
            del rows[row_idx+1:]

            # if we’re below the maximum, append a new row
            if v < slot_max:
                new_from = v
                f = ft.TextField(label="From", value=str(new_from), disabled=True, width=field_width)
                t = ft.TextField(
                    label="To",
                    value=str(slot_max),
                    on_change=on_to_change(day, len(rows)), width=field_width
                )
                u = ft.TextField(label="Utility", width=field_width)
                rows.append((f, t, u))

            # rebuild UI
            day_columns[day].controls = rebuild_day_column(day).controls
            page.update()
        return handler


    # Initialize one row per day
    for d in range(1, 8):
        f = ft.TextField(label="From", value="0", disabled=True, width=field_width)
        t = ft.TextField(
            label="To", 
            value=str(slot_max),
            on_change=on_to_change(d, 0), width=field_width
        )
        u = ft.TextField(label="Utility", width=field_width)
        day_rows[d].append((f, t, u))
        # build initial column
        day_columns[d] = rebuild_day_column(d)

    # Buttons
    pw_cancel = ft.ElevatedButton(dicts[current_lang]["cancel"], on_click=lambda e: close_pw_panel())
    def on_pw_confirm(e):
        has_something = False
        new_util = []
        for d in range(1, 8):
            rows = day_rows[d]
            to_vals = []
            util_vals = []
            for from_tf, to_tf, util in rows:
                # parse and skip empty utilities
                try:
                    t = int(to_tf.value)
                    has_something = True
                except:
                    continue
                try:
                    u = float(util.value)
                except:
                    u = 0.0
                to_vals.append(t)
                util_vals.append(u)
            new_util.append(dailyUtility(to_vals, util_vals))
        page._form_inputs["utility"] = new_util
        nonlocal util_tf
        if has_something:
            util_tf.disabled = True
            util_tf.value = 0
        close_pw_panel()

    pw_confirm = ft.ElevatedButton(
        dicts[current_lang]["confirm"],
        on_click=on_pw_confirm
    )

    # Actual pw_panel
    pw_panel = ft.Container(
        visible=False,
        content=ft.Card(
            content=ft.Container(
                ft.Column(
                    [
                        # arrange the seven day columns in a grid or list:
                        *[day_columns[d] for d in range(1, 8)],
                        ft.Row([pw_cancel, pw_confirm], alignment=ft.MainAxisAlignment.END)
                    ],
                    scroll="auto",
                    spacing=20
                ),
                padding=20
            ),
            width=400
        )
    )

    # --- 5) Collect *only* form controls to disable ---
    form_controls = [
        type_dd, name_tf,
        *sched_fields.values(),
        var_min, var_max, util_tf,
        var_adj_min, var_adj_max,
        *win_fields.values(),
        *penalties_fixed.values(),
        *penalties_var.values(),
    ]

    # --- 6) open/close functions for pw_panel ---
    def open_pw_panel():
        pw_panel.visible = True
        for c in form_controls:
            c.disabled = True
        page.update()

    def close_pw_panel():
        pw_panel.visible = False
        for c in form_controls:
            c.disabled = False
        page.update()


    # --- 7) Advanced‐options toggle button ---
    adv_btn = ft.ElevatedButton(
        dicts[current_lang]["advanced_options"],
        on_click=lambda e: (
            fix_adv.__setattr__("visible", (type_dd.value == "fixed") & (not fix_adv.visible)),
            var_adv.__setattr__("visible", (type_dd.value != "fixed") & (not var_adv.visible)),
            page.update()
        )
    )

    # --- 8) Type‐change logic to switch base panels ---
    def on_type_change(e):
        fixed = (type_dd.value == "fixed")
        sched_panel.visible = fixed
        fix_adv.visible    = False
        var_min.visible    = not fixed
        var_max.visible    = not fixed
        util_tf.visible    = not fixed
        var_adv.visible    = False
        page.update()
    type_dd.on_change = on_type_change
    on_type_change(None)  # initialize

    # --- 9) Assemble form_body + return with pw_panel overlay ---
    form_body = ft.Column([
        ft.Container(height=5),
        type_dd, name_tf,
        sched_panel,
        var_min, var_max, util_tf,
        adv_btn,
        fix_adv, var_adv
    ], scroll="auto", expand=True)

    # Save for confirm_add_edit
    page._form_inputs = {
        "type_dd": type_dd,
        "name_tf": name_tf,
        "sched_fields": sched_fields,
        "var_min": var_min,
        "var_max": var_max,
        "util_tf": util_tf,
        "var_adj_min": var_adj_min,
        "var_adj_max": var_adj_max,
        "penalties_fixed": penalties_fixed,
        "penalties_var": penalties_var,
        "win_fields": win_fields,
        "utility": page._form_inputs["utility"] if page._form_inputs else [None]*7
    }

    return ft.Stack([form_body, pw_panel]), form_controls


def confirm_add_edit(dlg: ft.AlertDialog, edit=False):
    page = dlg.page
    f = page._form_inputs
    name = f["name_tf"].value.strip()
    if f["type_dd"].value == "fixed":
        assigned = parse_window(number_of_ts, f["sched_fields"])
        penalties = {a: float(f["penalties_fixed"][a].value) for a in f["penalties_fixed"] if f["penalties_fixed"][a].value.strip()}
        new_act = fixedActivity(name, penalties, assigned)
    else:
        min_ts = int(f["var_min"].value)
        max_ts = int(f["var_max"].value)
        util_cte = float(f["util_tf"].value)
        min_adj = int(f["var_adj_min"].value)
        max_adj = int(f["var_adj_max"].value)
        penalties = {a: float(f["penalties_var"][a].value) for a in f["penalties_var"] if f["penalties_var"][a].value.strip()}
        win = parse_window(number_of_ts,f["win_fields"])
        if util_cte!=0:
            cteUtil = {day:dailyUtility([number_of_ts/7],[util_cte]) for day in range(1,8)} 
            new_act = variableActivity(name,cteUtil, min_ts, max_ts,win, min_adj, max_adj, penalties)
        else:
            new_act = variableActivity(name,f["utility"], min_ts, max_ts,win, min_adj, max_adj, penalties)
        

    if edit:
        activities[selected_index] = new_act
    else:
        activities.append(new_act)


    refresh_activities(page)
    page.close(dlg)
    page.update()


def toggle_panel(panel: ft.Control):
    panel.visible = not panel.visible
    panel.page.update()



if __name__=="__main__":
    while(True):
        if(input("1. parse_window (hh:mm...)\n2. inverse parse window ([1,2,67...])\n")=="1"):
            print(parse_window(input("parse_window:\n"),168))
        else:
            print(inverse_parse_window(literal_eval(input("inverse_parse_window:\n")),168))
