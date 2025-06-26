import flet as ft
from math import floor
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
        "delete": "Delete",
        "info":"Activity data",
        "activity":"activity",
        "add": "Add",
        "edit": "Edit",
        "solve": "SOLVE",
        "type": "Type",
        "fixed": "fixed",
        "variable": "variable",
        "name": "Name",
        "assigned_schedule": "Assigned schedule",
        "advanced_options": "Advanced options",
        "penalties": "Penalties",
        "min_weekly_ts": "Min weekly time units",
        "max_weekly_ts": "Max weekly time units",
        "utility": "Utility (constant)",
        "pw_utility": "Daily piecewise utility",
        "min_adj": "Min adjacent time units",
        "max_adj": "Max adjacent time units",
        "configure_pw_util": "Configure piecewise daily utility",
        "allowed_window": "Allowed window",
        "hr_format_tooltip":"(as HH:MM-hh:mm,[HH:MM-hh:mm,...] in 24hr format)",
        "confirm": "Confirm",
        "cancel": "Cancel",
        "from": "From",
        "to": "To",
        "piece_utility": "Utility"
    },
    "es": {
        "language": "Idioma",
        "time_unit": "Unidad de tiempo/Tamaño de ranura",
        "one_hour": "1 hora",
        "thirty_min": "30 minutos",
        "fifteen_min": "15 minutos",
        "activities": "Actividades",
        "info": "Datos de actividad",
        "activity":"activity",
        "delete": "Eliminar",
        "add": "Agregar",
        "edit": "Editar",
        "solve": "RESOLVER",
        "type": "Tipo",
        "fixed": "fija",
        "variable": "variable",
        "name": "Nombre",
        "assigned_schedule": "Horario asignado",
        "advanced_options": "Opciones avanzadas",
        "penalties": "Penalizaciones",
        "min_weekly_ts": "Mín unidades de tiempo semanales",
        "max_weekly_ts": "Máx unidades de tiempo semanales",
        "utility": "Utilidad (constante)",
        "pw_utility": "Utilidad diaria escalonada",
        "min_adj": "Mín unidades de tiempo adyacentes",
        "max_adj": "Máx unidades de tiempo adyacentes",
        "configure_pw_util": "Configurar utilidad diaria por partes",
        "allowed_window": "Ventana permitida",
        "hr_format_tooltip":"(como HH:MM-hh:mm,[HH:MM-hh:mm,...] en formato 24hrs)",
        "confirm": "Confirmar",
        "cancel": "Cancelar",
        "from": "Desde",
        "to": "Hasta",
        "piece_utility": "Utilidad"
    }
}

# solver
pl = None

# Global state
current_lang = "en"
number_of_ts = 168
Test = True
if Test:
    fac1 = fixedActivity("fac2", list(range(1, 169)),{})
    vac1 = variableActivity(
        "vac1",
        [dailyUtility([1, 24], [3, 6]) for _ in range(7)],
        5, 20,
        list(range(1, 169)),
        1, 10,
        {}
    )
    vac2 = variableActivity(
        "vac_fragmented",
        [dailyUtility([5], [25]) for _ in range(7)],
        10, 10,
        [i for i in range(1, 169) if i % 10 == 0],
        1, 1,
        {}
    )

schedule_array = []
activities: list = [fac1,vac1,vac2] if Test else []
selected_index: int = -1
daydic = {1:"mon", 2:"tue", 3:"wed", 4:"thu", 5:"fri", 6:"sat", 7:"sun"} if current_lang=="en" else {1:"lun", 2:"mar", 3:"mié", 4:"jue", 5:"vie", 6:"sáb", 7:"dom"}

# UI references for enabling/disabling
lang_dd = None
tu_dd = None
activities_table = None
add_btn = None
edit_btn = None
delete_btn = None
solve_btn = None


