#!/usr/bin/env python3
"""
Agape Church Directory — PDF to CSV Converter
Drag & drop or browse for filled PDF forms, preview extracted data, export CSV.
Requires: pip install pypdf
"""

import sys
import os
import csv
import re
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime

try:
    from pypdf import PdfReader, PdfWriter
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pypdf', '-q'])
    from pypdf import PdfReader, PdfWriter

# ── CSV columns (must match ChurchCRM template) ───────────────────────────────
CSV_COLUMNS = [
    'FamilyID', 'FamilyRole', 'Title', 'FirstName', 'MiddleName', 'LastName',
    'Suffix', 'Gender', 'Envelope', 'Address1', 'Address2', 'City', 'State',
    'Zip', 'Country', 'HomePhone', 'WorkPhone', 'MobilePhone', 'Email',
    'WorkEmail', 'BirthDate', 'MembershipDate', 'WeddingDate',
    'PersonCustom:Married:', 'PersonCustom:Deceased:',
    'PersonCustom:Occupation:', 'FamilyCustom:CustomField1',
]

# ── Colours ───────────────────────────────────────────────────────────────────
NAVY   = '#1a3560'
GOLD   = '#c8a951'
WHITE  = '#ffffff'
LGRAY  = '#f4f4f6'
MGRAY  = '#cccccc'
GREEN  = '#2e7d32'
LGREEN = '#e8f5e9'
RED    = '#c62828'
LRED   = '#ffebee'
BLUE   = '#1565c0'
LBLUE  = '#e3f2fd'


# ── Conversion logic (same as cli script) ─────────────────────────────────────
def normalise_date(raw):
    if not raw or not raw.strip():
        return ''
    raw = raw.strip().replace('/', '-')
    for fmt in ('%m-%d-%Y', '%Y-%m-%d', '%m-%d-%y', '%d-%m-%Y'):
        try:
            return datetime.strptime(raw, fmt).strftime('%Y-%m-%d')
        except ValueError:
            continue
    return raw

def normalise_phone(raw):
    if not raw or not raw.strip():
        return ''
    digits = re.sub(r'\D', '', raw)
    if len(digits) == 10:
        return f'({digits[:3]}) {digits[3:6]}-{digits[6:]}'
    return raw.strip()

def extract_fields(pdf_path):
    reader = PdfReader(pdf_path)
    fields = {}
    raw = reader.get_fields() or {}
    for name, field in raw.items():
        val = field.get('/V', '')
        fields[name] = '' if (not val or str(val) in ('/Off', 'Off')) else str(val).strip()
    return fields

def person_row(family_id, title, first, middle, last, gender,
               birthdate, email, mobile, address1, address2,
               city, state, zip_code, home_phone, wedding_date,
               married_custom='', family_custom=''):
    return {
        'FamilyID':               family_id,
        'Title':                  title,
        'FirstName':              first,
        'MiddleName':             middle,
        'LastName':               last,
        'Suffix':                 '',
        'Gender':                 gender,
        'Envelope':               '',
        'Address1':               address1,
        'Address2':               address2,
        'City':                   city,
        'State':                  state,
        'Zip':                    zip_code,
        'Country':                'Canada',
        'HomePhone':              home_phone,
        'WorkPhone':              '',
        'MobilePhone':            mobile,
        'Email':                  email,
        'WorkEmail':              '',
        'BirthDate':              normalise_date(birthdate),
        'MembershipDate':         '',
        'WeddingDate':            normalise_date(wedding_date),
        'PersonCustom:Married:':  married_custom,
        'FamilyCustom:CustomField1': family_custom,
    }

