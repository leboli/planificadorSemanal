import flet as ft
from entities.fixedActivity import fixedActivity
from entities.variableActivity import variableActivity
from entities.dailyUtility import dailyUtility

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
        "assigned_schedule": "Assigned schedule as HH:MM-hh:mm,[HH:MM-hh:mm,...] in 24hr format",
        "advanced_options": "Advanced options",
        "penalties": "Penalties",
        "min_weekly_ts": "Min weekly time units",
        "max_weekly_ts": "Max weekly time units",
        "utility": "Utility (constant)",
        "min_adj": "Min adjacent time units",
        "max_adj": "Max adjacent time units",
        "configure_pw_util": "Configure piecewise daily utility",
        "allowed_window": "Allowed window as HH:MM-hh:mm,[HH:MM-hh:mm,...] in 24hr format",
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
        "assigned_schedule": "Horario asignado como HH:MM-hh:mm,[HH:MM-hh:mm,...] en formato 24hrs",
        "advanced_options": "Opciones avanzadas",
        "penalties": "Penalizaciones",
        "min_weekly_ts": "Mín unidades de tiempo semanales",
        "max_weekly_ts": "Máx unidades de tiempo semanales",
        "utility": "Utilidad (constante)",
        "min_adj": "Mín unidades de tiempo adyacentes",
        "max_adj": "Máx unidades de tiempo adyacentes",
        "configure_pw_util": "Configurar utilidad diaria por partes",
        "allowed_window": "Ventana permitida como HH:MM-hh:mm,[HH:MM-hh:mm,...] en formato 24hrs",
        "confirm": "Confirmar",
        "cancel": "Cancelar",
    }
}
daydic = {1:"mon", 2:"tue", 3:"wed", 4:"thu", 5:"fri", 6:"sat", 7:"sun"}


# Global state
current_lang = "en"
number_of_ts = 168
activities: list = [variableActivity("aaaaa",0,0,700,[range(168)],1,45,{}),variableActivity("bbbbbbb",0,0,700,[range(168)],1,45,{}),fixedActivity("fixeeed",{},[range(31)])]
selected_index: int = -1

# UI references for enabling/disabling
lang_dd = None
tu_dd = None
activities_table = None
add_btn = None
edit_btn = None
solve_btn = None


def main(page: ft.Page):
    global lang_dd, tu_dd, activities_table, add_btn, edit_btn, solve_btn
    page.title = "Scheduler"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.window_width = 1000
    page.window_height = 700

    # Language dropdown
    lang_dd = ft.Dropdown(
        options=[ft.dropdown.Option("en"), ft.dropdown.Option("es")],
        value=current_lang,
        on_change=on_language_change,
        alignment=ft.alignment.top_right,
    )

    # Time unit dropdown
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

    # Top rows
    top_row = ft.Row([
        tu_dd,
        ft.Container(expand=1),
        lang_dd,
    ], height=50)

    # Activities panel
    activities_table = ft.DataTable(columns=[ft.DataColumn(ft.Text(dicts[current_lang]["name"]))], rows=[], width=580)
    refresh_activities(page=page)

    add_btn = ft.ElevatedButton(dicts[current_lang]["add"], on_click=open_add_dialog)
    edit_btn = ft.ElevatedButton(dicts[current_lang]["edit"], on_click=open_edit_dialog, disabled=True)
    solve_btn = ft.ElevatedButton(dicts[current_lang]["solve"], on_click=lambda e: print("solving"), bgcolor=ft.Colors.PINK_ACCENT_200, width=620)

    activities_column = ft.Column(
        [
            ft.Text(dicts[current_lang]["activities"]),
            ft.Container(
                content=activities_table,
                height=400,
                bgcolor=ft.Colors.GREY_700,
                padding=5,
            ),
            ft.Row([add_btn, edit_btn]),
        ],
        width=600, scroll="auto"
    )
    activities_panel = ft.Container(
        content=activities_column,
        bgcolor=ft.Colors.GREY_900,
        padding=10,
        expand=False,
        height=500
    )

    # Right panel placeholder
    right_panel = ft.Container(expand=1)

    # Layout
    body = ft.Column([
        top_row,
        ft.Row([ft.Column([activities_panel, solve_btn]), right_panel], expand=True),
    ], expand=True)

    page.add(body)


def on_language_change(e: ft.ControlEvent):
    global current_lang
    current_lang = e.control.value
    e.page.controls.clear()
    main(e.page)
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


def refresh_activities(page):
    global activities_table
    activities_table.rows.clear()
    for idx, act in enumerate(activities):
        activities_table.rows.append(
            ft.DataRow(
                cells=[ft.DataCell(ft.Text(act.name))],
                on_select_changed=lambda e, i=idx: select_activity(i,page),
                selected=False,
            )
        )


def select_activity(index: int, page):
    global selected_index
    selected_index = index
    edit_btn.disabled = False
    for i, row in enumerate(activities_table.rows):
        row.selected = (i == index)
    page.update()


