import tkinter as tk
from tkinter import ttk, messagebox
from planner import planner
from entities.fixedActivity import fixedActivity
from entities.variableActivity import variableActivity
from entities.dailyUtility import dailyUtility

class PlannerGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        # --- Configuración inicial ---
        self.languages = {
            'es': {
                'title': "Planificador Semanal",
                'granularity': "Unidad de tiempo/Tamaño de las franjas:",
                'add_edit': "Agregar / Modificar Actividad",
                'type': "Tipo:",
                'fixed': "Fija",
                'variable': "Variable",
                'save': "Guardar",
                'delete': "Eliminar",
                'activities': "Actividades",
                'calculate': "Calcular",
                'name': "Nombre:",
                'slots': "Franjas permitidas (HH:MM-HH:MM,...):",
                'utility': "Utilidad:",
                'min_weekly': "Min Semanal:",
                'max_weekly': "Max Semanal:",
                'lmin': "Mín. franjas contiguas:",
                'lmax': "Máx. franjas contiguas:",
                'advanced': "Configuración avanzada",
                'const_utility': "Utilidad (constante):",
                'piecewise_utility': "Utilidad escalonada por día:",
                'penalties': "Penalizaciones (a:val,...):",
                'window': "Ventana permitida (HH:MM-HH:MM,...)",
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
                'granularity': "Time unit/Size of time slots:",
                'add_edit': "Add / Edit Activity",
                'type': "Type:",
                'fixed': "Fixed",
                'variable': "Variable",
                'save': "Save",
                'delete': "Delete",
                'activities': "Activities",
                'calculate': "Calculate",
                'name': "Name:",
                'slots': "Allowed slots (HH:MM-HH:MM,...):",
                'utility': "Utility:",
                'min_weekly': "Min Weekly:",
                'max_weekly': "Max Weekly:",
                'lmin': "Min. adjacent slots:",
                'lmax': "Max. adjacent slots:",
                'advanced': "Advanced settings",
                'const_utility': "Utility (constant):",
                'piecewise_utility': "Piecewise daily utility:",
                'penalties': "Penalties (a:val,...):",
                'window': "Allowed window (HH:MM-HH:MM,...)",
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
        self.language = tk.StringVar(value='es')
        self.texts = self.languages[self.language.get()]
        self.activities = []
        self.window_entries = {}
        self.util_entries = {}
        self.slots_entries = {}

        self.title(self.texts['title'])
        self.geometry("1000x600")
        self.create_widgets()

    def create_widgets(self):
        # Idioma
        lang_frame = ttk.Labelframe(self, text=self.texts['language'])
        lang_frame.pack(fill='x', padx=5, pady=5)
        ttk.OptionMenu(
            lang_frame, self.language, self.language.get(),
            *self.languages.keys(), command=self.set_language
        ).pack(side='left', padx=5)

        # Granularidad
        gran_frame = ttk.Labelframe(self, text=self.texts['granularity'])
        gran_frame.pack(fill='x', padx=5, pady=5)
        self.gran_var = tk.StringVar(value=self.texts['168'])
        ttk.Combobox(
            gran_frame, textvariable=self.gran_var,
            values=[self.texts['168'], self.texts['336'], self.texts['672']],
            state="readonly", width=15
        ).pack(side='left', padx=5)

        # Panel con scroll izquierda
        self.paned = ttk.Panedwindow(self, orient='horizontal')
        self.paned.pack(fill='both', expand=True)
        left_container = ttk.Frame(self.paned)
        self.paned.add(left_container, weight=1)
        self.left_canvas = tk.Canvas(left_container)
        vscroll = ttk.Scrollbar(left_container, orient='vertical', command=self.left_canvas.yview)
        self.left_canvas.configure(yscrollcommand=vscroll.set)
        vscroll.pack(side='right', fill='y')
        self.left_frame = ttk.Frame(self.left_canvas)
        self.left_canvas.create_window((0,0), window=self.left_frame, anchor='nw')
        self.left_canvas.pack(fill='both', expand=True)
        self.left_frame.bind('<Configure>', lambda e: self.left_canvas.configure(scrollregion=self.left_canvas.bbox('all')))

        # Panel derecha
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
        form_frame = ttk.Labelframe(self.left_frame, text=self.texts['add_edit'])
        form_frame.pack(fill='x', padx=5, pady=5)
        ttk.Label(form_frame, text=self.texts['type']).grid(row=0, column=0, sticky='w')
        self.type_var = tk.StringVar(value=self.texts['fixed'])
        ttk.Combobox(
            form_frame, textvariable=self.type_var,
            values=[self.texts['fixed'], self.texts['variable']],
            state="readonly", width=12
        ).grid(row=0, column=1, sticky='w')
        self.type_var.trace_add('write', lambda *args: self.build_form())

        self.dynamic_frame = ttk.Frame(form_frame)
        self.dynamic_frame.grid(row=1, column=0, columnspan=2, pady=5)
        self.build_form()

        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=99, column=0, columnspan=2, pady=5)
        ttk.Button(btn_frame, text=self.texts['save'], command=self.save_activity).pack(side='left', padx=5)
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

    def build_form(self):
        for w in self.dynamic_frame.winfo_children(): w.destroy()
        if self.type_var.get() == self.texts['fixed']:
            ttk.Label(self.dynamic_frame, text=self.texts['name']).grid(row=0, column=0, sticky='w')
            self.name_entry = ttk.Entry(self.dynamic_frame); self.name_entry.grid(row=0, column=1, sticky='ew')
            slots_frame = ttk.Labelframe(self.dynamic_frame, text=self.texts['slots'])
            slots_frame.grid(row=1, column=0, columnspan=2, pady=5, sticky='ew')
            self.slots_entries.clear()
            for i, day in enumerate(self.texts['days'], start=1):
                ttk.Label(slots_frame, text=f"{day}:").grid(row=i-1, column=0, sticky='w')
                e = ttk.Entry(slots_frame)
                e.grid(row=i-1, column=1, sticky='ew', padx=2, pady=1)
                self.slots_entries[i] = e
        else:
            ttk.Label(self.dynamic_frame, text=self.texts['name']).grid(row=0, column=0, sticky='w')
            self.name_entry = ttk.Entry(self.dynamic_frame); self.name_entry.grid(row=0, column=1, sticky='ew')

            ttk.Label(self.dynamic_frame, text=self.texts['min_weekly']).grid(row=1, column=0, sticky='w')
            self.min_entry = ttk.Entry(self.dynamic_frame); self.min_entry.grid(row=1, column=1, sticky='ew')

            ttk.Label(self.dynamic_frame, text=self.texts['max_weekly']).grid(row=2, column=0, sticky='w')
            self.max_entry = ttk.Entry(self.dynamic_frame); self.max_entry.grid(row=2, column=1, sticky='ew')

            ttk.Label(self.dynamic_frame, text=self.texts['const_utility']).grid(row=3, column=0, sticky='w')
            self.const_util = ttk.Entry(self.dynamic_frame); self.const_util.grid(row=3, column=1, sticky='ew')

            self.adv_var = tk.BooleanVar(value=False)
            ttk.Checkbutton(
                self.dynamic_frame, text=self.texts['advanced'], variable=self.adv_var,
                command=self.build_advanced
            ).grid(row=5, column=0, columnspan=2, pady=5)
            self.adv_frame = ttk.Frame(self.dynamic_frame)
            self.adv_frame.grid(row=6, column=0, columnspan=2, sticky='ew')

    def build_advanced(self):
        for w in self.adv_frame.winfo_children(): w.destroy()
        if not self.adv_var.get(): return
        ttk.Label(self.adv_frame, text=self.texts['lmin']).grid(row=1, column=0, sticky='w')
        self.lmin_entry = ttk.Entry(self.adv_frame); self.lmin_entry.grid(row=1, column=1, sticky='ew')

        ttk.Label(self.adv_frame, text=self.texts['lmax']).grid(row=2, column=0, sticky='w')
        self.lmax_entry = ttk.Entry(self.adv_frame); self.lmax_entry.grid(row=2, column=1, sticky='ew')

        # ----- piecewise utility section -----
        util_frame = ttk.Labelframe(self.adv_frame, text=self.texts['piecewise_utility'])
        util_frame.grid(row=3, column=0, columnspan=2, pady=5, sticky='ew')
        # create one subframe per day
        for i, day in enumerate(self.texts['days']):
            day_frame = ttk.Frame(util_frame)
            day_frame.grid(row=i, column=0, sticky='ew', pady=2)
            self.add_piecewise_row(day, day_frame, from_value=0)

        # penalties and window unchanged
        ttk.Label(self.adv_frame, text=self.texts['penalties']).grid(row=5, column=0, sticky='w')
        self.pens_entry = ttk.Entry(self.adv_frame); self.pens_entry.grid(row=5, column=1, sticky='ew')

        win_frame = ttk.Labelframe(self.adv_frame, text=self.texts['window'])
        win_frame.grid(row=4, column=0, columnspan=2, pady=5, sticky='ew')
        self.window_entries.clear()
        for i, day in enumerate(self.texts['days'], start=1):
            ttk.Label(win_frame, text=f"{day}:").grid(row=i-1, column=0, sticky='w')
            entry = ttk.Entry(win_frame)
            entry.grid(row=i-1, column=1, sticky='ew', padx=2, pady=1)
            self.window_entries[i] = entry

    def add_piecewise_row(self, day, frame, from_value):
        row = len(frame.grid_slaves()) // 4
        # day label on first row
        if row == 0:
            ttk.Label(frame, text=f"{day}:").grid(row=0, column=0, sticky='w', padx=(0,10))
        else:
            ttk.Label(frame, text="").grid(row=row, column=0)
        # from entry (disabled)
        from_var = tk.StringVar(value=str(from_value))
        ttk.Entry(frame, textvariable=from_var, width=5, state='disabled').grid(row=row, column=1, padx=5)
        # to entry
        to_var = tk.StringVar()
        to_ent = ttk.Entry(frame, textvariable=to_var, width=5)
        to_ent.grid(row=row, column=2, padx=5)
        to_ent.bind('<Return>', lambda e, d=day, fv=from_var, tv=to_var, f=frame: self.on_to_enter(d, fv, tv, f))
        # utility entry
        util_var = tk.StringVar()
        util_ent = ttk.Entry(frame, textvariable=util_var, width=8)
        util_ent.grid(row=row, column=3, padx=5)

    def on_to_enter(self, day, from_var, to_var, frame):
        try:
            start = float(from_var.get())
            end = float(to_var.get())
        except ValueError:
            return
        # find utility value in same row
        util_val = None
        info = to_var
        for w in frame.winfo_children():
            g = w.grid_info()
            if g['row'] == frame.grid_size()[1]-1 and g['column']==3:
                util_val = w.get()
        # store tuple in util_entries
        self.util_entries[day].append((end, util_val))
        # disable to_ent
        to_var.set(str(end))
        to_ent = frame.nametowidget(to_var._name)
        to_ent.config(state='disabled')
        # add next row
        self.add_piecewise_row(day, frame, from_value=end)

    def parse_window(self, num_slots, entries_dict):
        slots_per_day = num_slots // 7
        slot_minutes = (7*24*60) // num_slots
        idxs = []
        for day, entry in entries_dict.items():
            raw = entry.get().strip()
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

    def save_activity(self):
        t = self.type_var.get()
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showwarning(self.texts['error'], self.texts['name_required'])
            return
        sel = self.act_list.curselection()
        if sel:
            del self.activities[sel[0]]
            self.act_list.delete(sel)
        if t == self.texts['fixed']:
            num = {'1 hora':168, '30 minutos':336, '15 minutos':672}[self.gran_var.get()]
            slots = self.parse_window(num, self.slots_entries)
            act = fixedActivity(name, slots)
        else:
            mn = int(getattr(self, 'min_entry', None).get() or 0) if hasattr(self, 'min_entry') else 0
            lmin = int(getattr(self, 'lmin_entry', None).get() or 1) if hasattr(self, 'lmin_entry') else 1
            num = {'1 hora':168, '30 minutos':336, '15 minutos':672}[self.gran_var.get()]
            mx = int(getattr(self, 'max_entry', None).get() or num) if hasattr(self, 'max_entry') else num
            lmax = int(getattr(self, 'lmax_entry', None).get() or num) if hasattr(self, 'lmax_entry') else num

            window = self.parse_window(num, self.window_entries)
            utility = self.calculate_utility(self.piecewise_util, self.const_util)


            act = variableActivity(name, mn, mx, window, lmin, lmax)
            if hasattr(self, 'const_util') and self.adv_var.get():
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
        if not sel: return
        act = self.activities[sel[0]]
        num = {'1 hora':168, '30 minutos':336, '15 minutos':672}[self.gran_var.get()]
        if isinstance(act, fixedActivity):
            self.type_var.set(self.texts['fixed'])
            self.build_form()
            self.name_entry.delete(0,'end'); self.name_entry.insert(0, act.name)
            for i, entry in self.slots_entries.items():
                # reconstruir de índices a periodos si se requiere
                entry.delete(0,'end')
        else:
            self.type_var.set(self.texts['variable'])
            self.build_form()
            self.name_entry.delete(0,'end'); self.name_entry.insert(0, act.name)
            self.min_entry.delete(0,'end'); self.min_entry.insert(0, str(act.weekly_min))
            self.max_entry.delete(0,'end'); self.max_entry.insert(0, str(act.weekly_max))
            self.lmin_entry.delete(0,'end'); self.lmin_entry.insert(0, str(act.lmin))
            self.lmax_entry.delete(0,'end'); self.lmax_entry.insert(0, str(act.lmax))
            self.adv_var.set(bool(act.allowed_ts))
            self.build_advanced()
            for i, entry in self.window_entries.items():
                entry.delete(0,'end')

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