# ─────────────────────────────────────────────────────────────────────────────
def GUI(page: ft.Page):
    global lang_dd, tu_dd, activities_table, add_btn, edit_btn, solve_btn, delete_btn

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
    tu_dd = ft.Row([ft.Text(dicts[current_lang]["time_unit"]+":"),ft.Dropdown(
        options=[
            ft.dropdown.Option(dicts[current_lang]["one_hour"]),
            ft.dropdown.Option(dicts[current_lang]["thirty_min"]),
            ft.dropdown.Option(dicts[current_lang]["fifteen_min"]),
        ],
        value=dicts[current_lang]["one_hour"],
        on_change=on_time_unit_change,
        alignment=ft.alignment.top_left,)])
    top_row = ft.Row(
        [
            tu_dd,
            ft.Container(
                expand=1,
                content=ft.Row(
                    [
                        ft.Text("Week", size=80, color=ft.Colors.RED_400,   weight=ft.FontWeight.BOLD),
                        ft.Text("LINQ", size=80, color=ft.Colors.LIGHT_GREEN_400, weight=ft.FontWeight.BOLD),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    expand=True, 
                )
            ),
            lang_dd,
        ],
        height=100,
        vertical_alignment=ft.CrossAxisAlignment.END
    )

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
    delete_btn = ft.ElevatedButton(dicts[current_lang]["delete"], on_click=delete_selected, disabled=True)
    solve_btn = ft.ElevatedButton(
        dicts[current_lang]["solve"],
        on_click=on_solve,
        bgcolor=ft.Colors.LIGHT_GREEN_400,
        expand=True, color=ft.Colors.LIGHT_GREEN_900
    )

    # --- Info panel (new!) --------------------------------------------------
    selected_info_panel = ft.Column([], visible=False, scroll="auto",expand=True)

    # --- Left column: activities + info -------------------------------------
    activities_column = ft.Column([
        ft.Row([
        ft.Container(
            content=ft.Text(dicts[current_lang]["activities"],
                            size=25, text_align=ft.TextAlign.CENTER, weight=ft.FontWeight.BOLD),
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
        ft.Row([add_btn, edit_btn, delete_btn]),
    ], expand=True)

    activities_panel = ft.Row([ft.Container(
        content=ft.Row([activities_column]),
        bgcolor=ft.Colors.GREY_900,
        padding=20,
        expand=True,
        border_radius=10, border=ft.border.all(3, ft.Colors.RED_400)
    )])

    #---Scheduler-------------------------------------------------------------
    hourows=[]
    for r in range(24):
        hourows.append(ft.DataRow([ft.DataCell(ft.Text(f"{r:02d}:00hrs-{(r):02d}:59hrs",size=12))]))
    hour_table = ft.DataTable(
        columns=[ft.DataColumn(ft.Text(" ",weight=ft.FontWeight.BOLD,size=16))],
        rows=hourows,
        data_row_min_height=1020/24,
        data_row_max_height=1020/24,
        show_checkbox_column=False,
        expand=False
    )

    def build_schedule_panel(schedule_array):

        # number_of_ts is a global
        rows_per_col = number_of_ts // 7
        # Column labels
        days = [daydic[d].capitalize() for d in range(1, 8)]

        # Build DataTable columns
        cols = [ft.DataColumn(ft.Text(label,weight=ft.FontWeight.BOLD,size=16)) for label in days]

        # Build DataRows
        rows = []
        for r in range(rows_per_col):
            cells = []
            for c in range(7):
                idx = c * rows_per_col + r  # zero‐based into schedule_array
                name = schedule_array[idx] if idx < len(schedule_array) else None
                cells.append(ft.DataCell(ft.Text(name or "", size=10)))
            rows.append(ft.DataRow(cells=cells))

        table = ft.DataTable(
            columns=cols,
            rows=rows,
            show_checkbox_column=False,
            expand=True,
            data_row_min_height=1020/rows_per_col,
            data_row_max_height=1020/rows_per_col
        )

        panel = ft.Container(
            content=ft.Row([hour_table,table]), expand=True,
            height=1090,  
            padding=10,
            border=ft.border.all(3, ft.Colors.LIGHT_GREEN_400), border_radius=10
        )
        return panel
    
    page.build_schedule_panel = build_schedule_panel



    page.schedule_container = ft.Container(
        expand=1,
        padding=0,
        content=page.build_schedule_panel(schedule_array)
    )
    right_panel = page.schedule_container

    # --- Assemble page ------------------------------------------------------
    body = ft.Column([
        top_row,
        ft.Row([
            ft.Container(ft.Column([activities_panel, 
                        ft.Row([ft.Container(content=solve_btn, expand=True)]),
                        ft.Row([ft.Container(ft.Column([ft.Row([ft.Container(ft.Text(dicts[current_lang]["info"],size=20, text_align=ft.TextAlign.CENTER, weight=ft.FontWeight.BOLD),expand=True)]),selected_info_panel]), margin=ft.margin.only(top=10), padding=5,border=ft.border.all(1, ft.Colors.BLUE_200), border_radius=5,expand=True, height=496)])],
                        width=400), expand=False, padding=15),
            ft.Container(right_panel,expand=1,padding=15)
        ], expand=True, vertical_alignment=ft.CrossAxisAlignment.START),
    ], expand=True)

    page.selected_info_panel = selected_info_panel

    page.solve_overlay = ft.Container(
        expand=True,
        bgcolor=ft.Colors.with_opacity(0.5,ft.Colors.BLACK),
        content=ft.Column(
            [ft.Text("Solving...", size=30, color=ft.Colors.WHITE)],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        visible=False,
    )
    page.overlay.append(page.solve_overlay)

    page.add(body)

# ─────────────────────────────────────────────────────────────────────────────

def on_solve(e: ft.ControlEvent):
    global pl, schedule_array
    # gather activities & create planner
    fixedActs = [a for a in activities if isinstance(a, fixedActivity)]
    varActs   = [a for a in activities if isinstance(a, variableActivity)]
    pl = planner(fixedActs, varActs, number_of_ts)

    page = e.page
    # show overlay
    page.solve_overlay.visible = True
    page.update()

    result = pl.solve()  # returns (utility, schedule_array) or None

    # hide overlay
    page.solve_overlay.visible = False

    if result:
        _, new_sched = result
        schedule_array = new_sched
        # rebuild right panel
        page.schedule_container.content = page.build_schedule_panel(schedule_array)
    else:
        page.dialog = ft.AlertDialog(title=ft.Text("No solution found"))
        page.dialog.open = True

    page.update()




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

    page = e.page
    page.schedule_container.content = page.build_schedule_panel(schedule_array)

    if pl:
        on_solve() 

    page.update()

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
    global selected_index, edit_btn, delete_btn
    selected_index = index
    edit_btn.disabled = False
    delete_btn.disabled = False

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
    """Turn a fixedActivity or variableActivity into a list of Controls."""
    info: list[ft.Control] = []

    # Helper to generate day strings
    def daydic_to_strarray(dic, minus_one=False):
        lines = []
        for d in range(1, 8):
            day_label = daydic[d].capitalize()
            if minus_one:
                val = dic[d-1]
            else:
                val = dic.get(day_label, None) if isinstance(dic, dict) else None
            lines.append(f"{day_label}: {val}")
        return lines

    # 1) Name row
    info.append(
        ft.Row([
            ft.Text(f"{dicts[current_lang]['name']}:", weight=ft.FontWeight.BOLD),
            ft.Text(act.name)
        ], alignment=ft.MainAxisAlignment.START)
    )

    # 2) Type row
    typ = dicts[current_lang]["fixed"] if isinstance(act, fixedActivity) else dicts[current_lang]["variable"]
    info.append(
        ft.Row([
            ft.Text(f"{dicts[current_lang]['type']}:", weight=ft.FontWeight.BOLD),
            ft.Text(typ)
        ], alignment=ft.MainAxisAlignment.START)
    )

    # 3) Fixed vs Variable details
    if isinstance(act, fixedActivity):
        sched = inverse_parse_window(act.assigned_ts, number_of_ts)
        lines = daydic_to_strarray(sched)
        # header
        info.append(ft.Text(f"{dicts[current_lang]['assigned_schedule']}:", weight=ft.FontWeight.BOLD))
        # each day on its own line
        for ln in lines:
            info.append(ft.Text(ln))
    else:
        # min / max weekly
        for key, val in [
            ("min_weekly_ts", act.min_ts),
            ("max_weekly_ts", act.max_ts),
            ("min_adj", act.min_adjacent_ts),
            ("max_adj", act.max_adjacent_ts),
        ]:
            info.append(
                ft.Row([
                    ft.Text(f"{dicts[current_lang][key]}:", weight=ft.FontWeight.BOLD),
                    ft.Text(str(val))
                ], alignment=ft.MainAxisAlignment.START)
            )

        # allowed window
        allowed = inverse_parse_window(act.allowed_ts, number_of_ts)
        lines = daydic_to_strarray(allowed)
        info.append(ft.Text(f"{dicts[current_lang]['allowed_window']}:", weight=ft.FontWeight.BOLD))
        for ln in lines:
            info.append(ft.Text(ln))

        # piecewise utility
        util_lines = daydic_to_strarray(act.utility, minus_one=True)
        info.append(ft.Text(f"{dicts[current_lang]['pw_utility']}:", weight=ft.FontWeight.BOLD))
        for ln in util_lines:
            info.append(ft.Text(ln))

    # 4) Penalties (if any)
    if getattr(act, "penalties", None):
        info.append(ft.Text(f"{dicts[current_lang]['penalties']}:", weight=ft.FontWeight.BOLD))
        for other, pval in act.penalties.items():
            info.append(ft.Text(f"{other.name}: {pval}"))

    return info


# ─────────────────────────────────────────────────────────────────────────────
def delete_selected(e: ft.ControlEvent):
    global edit_btn, delete_btn, selected_index
    activities.pop(selected_index)
    edit_btn.disabled = True
    delete_btn.disabled = True
    refresh_activities(e.page)
    e.page.selected_info_panel.controls.clear()
    e.page.selected_info_panel.visible = False
    selected_index = -1
    # commit UI changes
    e.page.update()


def open_add_dialog(e: ft.ControlEvent):
    page = e.page
    form_stack, controls = build_activity_form(page, None)

    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text(f"{dicts[current_lang]['add']} {dicts[current_lang]['activity']}"),
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
        title=ft.Text(f"{dicts[current_lang]['edit']} {dicts[current_lang]['activity']}"),
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
        print(sorted(set(idxs)))
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
        [ft.Text(dicts[current_lang]["assigned_schedule"]), ft.Text(dicts[current_lang]["hr_format_tooltip"],size=10)] +
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
            ft.Text(dicts[current_lang]["allowed_window"]), ft.Text(dicts[current_lang]["hr_format_tooltip"],size=10),
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
                f = ft.TextField(label=dicts[current_lang]["from"], value=str(new_from), disabled=True, width=field_width)
                t = ft.TextField(
                    label=dicts[current_lang]["to"],
                    value=str(slot_max),
                    on_change=on_to_change(day, len(rows)), width=field_width
                )
                u = ft.TextField(label={dicts[current_lang]['piece_utility']}, width=field_width)
                rows.append((f, t, u))

            # rebuild UI
            day_columns[day].controls = rebuild_day_column(day).controls
            page.update()
        return handler


    # Initialize one row per day
    for d in range(1, 8):
        f = ft.TextField(label=dicts[current_lang]["from"], value="0", disabled=True, width=field_width)
        t = ft.TextField(
            label=dicts[current_lang]["to"], 
            value=str(slot_max),
            on_change=on_to_change(d, 0), width=field_width
        )
        u = ft.TextField(label=dicts[current_lang]["piece_utility"], width=field_width)
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
