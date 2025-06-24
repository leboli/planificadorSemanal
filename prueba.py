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
        "assigned_schedule": "Assigned schedule",
        "advanced_options": "Advanced options",
        "penalties": "Penalties",
        "min_weekly_ts": "Min weekly time units",
        "max_weekly_ts": "Max weekly time units",
        "utility": "Utility (constant)",
        "min_adj": "Min adjacent slots",
        "max_adj": "Max adjacent slots",
        "configure_pw_util": "Configure piecewise daily utility",
        "allowed_window": "Allowed window",
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
        "assigned_schedule": "Horario asignado",
        "advanced_options": "Opciones avanzadas",
        "penalties": "Penalizaciones",
        "min_weekly_ts": "Mín ranuras semanales",
        "max_weekly_ts": "Máx ranuras semanales",
        "utility": "Utilidad (constante)",
        "min_adj": "Mín ranuras adyacentes",
        "max_adj": "Máx ranuras adyacentes",
        "configure_pw_util": "Configurar utilidad diaria por partes",
        "allowed_window": "Ventana permitida",
        "confirm": "Confirmar",
        "cancel": "Cancelar",
    }
}

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
    activities_table = ft.DataTable(columns=[ft.DataColumn(ft.Text(dicts[current_lang]["name"]))], rows=[], width=280)
    refresh_activities(page=page)

    add_btn = ft.ElevatedButton(dicts[current_lang]["add"], on_click=open_add_dialog)
    edit_btn = ft.ElevatedButton(dicts[current_lang]["edit"], on_click=open_edit_dialog, disabled=True)
    solve_btn = ft.ElevatedButton(dicts[current_lang]["solve"], on_click=lambda e: print("solving"), bgcolor=ft.Colors.PINK_ACCENT_200, width=320)

    activities_column = ft.Column(
        [
            ft.Text(dicts[current_lang]["activities"]),
            ft.Container(
                content=activities_table,
                height=300,
                bgcolor=ft.Colors.GREY_700,
                padding=5,
            ),
            ft.Row([add_btn, edit_btn]),
        ],
        width=300,
    )
    activities_panel = ft.Container(
        content=activities_column,
        bgcolor=ft.Colors.GREY_900,
        padding=10,
        expand=False,
        height=400  # minimum panel height
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
    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text(f"{dicts[current_lang]['add']} Activity"),
        content=ft.Container(build_activity_form(None),width=600),
        actions=[
            ft.TextButton(text=dicts[current_lang]["cancel"], on_click=close_dialog),
            ft.TextButton(text=dicts[current_lang]["confirm"], on_click=close_dialog),
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
        content=build_activity_form(activities[selected_index]),
        actions=[
            ft.TextButton(text=dicts[current_lang]["cancel"], on_click=close_dialog),
            ft.TextButton(text=dicts[current_lang]["confirm"], on_click=close_dialog),
        ],
    )
    page.open(dlg)
    page.update()


def close_dialog(e: ft.ControlEvent):
    page = e.page
    if page.dialog:
        page.close(page.dialog)
        page.update()


def build_activity_form(act):
    new_act_type = "fixed" if not act or isinstance(act, fixedActivity) else "variable"
    new_act_name = act.name if act else ""
    new_act_schedules = {} if not act or isinstance(act,variableActivity) else act.assigned_ts
    new_act_penalties = {} if not act else act.penalties
    new_act_min_ts = 0 if not act or isinstance(act,fixedActivity) else act.min_ts
    new_act_max_ts = number_of_ts if not act or isinstance(act,fixedActivity) else act.max_ts
    new_act_util_cte = 0
    new_act_min_adj = 1 if not act or isinstance(act,fixedActivity) else act.min_adjacent_ts
    new_act_max_adj = number_of_ts if not act or isinstance(act,fixedActivity) else act.max_adjacent_ts
    new_act_util = {} if not act or isinstance(act,fixedActivity) else act.utility
    new_act_window = {} if not act or isinstance(act,fixedActivity) else act.allowed_ts

    type_dd = ft.Dropdown(
        options=[
            ft.dropdown.Option(dicts[current_lang]["fixed"]),
            ft.dropdown.Option(dicts[current_lang]["variable"]),
        ],
        value=new_act_type,
    )
    name_tf = ft.TextField(label=dicts[current_lang]["name"], value=new_act_name)

    sched_fields = {day: ft.TextField(label=day.capitalize(), value=(act.assigned_ts[day] if act and isinstance(act, fixedActivity) else "")) for day in ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"]}
    sched_panel = ft.Column([ft.Text(dicts[current_lang]["assigned_schedule"])] + list(sched_fields.values()))

    penalties_fields = {a: ft.TextField(label=a.name, value=(act.penalties.get(a,"") if act else "")) for a in activities}
    penalties_panel = ft.Column([ft.Text(dicts[current_lang]["penalties"])] + list(penalties_fields.values()), visible=False)
    adv_btn = ft.ElevatedButton(dicts[current_lang]["advanced_options"], on_click=lambda e: toggle_panel(penalties_panel))

    var_min = ft.TextField(label=dicts[current_lang]["min_weekly_ts"], value=(str(act.min_ts) if act and isinstance(act, variableActivity) else ""))
    var_max = ft.TextField(label=dicts[current_lang]["max_weekly_ts"], value=(str(act.max_ts) if act and isinstance(act, variableActivity) else ""))
    util_tf = ft.TextField(label=dicts[current_lang]["utility"], value=(str(act.util) if act and isinstance(act, variableActivity) else ""))

    var_adj_min = ft.TextField(label=dicts[current_lang]["min_adj"], value=(str(act.min_adj) if act and isinstance(act, variableActivity) else ""))
    var_adj_max = ft.TextField(label=dicts[current_lang]["max_adj"], value=(str(act.max_adj) if act and isinstance(act, variableActivity) else ""))
    pw_btn = ft.ElevatedButton(dicts[current_lang]["configure_pw_util"], on_click=lambda e: open_pw_dialog(util_tf))
    win_fields = {day: ft.TextField(label=day.capitalize(), value=(act.window.get(day,"") if act and isinstance(act, variableActivity) else "")) for day in ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"]}
    window_panel = ft.Column([ft.Text(dicts[current_lang]["allowed_window"])] + list(win_fields.values()))
    penalties_panel_var = ft.Column([ft.Text(dicts[current_lang]["penalties"])] + list(penalties_fields.values()), visible=False)
    var_advanced_panel = ft.Column([var_adj_min, var_adj_max, pw_btn, window_panel, penalties_panel_var], visible=False)
    adv_btn_var = ft.ElevatedButton(dicts[current_lang]["advanced_options"], on_click=lambda e: toggle_panel(var_advanced_panel))

    def on_type_change(e):
        fixed = e.control.value == dicts[current_lang]["fixed"]
        sched_panel.visible = fixed
        adv_btn.visible = fixed
        var_min.visible = not fixed
        var_max.visible = not fixed
        util_tf.visible = not fixed
        adv_btn_var.visible = not fixed
        var_advanced_panel.visible = False
        e.page.update()

    type_dd.on_change = on_type_change

    return ft.Column([
        type_dd,
        name_tf,
        sched_panel,
        adv_btn,
        var_min,
        var_max,
        util_tf,
        adv_btn_var,
        var_advanced_panel,
    ])


def toggle_panel(panel: ft.Control):
    panel.visible = not panel.visible
    panel.page.update()


def open_pw_dialog(util_tf: ft.TextField):
    page = util_tf.page
    pw_dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text(dicts[current_lang]["configure_pw_util"]),
        content=ft.Text(""),
        actions=[
            ft.TextButton(dicts[current_lang]["cancel"], on_click=close_dialog),
            ft.TextButton(dicts[current_lang]["confirm"], on_click=lambda e: confirm_pw(pw_dlg, util_tf)),
        ],
    )
    page.open(pw_dlg)
    page.update()


def confirm_pw(dlg: ft.AlertDialog, util_tf: ft.TextField):
    util_tf.disabled = True
    util_tf.value = ""
    util_tf.page.data = {"monday": ([1, 2, 3], [4, 5, 6, 7])}
    page = util_tf.page
    page.close(dlg)
    page.update()


def confirm_add_edit(dlg: ft.AlertDialog, edit=False):
    new_act = fixedActivity("Example", {}, {})
    if edit:
        activities[selected_index] = new_act
    else:
        activities.append(new_act)
    page = dlg.page
    refresh_activities(page)
    page.close(dlg)
    page.update()


if __name__ == "__main__":
    ft.app(target=main)