def convert_pdf(pdf_path, family_id=1001):
    import re
    f = extract_fields(pdf_path)
    fam_last    = f.get('family_last_name','').strip()
    addr1       = f.get('address1','').strip()
    addr2       = f.get('address2','').strip()
    city        = f.get('city','').strip()
    state       = f.get('state','').strip()
    zip_        = f.get('zip','').strip()
    country     = f.get('country','US').strip() or 'US'
    home_ph     = normalise_phone(f.get('home_phone',''))
    wedding     = f.get('wedding_date','').strip()
    occupn      = f.get('occupation','').strip()
    notes       = f.get('notes','').strip()
    fam_custom  = '; '.join(filter(None, [occupn, notes]))

    def mkrow(role, title, first, middle, last, gender, birthdate,
              email='', mobile='', wedding_date='', married='',
              deceased='', occupation=''):
        return {
            'FamilyID': family_id, 'FamilyRole': role, 'Title': title,
            'FirstName': first, 'MiddleName': middle, 'LastName': last,
            'Suffix': '', 'Gender': gender, 'Envelope': '',
            'Address1': addr1, 'Address2': addr2, 'City': city,
            'State': state, 'Zip': zip_, 'Country': country,
            'HomePhone': home_ph, 'WorkPhone': '', 'MobilePhone': mobile,
            'Email': email, 'WorkEmail': '',
            'BirthDate': normalise_date(birthdate), 'MembershipDate': '',
            'WeddingDate': normalise_date(wedding_date),
            'PersonCustom:Married:': married,
            'PersonCustom:Deceased:': deceased,
            'PersonCustom:Occupation:': occupation,
            'FamilyCustom:CustomField1': fam_custom,
        }

    rows = []

    hf = f.get('head_first','').strip()
    if hf:
        rows.append(mkrow('Head of Household','Mr', hf,
            f.get('head_middle','').strip(),
            f.get('head_last','').strip() or fam_last, 'Male',
            f.get('head_birthdate',''),
            email=f.get('head_email','').strip(),
            mobile=normalise_phone(f.get('head_mobile','')),
            wedding_date=wedding, occupation=occupn))

    sf = f.get('spouse_first','').strip()
    if sf:
        rows.append(mkrow('Spouse','Mrs', sf,
            f.get('spouse_middle','').strip(),
            f.get('spouse_last','').strip() or fam_last, 'Female',
            f.get('spouse_birthdate',''),
            email=f.get('spouse_email','').strip(),
            mobile=normalise_phone(f.get('spouse_mobile','')),
            wedding_date=wedding))

    for prefix, role, title, gender in [
        ('pat_gf','paternalGrandfather','Mr','Male'),
        ('pat_gm','paternalGrandmother','Mrs','Female'),
        ('mat_gf','maternalGrandfather','Mr','Male'),
        ('mat_gm','maternalGrandmother','Mrs','Female'),
    ]:
        gf = f.get(f'{prefix}_first','').strip()
        if not gf: continue
        rows.append(mkrow(role, title, gf,
            f.get(f'{prefix}_middle','').strip(),
            f.get(f'{prefix}_last','').strip() or fam_last,
            gender, f.get(f'{prefix}_birthdate',''),
            deceased=f.get(f'{prefix}_deceased','').strip()))

    for i in range(1, 16):
        p = f'child{i}'
        cf = f.get(f'{p}_first','').strip()
        if not cf: continue
        rows.append(mkrow('Child','', cf,
            f.get(f'{p}_middle','').strip(), fam_last, '',
            f.get(f'{p}_birthdate',''),
            married=f.get(f'{p}_spouse','').strip()))

    return rows, fam_last