def open_add_dialog(e: ft.ControlEvent):
    page = e.page
    def on_confirm(e): confirm_add_edit(dlg)
    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text(f"{dicts[current_lang]['add']} Activity"),
        content=ft.Container(build_activity_form(page, None, confirm_btn_ref := [], cancel_btn_ref := []), width=600),
        actions=[
            ft.TextButton(text=dicts[current_lang]["cancel"], on_click=close_dialog, ref=cancel_btn_ref),
            ft.TextButton(text=dicts[current_lang]["confirm"], on_click=on_confirm, ref=confirm_btn_ref),
        ],
    )
    page.dialog = dlg
    page.open(dlg)
    page.update()

def open_edit_dialog(e: ft.ControlEvent):
    page = e.page
    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text(f"{dicts[current_lang]['edit']} Activity"),
        content=build_activity_form(page,activities[selected_index]),
        actions=[
            ft.TextButton(text=dicts[current_lang]["cancel"], on_click=close_dialog),
            ft.TextButton(text=dicts[current_lang]["confirm"], on_click=close_dialog),
        ],
    )
    page.open(dlg)
    page.update()


def close_dialog(e: ft.ControlEvent):
    page = e.page
    page.close(page.dialog)
    page.update()


def parse_window(self, num_slots, entries_dict):
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
    minutes_per_slot = (7 * 24 * 60) // num_slots  # duración de cada franja en minutos
    result = {day: [] for day in range(1, 8)}  # 1=Lunes ... 7=Domingo

    for idx in indices:
        day = (idx // slots_per_day) + 1
        slot = idx % slots_per_day
        total_minutes = slot * minutes_per_slot
        hour = total_minutes // 60
        minute = total_minutes % 60
        result[day].append(f"{hour:02d}:{minute:02d}")

    return result



def build_activity_form(page, act=None, confirm_btn_ref=None, cancel_btn_ref=None):
    from entities.dailyUtility import dailyUtility

    init_type = "fixed" if not act or isinstance(act, fixedActivity) else "variable"
    init_name = act.name if act else ""
    init_schedules = {} if not act or isinstance(act, variableActivity) else inverse_parse_window(act.assigned_ts)
    init_penalties = act.penalties.copy() if act else {}
    init_min_ts = 0 if not act or isinstance(act, fixedActivity) else act.min_ts
    init_max_ts = number_of_ts if not act or isinstance(act, fixedActivity) else act.max_ts
    init_util_cte = act.util_cte if act and hasattr(act, "util_cte") else 0
    init_min_adj = 1 if not act or isinstance(act, fixedActivity) else act.min_adjacent_ts
    init_max_adj = number_of_ts if not act or isinstance(act, fixedActivity) else act.max_adjacent_ts
    util = act.utility if act and hasattr(act, "utility") else {}
    init_window = act.allowed_ts if act and hasattr(act, "allowed_ts") else {}

    segment_inputs = {}
    utility_inputs = {}

    def close_pw_panel(e=None):
        pw_panel.visible = False
        if confirm_btn_ref: confirm_btn_ref[0].disabled = False
        if cancel_btn_ref: cancel_btn_ref[0].disabled = False
        page.update()

    def confirm_pw_panel(e=None):
        try:
            new_util = {}
            for day in range(1, 8):
                seg_str = segment_inputs[day].value.strip()
                util_str = utility_inputs[day].value.strip()
                segments = [int(x.strip()) for x in seg_str.split(",") if x.strip()]
                utilities = [float(x.strip()) for x in util_str.split(",") if x.strip()]
                if len(segments) + 1 != len(utilities):
                    raise ValueError(f"Day {day}: mismatch between segments and utilities.")
                new_util[day] = dailyUtility(segments, utilities)
            nonlocal util
            util = new_util
            close_pw_panel()
        except Exception as err:
            page.dialog = ft.AlertDialog(title=ft.Text(str(err)))
            page.dialog.open = True
            page.update()

    pw_rows = []
    for day in range(1, 8):
        seg_tf = ft.TextField(label="Segment ends (e.g. 3,5,8)")
        util_tf = ft.TextField(label="Corresponding utilities (e.g. 2,4,1)")
        segment_inputs[day] = seg_tf
        utility_inputs[day] = util_tf
        pw_rows.append(ft.Column([ft.Text(daydic[day].capitalize(), weight="bold"), seg_tf, util_tf], spacing=5))

    pw_panel = ft.Container(
        visible=False, padding=20, alignment=ft.alignment.center,
        content=ft.Card(
            elevation=8,
            content=ft.Container(content=ft.Column([
                ft.Text("Configure piecewise utility", size=20, weight="bold"),
                *pw_rows,
                ft.Row([
                    ft.ElevatedButton("Cancel", on_click=close_pw_panel),
                    ft.ElevatedButton("Confirm", on_click=confirm_pw_panel),
                ], alignment=ft.MainAxisAlignment.END)
            ], tight=True, scroll="auto"), padding=15), width=1000
        )
    )

    sched_fields = {day: ft.TextField(label=daydic[day].capitalize(), value=init_schedules.get(day, "")) for day in range(1, 8)}
    sched_panel = ft.Column([ft.Text(dicts[current_lang]["assigned_schedule"])] + list(sched_fields.values()))
    penalties_fields_fixed = {a: ft.TextField(label=a.name, value=str(init_penalties.get(a, ""))) for a in activities}
    penalties_panel_fixed = ft.Column([ft.Text(dicts[current_lang]["penalties"])] + list(penalties_fields_fixed.values()))

    var_min = ft.TextField(label=dicts[current_lang]["min_weekly_ts"], value=str(init_min_ts))
    var_max = ft.TextField(label=dicts[current_lang]["max_weekly_ts"], value=str(init_max_ts))
    util_tf = ft.TextField(label=dicts[current_lang]["utility"], value=str(init_util_cte))
    var_adj_min = ft.TextField(label=dicts[current_lang]["min_adj"], value=str(init_min_adj))
    var_adj_max = ft.TextField(label=dicts[current_lang]["max_adj"], value=str(init_max_adj))

    def open_pw_panel():
        pw_panel.visible = True
        if confirm_btn_ref: confirm_btn_ref[0].disabled = True
        if cancel_btn_ref: cancel_btn_ref[0].disabled = True
        page.update()

    pw_btn = ft.ElevatedButton(dicts[current_lang]["configure_pw_util"], on_click=lambda e: open_pw_panel())

    win_fields = {day: ft.TextField(label=daydic[day].capitalize(), value=init_window.get(day, "")) for day in range(1, 8)}
    window_panel = ft.Column([ft.Text(dicts[current_lang]["allowed_window"])] + list(win_fields.values()))
    penalties_fields_var = {a: ft.TextField(label=a.name, value=str(init_penalties.get(a, ""))) for a in activities}
    penalties_panel_var = ft.Column([ft.Text(dicts[current_lang]["penalties"])] + list(penalties_fields_var.values()))

    fix_advanced_panel = ft.Column([penalties_panel_fixed], visible=False)
    var_advanced_panel = ft.Column([var_adj_min, var_adj_max, pw_btn, window_panel, penalties_panel_var], visible=False)

    def on_type_change(e):
        is_fixed = (type_dd.value == "fixed")
        sched_panel.visible = is_fixed
        var_min.visible = not is_fixed
        var_max.visible = not is_fixed
        util_tf.visible = not is_fixed
        fix_advanced_panel.visible = False
        var_advanced_panel.visible = False
        page.update()

    type_dd = ft.Dropdown(
        label=dicts[current_lang]["type"],
        options=[
            ft.dropdown.Option(dicts[current_lang]["fixed"], data="fixed"),
            ft.dropdown.Option(dicts[current_lang]["variable"], data="variable"),
        ],
        value=init_type,
        on_change=on_type_change
    )
    name_tf = ft.TextField(label=dicts[current_lang]["name"], value=init_name)
    adv_btn = ft.ElevatedButton(dicts[current_lang]["advanced_options"], on_click=lambda e: toggle_panel(fix_advanced_panel if type_dd.value == "fixed" else var_advanced_panel))

    on_type_change(None)

    form_body = ft.Column([
        type_dd, name_tf, sched_panel, var_min, var_max, util_tf,
        fix_advanced_panel, var_advanced_panel, adv_btn,
    ], scroll="auto", expand=True)

    # Save form data into function attribute for confirm_add_edit()
    page._form_inputs = {
        "type_dd": type_dd,
        "name_tf": name_tf,
        "sched_fields": sched_fields,
        "var_min": var_min,
        "var_max": var_max,
        "util_tf": util_tf,
        "var_adj_min": var_adj_min,
        "var_adj_max": var_adj_max,
        "penalties_fields_var": penalties_fields_var,
        "penalties_fields_fixed": penalties_fields_fixed,
        "win_fields": win_fields,
        "utility": util
    }

    return ft.Stack([form_body, pw_panel])

def confirm_add_edit(dlg: ft.AlertDialog, edit=False):
    page = dlg.page
    f = page._form_inputs
    name = f["name_tf"].value.strip()
    if f["type_dd"].value == "fixed":
        assigned = parse_window(None, number_of_ts, f["sched_fields"])
        penalties = {a: float(f["penalties_fields_fixed"][a].value) for a in f["penalties_fields_fixed"] if f["penalties_fields_fixed"][a].value.strip()}
        new_act = fixedActivity(name, penalties, assigned)
    else:
        min_ts = int(f["var_min"].value)
        max_ts = int(f["var_max"].value)
        util_cte = float(f["util_tf"].value)
        min_adj = int(f["var_adj_min"].value)
        max_adj = int(f["var_adj_max"].value)
        penalties = {a: float(f["penalties_fields_var"][a].value) for a in f["penalties_fields_var"] if f["penalties_fields_var"][a].value.strip()}
        win = {d: f["win_fields"][d].value for d in f["win_fields"]}
        if util_cte>0:
            cteUtil = {day:dailyUtility([3],[util_cte,util_cte]) for day in range(1,8)} 
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




if __name__ == "__main__":
    ft.app(target=main)
