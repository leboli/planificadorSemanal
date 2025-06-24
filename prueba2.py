import flet as ft
from entities.fixedActivity import fixedActivity
from entities.variableActivity import variableActivity

# Traducciones
dicts = {
    "en": {
        "add": "Add",
        "edit": "Edit",
        "confirm": "Confirm",
        "cancel": "Cancel",
        "activities": "Activities",
        "name": "Name",
    },
    "es": {
        "add": "Agregar",
        "edit": "Editar",
        "confirm": "Confirmar",
        "cancel": "Cancelar",
        "activities": "Actividades",
        "name": "Nombre",
    }
}

def main(page: ft.Page):
    page.title = "Scheduler"
    page.window_width = 800
    page.window_height = 600

    # Estado
    current_lang = "en"
    activities: list = []
    selected_index = -1

    # Referencias UI
    lang_dd = None
    activities_table = None
    add_btn = None
    edit_btn = None

    # Refrescar tabla
    def refresh_activities():
        activities_table.rows.clear()
        for i, act in enumerate(activities):
            activities_table.rows.append(
                ft.DataRow(
                    cells=[ft.DataCell(ft.Text(act.name))],
                    on_select=lambda e, idx=i: select_activity(idx),
                )
            )
        page.update()

    # Selección
    def select_activity(idx: int):
        nonlocal selected_index
        selected_index = idx
        edit_btn.disabled = False
        for j, row in enumerate(activities_table.rows):
            row.selected = (j == idx)
        page.update()

    # Cerrar diálogo genérico
    def close_dlg(dlg: ft.AlertDialog):
        dlg.open = False
        page.update()

    # Abrir diálogo de añadir
    def open_add(e):
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text(dicts[current_lang]["add"] + " Activity"),
            content=build_activity_form(None),
            actions=[
                ft.TextButton(dicts[current_lang]["cancel"],
                              on_click=lambda e, dlg=dlg: close_dlg(dlg)),
                ft.TextButton(dicts[current_lang]["confirm"],
                              on_click=lambda e, dlg=dlg: confirm_add_edit(dlg, edit=False)),
            ],
        )
        page.dialog = dlg
        dlg.open = True
        page.update()

    # Abrir diálogo de editar
    def open_edit(e):
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text(dicts[current_lang]["edit"] + " Activity"),
            content=build_activity_form(activities[selected_index]),
            actions=[
                ft.TextButton(dicts[current_lang]["cancel"],
                              on_click=lambda e, dlg=dlg: close_dlg(dlg)),
                ft.TextButton(dicts[current_lang]["confirm"],
                              on_click=lambda e, dlg=dlg: confirm_add_edit(dlg, edit=True)),
            ],
        )
        page.dialog = dlg
        dlg.open = True
        page.update()

    # Confirmar añadir/editar
    def confirm_add_edit(dlg: ft.AlertDialog, edit=False):
        # Ejemplo: siempre creamos un fixedActivity de prueba
        new_act = fixedActivity("New Activity", {}, {})
        if edit:
            activities[selected_index] = new_act
        else:
            activities.append(new_act)
        refresh_activities()
        close_dlg(dlg)

    # Formulario de actividad (simplificado)
    def build_activity_form(act):
        return ft.Column([
            ft.TextField(label=dicts[current_lang]["name"], value=(act.name if act else "")),
        ])

    # Construcción UI
    lang_dd = ft.Dropdown(
        options=[ft.dropdown.Option("en"), ft.dropdown.Option("es")],
        value=current_lang,
        on_change=lambda e: change_language(e),
    )

    activities_table = ft.DataTable(
        columns=[ft.DataColumn(ft.Text(dicts[current_lang]["name"]))],
        rows=[],
        width=300,
        height=200,
    )
    refresh_activities()

    add_btn = ft.ElevatedButton(dicts[current_lang]["add"], on_click=open_add)
    edit_btn = ft.ElevatedButton(dicts[current_lang]["edit"], on_click=open_edit, disabled=True)

    page.add(
        ft.Row([lang_dd]),
        ft.Row([
            activities_table,
            ft.Column([add_btn, edit_btn], spacing=10)
        ], spacing=20)
    )

    # Cambio de idioma: solo actualiza etiquetas
    def change_language(e):
        nonlocal current_lang
        current_lang = e.control.value
        # actualizar textos estáticos
        add_btn.text = dicts[current_lang]["add"]
        edit_btn.text = dicts[current_lang]["edit"]
        activities_table.columns[0].label.value = dicts[current_lang]["name"]
        page.update()

if __name__ == "__main__":
    ft.app(target=main)
