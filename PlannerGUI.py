import tkinter as tk
from tkinter import ttk, messagebox
from planner import planner
from entities.fixedActivity import fixedActivity
from entities.variableActivity import variableActivity
from entities.dailyUtility import dailyUtility

class PlannerGUI(tk.Tk):
    def __init__(self):
        super().__init__()

        # language labels dictionaries
        self.languages = {
            'es': {
                'title': "Planificador Semanal",
                'granularity': "Unidad de tiempo:",
                'add_edit': "Agregar / Modificar Actividad",
                'type': "Tipo:",
                'fixed': "Fija",
                'variable': "Variable",
                'save': "Guardar",
                'delete': "Eliminar",
                'activities': "Actividades",
                'calculate': "Calcular",
                'name': "Nombre:",
                'slots': "Franjas (p.ej. 0,1,2):",
                'utility': "Utilidad:",
                'min_weekly': "Min Semanal:",
                'max_weekly': "Max Semanal:",
                'lmin': "Lmin:",
                'lmax': "Lmax:",
                'advanced': "Configuración avanzada",
                'const_utility': "Utilidad constante (u):",
                'penalties': "Penalizaciones (a:val,...):",
                'window': "Ventana permitida",
                'days': ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"],
                'error': "Error",
                'name_required': "Nombre requerido",
                'no_solution': "No hay solución óptima.",
                'total_utility': "Utilidad total: ",
                'language': "Idioma:",
                '168': "1 hora",
                '336': "30 minutos",
                '672': "15 minutos"
            },
            'en': {
                'title': "Weekly Planner",
                'granularity': "Time unit:",
                'add_edit': "Add / Edit Activity",
                'type': "Type:",
                'fixed': "Fixed",
                'variable': "Variable",
                'save': "Save",
                'delete': "Delete",
                'activities': "Activities",
                'calculate': "Calculate",
                'name': "Name:",
                'slots': "Slots (e.g. 0,1,2):",
                'utility': "Utility:",
                'min_weekly': "Min Weekly:",
                'max_weekly': "Max Weekly:",
                'lmin': "Lmin:",
                'lmax': "Lmax:",
                'advanced': "Advanced settings",
                'const_utility': "Constant utility (u):",
                'penalties': "Penalties (a:val,...):",
                'window': "Allowed window",
                'days': ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                'error': "Error",
                'name_required': "Name required",
                'no_solution': "No optimal solution.",
                'total_utility': "Total utility: ",
                'language': "Language:",
                '168': "1 hour",
                '336': "30 minutes",
                '672': "15 minutes"
            }
        }

        # Idioma inicial
        self.language = tk.StringVar(value='es')
        self.texts = self.languages[self.language.get()]
        self.activities = []
        self.window_entries = {}  # para almacenar entradas de ventana

        # Window config
        self.title(self.texts['title'])
        self.geometry("1000x600")
        self.create_widgets()

    def create_widgets(self):
        # Sección de idioma
        lang_frame = ttk.Labelframe(self, text=self.texts['language'])
        lang_frame.pack(fill='x', padx=5, pady=5)
        ttk.OptionMenu(
            lang_frame, self.language, self.language.get(),
            *self.languages.keys(), command=self.set_language
        ).pack(side='left', padx=5)

        # Sección de cantidad de ts
        gran_frame = ttk.Labelframe(self, text=self.texts['granularity'])
        gran_frame.pack(fill='x', padx=5, pady=5)
        self.gran_var = tk.StringVar(value=self.texts['168'])
        ttk.Combobox(
            gran_frame, textvariable=self.gran_var,
            values=[self.texts['168'], self.texts['336'], self.texts['672']],
            state="readonly", width=15
        ).pack(side='left', padx=5)

        # Paneles izquierdo y derecho
        self.paned = ttk.Panedwindow(self, orient='horizontal')
        self.paned.pack(fill='both', expand=True)

        self.left_frame = ttk.Frame(self.paned, width=300)
        self.paned.add(self.left_frame, weight=1)

        self.right_frame = ttk.Frame(self.paned)
        self.paned.add(self.right_frame, weight=3)

        self.build_left()
        self.build_right()

    def set_language(self, lang_code):
        self.texts = self.languages[lang_code]
        self.title(self.texts['title'])
        for w in self.winfo_children(): w.destroy()
        self.create_widgets()

    def build_left(self):
        # Sección de formulario y lista de actividades
        form_frame = ttk.Labelframe(self.left_frame, text=self.texts['add_edit'])
        form_frame.pack(fill='x', padx=5, pady=5)

        ttk.Label(form_frame, text=self.texts['type']).grid(row=0, column=0, sticky='w')
        self.type_var = tk.StringVar(value=self.texts['fixed'])
        ttk.Combobox(
            form_frame, textvariable=self.type_var,
            values=[self.texts['fixed'], self.texts['variable']],
            state="readonly", width=12
        ).grid(row=0, column=1, sticky='w')
        self.type_var.trace_add('write', lambda *args: self.build_form(form_frame))

        self.dynamic_frame = ttk.Frame(form_frame)
        self.dynamic_frame.grid(row=1, column=0, columnspan=2, pady=5)
        self.build_form(form_frame)

        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=99, column=0, columnspan=2, pady=5)
        ttk.Button(btn_frame, text=self.texts['save'],   command=self.save_activity).pack(side='left', padx=5)
        ttk.Button(btn_frame, text=self.texts['delete'], command=self.delete_activity).pack(side='left')

        list_frame = ttk.Labelframe(self.left_frame, text=self.texts['activities'])
        list_frame.pack(fill='both', expand=True, padx=5, pady=5)
        self.act_list = tk.Listbox(list_frame)
        self.act_list.pack(fill='both', expand=True)
        self.act_list.bind('<<ListboxSelect>>', self.load_selected)

    def build_right(self):
        ttk.Button(self.right_frame, text=self.texts['calculate'], command=self.calculate).pack(pady=5)
        self.result_text = tk.Text(self.right_frame, height=10)
        self.result_text.pack(fill='both', expand=True, padx=5, pady=5)

    def build_form(self, parent):
        for w in self.dynamic_frame.winfo_children(): w.destroy()

        if self.type_var.get() == self.texts['fixed']:
            ttk.Label(self.dynamic_frame, text=self.texts['name']).grid(row=0, column=0, sticky='w')
            self.name_entry = ttk.Entry(self.dynamic_frame); self.name_entry.grid(row=0, column=1, sticky='ew')

            ttk.Label(self.dynamic_frame, text=self.texts['slots']).grid(row=1, column=0, sticky='w')
            self.slots_entry = ttk.Entry(self.dynamic_frame); self.slots_entry.grid(row=1, column=1, sticky='ew')

        else:
            ttk.Label(self.dynamic_frame, text=self.texts['name']).grid(row=0, column=0, sticky='w')
            self.name_entry = ttk.Entry(self.dynamic_frame); self.name_entry.grid(row=0, column=1, sticky='ew')

            ttk.Label(self.dynamic_frame, text=self.texts['min_weekly']).grid(row=1, column=0, sticky='w')
            self.min_entry = ttk.Entry(self.dynamic_frame); self.min_entry.grid(row=1, column=1, sticky='ew')

            ttk.Label(self.dynamic_frame, text=self.texts['max_weekly']).grid(row=2, column=0, sticky='w')
            self.max_entry = ttk.Entry(self.dynamic_frame); self.max_entry.grid(row=2, column=1, sticky='ew')

            ttk.Label(self.dynamic_frame, text=self.texts['lmin']).grid(row=3, column=0, sticky='w')
            self.lmin_entry = ttk.Entry(self.dynamic_frame); self.lmin_entry.grid(row=3, column=1, sticky='ew')

            ttk.Label(self.dynamic_frame, text=self.texts['lmax']).grid(row=4, column=0, sticky='w')
            self.lmax_entry = ttk.Entry(self.dynamic_frame); self.lmax_entry.grid(row=4, column=1, sticky='ew')

            self.adv_var = tk.BooleanVar(value=False)
            ttk.Checkbutton(
                self.dynamic_frame, text=self.texts['advanced'],
                variable=self.adv_var, command=self.build_advanced
            ).grid(row=5, column=0, columnspan=2, pady=5)

            self.adv_frame = ttk.Frame(self.dynamic_frame)
            self.adv_frame.grid(row=6, column=0, columnspan=2, sticky='ew')

    def build_advanced(self):
        for w in self.adv_frame.winfo_children(): w.destroy()
        if not self.adv_var.get():
            return
        # Utilidad y penalidades
        ttk.Label(self.adv_frame, text=self.texts['const_utility']).grid(row=0, column=0, sticky='w')
        self.const_util = ttk.Entry(self.adv_frame); self.const_util.grid(row=0, column=1, sticky='ew')

        ttk.Label(self.adv_frame, text=self.texts['penalties']).grid(row=1, column=0, sticky='w')
        self.pens_entry = ttk.Entry(self.adv_frame); self.pens_entry.grid(row=1, column=1, sticky='ew')

        # Sección de ventana permitida
        win_frame = ttk.Labelframe(self.adv_frame, text=self.texts['window'])
        win_frame.grid(row=2, column=0, columnspan=2, pady=5, sticky='ew')
        self.window_entries.clear()
        for i, day in enumerate(self.texts['days'], start=1):
            ttk.Label(win_frame, text=f"{day}:").grid(row=i-1, column=0, sticky='w')
            entry = ttk.Entry(win_frame)
            entry.grid(row=i-1, column=1, sticky='ew', padx=2, pady=1)
            self.window_entries[i] = entry

    def parse_window(self, num_slots):
        # convierte entradas HH:MM-HH:MM[, ...] por día a lista de índices
        slots_per_day = num_slots // 7
        slot_minutes = 7*24*60 // num_slots  # minutos por franja
        indices = []
        for day, entry in self.window_entries.items():
            raw = entry.get().strip()
            if not raw:
                continue
            periods = [p.strip() for p in raw.split(',')]
            for period in periods:
                try:
                    start_s, end_s = period.split('-')
                    h1, m1 = map(int, start_s.split(':'))
                    h2, m2 = map(int, end_s.split(':'))
                except ValueError:
                    continue
                start_min = h1*60 + m1
                end_min = h2*60 + m2
                start_idx = (day-1)*slots_per_day + start_min // slot_minutes
                end_idx = (day-1)*slots_per_day + end_min // slot_minutes
                indices.extend(range(start_idx, end_idx+1))
        return sorted(set(indices))

    def save_activity(self):
        t    = self.type_var.get()
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showwarning(self.texts['error'], self.texts['name_required'])
            return

        sel = self.act_list.curselection()
        if sel:
            del self.activities[sel[0]]
            self.act_list.delete(sel)

        if t == self.texts['fixed']:
            slots = [int(x) for x in self.slots_entry.get().split(',') if x.strip().isdigit()]
            act = fixedActivity(name, slots)
        else:
            mn = int(self.min_entry.get() or 0)
            mx = int(self.max_entry.get() or 700)
            lmin = int(self.lmin_entry.get() or 1)
            num = {'168':168, '336':336, '672':672}[str({'1 hora':168,'30 minutos':336,'15 minutos':672}[self.gran_var.get()])]
            lmax = int(self.lmax_entry.get() or num)
            # parse ventana según granularidad
            window = self.parse_window(num)
            act = variableActivity(name, mn, mx, window, lmin, lmax)
            if self.adv_var.get() and hasattr(self, 'const_util'):
                u = float(self.const_util.get() or 0)
                act.set_constant_utility(u)

        self.activities.append(act)
        self.act_list.insert('end', f"{t}: {name}")

    def delete_activity(self):
        sel = self.act_list.curselection()
        if sel:
            del self.activities[sel[0]]
            self.act_list.delete(sel)

    def load_selected(self, event):
        sel = self.act_list.curselection()
        if not sel:
            return
        act = self.activities[sel[0]]

        if isinstance(act, fixedActivity):
            self.type_var.set(self.texts['fixed'])
        else:
            self.type_var.set(self.texts['variable'])
        self.build_form(None)

        self.name_entry.delete(0,'end'); self.name_entry.insert(0, act.name)
        if isinstance(act, fixedActivity):
            self.slots_entry.delete(0,'end'); self.slots_entry.insert(0, ",".join(map(str, act.assigned_slots)))
        else:
            self.min_entry.delete(0,'end'); self.min_entry.insert(0, str(act.weekly_min))
            self.max_entry.delete(0,'end'); self.max_entry.insert(0, str(act.weekly_max))
            self.lmin_entry.delete(0,'end'); self.lmin_entry.insert(0, str(act.lmin))
            self.lmax_entry.delete(0,'end'); self.lmax_entry.insert(0, str(act.lmax))
            self.adv_var.set(bool(act.allowed_ts))
            self.build_advanced()
            for d, entry in self.window_entries.items():
                # reconstruir texto de ventana si existe
                periods = []
                for idx in act.allowed_ts:
                    day = (idx // (num_slots//7)) + 1
                    if day == d:
                        slot = idx % (num_slots//7)
                        periods.append(f"{slot}")
                entry_text = ",".join(periods)
                entry.insert(0, entry_text)

    def calculate(self):
        num = {'1 hora':168, '30 minutos':336, '15 minutos':672}[self.gran_var.get()]
        pl = planner(
            fixed_activities=[a for a in self.activities if isinstance(a, fixedActivity)],
            variable_activities=[a for a in self.activities if isinstance(a, variableActivity)],
            num_slots=num
        )
        pl.buildModel()
        util, sol = pl.solve()

        self.result_text.delete('1.0', 'end')
        if sol is None:
            self.result_text.insert('end', self.texts['no_solution'])
        else:
            self.result_text.insert('end', f"{self.texts['total_utility']}{util}\n")
            for (name, t), val in sol.items():
                if val:
                    self.result_text.insert('end', f"{name}@{t} | ")
            self.result_text.insert('end', "\n---\n")