# ═════════════════════════════════════════════════════════════════════════════
# GUI
# ═════════════════════════════════════════════════════════════════════════════
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Agape Directory — PDF to CSV Converter')
        self.geometry('900x680')
        self.minsize(750, 550)
        self.configure(bg=LGRAY)
        self.resizable(True, True)

        self.pdf_files  = []   # list of (path, rows, family_name)
        self.next_fam_id = 1001

        self._build_ui()
        self._enable_drop()

    # ── Build UI ──────────────────────────────────────────────────────────────
    def _build_ui(self):
        # Header bar
        hdr = tk.Frame(self, bg=NAVY, height=56)
        hdr.pack(fill='x')
        hdr.pack_propagate(False)
        tk.Label(hdr, text='Agape Church Directory', bg=NAVY, fg=WHITE,
                 font=('Arial', 15, 'bold')).pack(side='left', padx=16, pady=12)
        tk.Label(hdr, text='PDF → CSV Converter', bg=NAVY, fg=GOLD,
                 font=('Arial', 11)).pack(side='left', padx=0, pady=12)

        # Gold rule
        tk.Frame(self, bg=GOLD, height=3).pack(fill='x')

        # Main area (left panel + right preview)
        body = tk.Frame(self, bg=LGRAY)
        body.pack(fill='both', expand=True, padx=12, pady=10)

        # ── Left panel ────────────────────────────────────────
        left = tk.Frame(body, bg=LGRAY, width=280)
        left.pack(side='left', fill='y', padx=(0, 10))
        left.pack_propagate(False)

        # Drop zone
        self.drop_frame = tk.LabelFrame(left, text=' Drop PDFs Here ',
            bg=WHITE, fg=NAVY, font=('Arial', 9, 'bold'),
            bd=2, relief='groove')
        self.drop_frame.pack(fill='x', pady=(0, 8))

        self.drop_label = tk.Label(self.drop_frame,
            text='⬇\n\nDrag & drop\nfilled PDF forms\nhere\n\nor',
            bg=WHITE, fg='#888888', font=('Arial', 10), pady=20)
        self.drop_label.pack()

        tk.Button(self.drop_frame, text='Browse for PDFs…',
            command=self._browse, bg=NAVY, fg=WHITE,
            font=('Arial', 9, 'bold'), bd=0, padx=10, pady=6,
            cursor='hand2', activebackground=BLUE, activeforeground=WHITE,
        ).pack(pady=(0, 12))

        # File list
        tk.Label(left, text='Queued Files', bg=LGRAY, fg=NAVY,
                 font=('Arial', 9, 'bold')).pack(anchor='w')

        list_frame = tk.Frame(left, bg=WHITE, bd=1, relief='solid')
        list_frame.pack(fill='both', expand=True, pady=(4, 8))

        self.file_listbox = tk.Listbox(list_frame, bg=WHITE, fg='#333333',
            font=('Arial', 9), selectbackground=LBLUE, selectforeground=BLUE,
            bd=0, highlightthickness=0, activestyle='none')
        self.file_listbox.pack(fill='both', expand=True, padx=4, pady=4)
        self.file_listbox.bind('<<ListboxSelect>>', self._on_select)

        btn_row = tk.Frame(left, bg=LGRAY)
        btn_row.pack(fill='x')
        tk.Button(btn_row, text='Remove', command=self._remove_selected,
            bg='#e53935', fg=WHITE, font=('Arial', 8, 'bold'),
            bd=0, padx=8, pady=4, cursor='hand2').pack(side='left')
        tk.Button(btn_row, text='Clear All', command=self._clear_all,
            bg='#757575', fg=WHITE, font=('Arial', 8, 'bold'),
            bd=0, padx=8, pady=4, cursor='hand2').pack(side='left', padx=6)

        # ── Right panel ───────────────────────────────────────
        right = tk.Frame(body, bg=LGRAY)
        right.pack(side='left', fill='both', expand=True)

        tk.Label(right, text='Preview — Extracted Data', bg=LGRAY, fg=NAVY,
                 font=('Arial', 9, 'bold')).pack(anchor='w')

        # Treeview
        tree_frame = tk.Frame(right, bg=WHITE, bd=1, relief='solid')
        tree_frame.pack(fill='both', expand=True, pady=(4, 8))

        preview_cols = ('Role', 'First', 'Last', 'BirthDate', 'Email', 'Phone', 'Married')
        self.tree = ttk.Treeview(tree_frame, columns=preview_cols,
                                 show='headings', height=15)

        col_widths = {'Role':70, 'First':90, 'Last':90,
                      'BirthDate':90, 'Email':150, 'Phone':110, 'Married':110}
        for col in preview_cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=col_widths[col], anchor='w')

        self.tree.tag_configure('head',   background='#e3f2fd')
        self.tree.tag_configure('spouse', background='#fce4ec')
        self.tree.tag_configure('child',  background=LGREEN)
        self.tree.tag_configure('sep',    background='#eeeeee')

        vsb = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side='right', fill='y')
        hsb.pack(side='bottom', fill='x')
        self.tree.pack(fill='both', expand=True)

        # Status bar
        self.status_var = tk.StringVar(value='Ready — add PDF forms to get started.')
        status_bar = tk.Frame(right, bg='#e0e0e0', height=24)
        status_bar.pack(fill='x')
        status_bar.pack_propagate(False)
        tk.Label(status_bar, textvariable=self.status_var,
                 bg='#e0e0e0', fg='#555555', font=('Arial', 8),
                 anchor='w').pack(fill='x', padx=8, pady=4)

        # Export buttons
        btn_bar = tk.Frame(right, bg=LGRAY)
        btn_bar.pack(fill='x', pady=(4, 0))

        tk.Button(btn_bar, text='⬇  Export Selected as CSV',
            command=lambda: self._export(selected_only=True),
            bg=BLUE, fg=WHITE, font=('Arial', 10, 'bold'),
            bd=0, padx=14, pady=8, cursor='hand2',
            activebackground=NAVY, activeforeground=WHITE,
        ).pack(side='left')

        tk.Button(btn_bar, text='⬇  Export ALL as Single CSV',
            command=lambda: self._export(selected_only=False),
            bg=GREEN, fg=WHITE, font=('Arial', 10, 'bold'),
            bd=0, padx=14, pady=8, cursor='hand2',
            activebackground='#1b5e20', activeforeground=WHITE,
        ).pack(side='left', padx=8)

        tk.Button(btn_bar, text='?  Help',
            command=self._show_help,
            bg='#616161', fg=WHITE, font=('Arial', 9),
            bd=0, padx=10, pady=8, cursor='hand2',
        ).pack(side='right')

    # ── Drag & drop (Windows + Linux) ─────────────────────────────────────────
    def _enable_drop(self):
        try:
            self.drop_frame.drop_target_register('DND_Files')  # type: ignore
            self.drop_frame.dnd_bind('<<Drop>>', self._on_drop)
            self.drop_label.drop_target_register('DND_Files')  # type: ignore
            self.drop_label.dnd_bind('<<Drop>>', self._on_drop)
        except Exception:
            pass  # tkinterdnd2 not installed — browse still works

    def _on_drop(self, event):
        paths = self.tk.splitlist(event.data)
        for p in paths:
            if p.lower().endswith('.pdf'):
                self._add_pdf(p)

    # ── File management ───────────────────────────────────────────────────────
    def _browse(self):
        paths = filedialog.askopenfilenames(
            title='Select filled PDF forms',
            filetypes=[('PDF files', '*.pdf'), ('All files', '*.*')],
        )
        for p in paths:
            self._add_pdf(p)

    def _add_pdf(self, path):
        if any(p == path for p, _, _ in self.pdf_files):
            return  # already added
        self._set_status(f'Reading {os.path.basename(path)}…')
        self.update_idletasks()
        try:
            rows, family_name = convert_pdf(path, self.next_fam_id)
            if not rows:
                messagebox.showwarning('Empty Form',
                    f'No data found in:\n{os.path.basename(path)}\n\n'
                    'Make sure the PDF was filled and saved.')
                self._set_status('Ready.')
                return
            self.pdf_files.append((path, rows, family_name or os.path.basename(path)))
            self.next_fam_id += 1
            name = family_name or os.path.basename(path)
            self.file_listbox.insert('end', f'  {name}  ({len(rows)} people)')
            self.file_listbox.selection_clear(0, 'end')
            self.file_listbox.selection_set('end')
            self._refresh_preview()
            self._set_status(
                f'Loaded {os.path.basename(path)} — {len(rows)} person(s) extracted.')
        except Exception as e:
            messagebox.showerror('Error', f'Could not read PDF:\n{e}')
            self._set_status('Error reading file.')

    def _remove_selected(self):
        sel = self.file_listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        self.file_listbox.delete(idx)
        self.pdf_files.pop(idx)
        self.tree.delete(*self.tree.get_children())
        self._set_status('File removed.')

    def _clear_all(self):
        self.file_listbox.delete(0, 'end')
        self.pdf_files.clear()
        self.tree.delete(*self.tree.get_children())
        self.next_fam_id = 1001
        self._set_status('Cleared.')

    # ── Preview ───────────────────────────────────────────────────────────────
    def _on_select(self, event):
        self._refresh_preview()

    def _refresh_preview(self):
        self.tree.delete(*self.tree.get_children())
        sel = self.file_listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        _, rows, family_name = self.pdf_files[idx]

        self.tree.insert('', 'end',
            values=(f'── {family_name} Family ──', '', '', '', '', '', ''),
            tags=('sep',))

        for row in rows:
            fr = row.get('FamilyRole','')
            if fr == 'Head of Household':
                role = 'Head'; tag = 'head'
            elif fr == 'Spouse':
                role = 'Spouse'; tag = 'spouse'
            elif 'Grand' in fr or 'grandfather' in fr or 'grandmother' in fr:
                role = fr; tag = 'head'
            else:
                role = 'Child'; tag = 'child'

            self.tree.insert('', 'end', tags=(tag,), values=(
                role,
                row['FirstName'],
                row['LastName'],
                row['BirthDate'],
                row['Email'] or row['MobilePhone'],
                row['HomePhone'],
                row['PersonCustom:Married:'] or row['PersonCustom:Deceased:'],
            ))

    # ── Export ────────────────────────────────────────────────────────────────
    def _export(self, selected_only=False):
        if not self.pdf_files:
            messagebox.showinfo('No Files', 'Add some PDF forms first.')
            return

        if selected_only:
            sel = self.file_listbox.curselection()
            if not sel:
                messagebox.showinfo('Nothing Selected', 'Select a file in the list first.')
                return
            to_export = [self.pdf_files[sel[0]]]
            default_name = self.pdf_files[sel[0]][2] + '.csv'
        else:
            to_export = self.pdf_files
            default_name = 'Agape_Directory_Import.csv'

        out_path = filedialog.asksaveasfilename(
            title='Save CSV',
            defaultextension='.csv',
            initialfile=default_name,
            filetypes=[('CSV files', '*.csv'), ('All files', '*.*')],
        )
        if not out_path:
            return

        all_rows = []
        for _, rows, _ in to_export:
            all_rows.extend(rows)

        with open(out_path, 'w', newline='', encoding='utf-8') as fh:
            writer = csv.DictWriter(fh, fieldnames=CSV_COLUMNS)
            writer.writeheader()
            writer.writerows(all_rows)

        self._set_status(
            f'Exported {len(all_rows)} person(s) → {os.path.basename(out_path)}')
        messagebox.showinfo('Export Complete',
            f'Exported {len(all_rows)} person(s) to:\n{out_path}\n\n'
            'Upload this file to ChurchCRM:\n'
            'Admin ⚙ → CSV Import → Upload')

    # ── Status ────────────────────────────────────────────────────────────────
    def _set_status(self, msg):
        self.status_var.set(msg)
        self.update_idletasks()

    # ── Help ──────────────────────────────────────────────────────────────────
    def _show_help(self):
        win = tk.Toplevel(self)
        win.title('Help')
        win.geometry('480x380')
        win.configure(bg=WHITE)
        win.resizable(False, False)

        tk.Label(win, text='How to Use', bg=NAVY, fg=WHITE,
                 font=('Arial', 12, 'bold'), pady=10).pack(fill='x')

        help_text = (
            "STEP 1 — Collect filled PDFs\n"
            "  Hand out the Agape Church Directory PDF form.\n"
            "  Families fill it in and return it (email or print).\n\n"
            "STEP 2 — Add PDFs to this app\n"
            "  Drag & drop PDF files onto the left panel,\n"
            "  or click 'Browse for PDFs…'\n\n"
            "STEP 3 — Review the preview\n"
            "  Click each file in the list to preview the people\n"
            "  that will be imported.\n\n"
            "STEP 4 — Export CSV\n"
            "  • 'Export Selected' — one family at a time\n"
            "  • 'Export ALL' — all families in one CSV file\n\n"
            "STEP 5 — Import into ChurchCRM\n"
            "  Admin ⚙ → CSV Import → choose your CSV file\n"
            "  Tick 'Generate Family records by Last Name + Address'\n\n"
            "NOTES\n"
            "  • Children's spouse name → PersonCustom:Married:\n"
            "  • Last name, address, phone auto-filled for all members\n"
            "  • Dates normalised to YYYY-MM-DD automatically\n"
        )
        txt = tk.Text(win, bg=WHITE, fg='#333333', font=('Arial', 9),
                      bd=0, padx=16, pady=12, wrap='word',
                      highlightthickness=0)
        txt.insert('1.0', help_text)
        txt.config(state='disabled')
        txt.pack(fill='both', expand=True)

        tk.Button(win, text='Close', command=win.destroy,
                  bg=NAVY, fg=WHITE, font=('Arial', 9, 'bold'),
                  bd=0, padx=16, pady=6).pack(pady=8)


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == '__main__':
    # Try to enable drag & drop via tkinterdnd2 if available
    try:
        from tkinterdnd2 import TkinterDnD
        class App(App, TkinterDnD.Tk): pass  # type: ignore
    except ImportError:
        pass  # drag & drop unavailable — browse still works

    app = App()
    app.mainloop()
