import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from database.policy_queries import get_all_policies, purchase_policy, get_user_policies
from database.claim_queries import add_claim, get_user_claims, delete_claim_by_id
from utils.hash_utils import hash_password
from database.connection import get_connection


def open_user_dashboard(user_id, username=None):

    if username is None:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM USERS WHERE user_id = %s", (user_id,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        username = row[0] if row else "User"

    current_view = {"type": None, "data": []}

    def clear_table():
        for row in tree.get_children():
            tree.delete(row)

    def populate_table(columns, data, claim_view=False):
        clear_table()
        tree["columns"] = columns
        tree["show"] = "headings"
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=160)
        for row in data:
            if claim_view and len(row) >= 4:
                tree.insert("", "end", values=row, tags=(row[3],))
            else:
                tree.insert("", "end", values=row)

    # =============================
    # Statistics
    # =============================

    def update_statistics():
        policies = get_user_policies(user_id)
        claims = get_user_claims(user_id)

        total_policies_label.config(text="My Policies: {}".format(len(policies)))
        total_claims_label.config(text="My Claims: {}".format(len(claims)))

        pending = sum(1 for c in claims if c[3] == "Pending")
        approved = sum(1 for c in claims if c[3] == "Approved")
        pending_label.config(text="Pending: {}".format(pending))

        invested = sum(float(p[2]) for p in policies)
        total_premium_label.config(text="Invested: Rs.{:.2f}".format(invested))

        success_rate = (approved / len(claims) * 100) if claims else 0.0
        success_label.config(text="Success: {:.1f}%".format(success_rate))

    # =============================
    # Views
    # =============================

    def view_my_policies():
        policies = get_user_policies(user_id)
        current_view["type"] = "policies"
        current_view["data"] = policies
        populate_table(("Purchase ID", "Policy Name", "Premium", "Start Date"), policies)
        section_label.config(text="My Policies")
        status_label.config(text="")
        update_statistics()

    def view_my_claims():
        claims = get_user_claims(user_id)
        current_view["type"] = "claims"
        current_view["data"] = claims
        populate_table(("Claim ID", "Policy Name", "Amount", "Status"), claims, claim_view=True)
        section_label.config(text="My Claims")
        status_label.config(text="")
        update_statistics()

    # =============================
    # Search
    # =============================

    def search_data():
        query = search_entry.get().lower().strip()
        if not query:
            if current_view["type"] == "policies":
                view_my_policies()
            elif current_view["type"] == "claims":
                view_my_claims()
            return
        filtered = [row for row in current_view["data"]
                    if any(query in str(item).lower() for item in row)]
        if current_view["type"] == "policies":
            populate_table(("Purchase ID", "Policy Name", "Premium", "Start Date"), filtered)
        elif current_view["type"] == "claims":
            populate_table(("Claim ID", "Policy Name", "Amount", "Status"), filtered, claim_view=True)

    # =============================
    # Purchase Policy
    # =============================

    def open_purchase_window():
        policies = get_all_policies()
        if not policies:
            messagebox.showinfo("Info", "No policies available!")
            return

        win = tk.Toplevel(root)
        win.title("Purchase Policy")
        win.geometry("400x340")
        win.configure(bg="#0f1117")
        win.resizable(False, False)

        tk.Frame(win, bg="#4f8ef7", height=4).pack(fill="x")
        tk.Label(win, text="Purchase Policy",
                 bg="#0f1117", fg="white",
                 font=("Helvetica", 13, "bold")).pack(pady=(20, 15))

        form = tk.Frame(win, bg="#0f1117")
        form.pack(padx=30, fill="x")

        tk.Label(form, text="SELECT POLICY", bg="#0f1117", fg="#6b7280",
                 font=("Helvetica", 9, "bold")).pack(anchor="w")

        policy_dict = {"{} - Rs.{}".format(p[1], p[2]): p[0] for p in policies}
        policy_options = list(policy_dict.keys())

        policy_combo = ttk.Combobox(form, values=policy_options, state="readonly",
                                    font=("Helvetica", 10))
        policy_combo.set(policy_options[0])
        policy_combo.pack(fill="x", pady=(4, 14), ipady=5)

        tk.Label(form, text="START DATE (DD-MM-YYYY)", bg="#0f1117", fg="#6b7280",
                 font=("Helvetica", 9, "bold")).pack(anchor="w")
        date_entry = tk.Entry(form, bg="#1a1d27", fg="white",
                              insertbackground="white", relief="flat",
                              font=("Helvetica", 11),
                              highlightthickness=1,
                              highlightbackground="#2e3250",
                              highlightcolor="#4f8ef7")
        date_entry.pack(fill="x", ipady=7, pady=(4, 20))

        def purchase():
            selected = policy_combo.get()
            date_str = date_entry.get().strip()
            if not selected or not date_str:
                messagebox.showwarning("Warning", "All fields required!")
                return
            try:
                date_obj = datetime.strptime(date_str, "%d-%m-%Y")
                date_db = date_obj.strftime("%Y-%m-%d")
            except ValueError:
                messagebox.showwarning("Warning", "Date must be DD-MM-YYYY format!")
                return
            policy_id = policy_dict[selected]
            policy_name = selected.split(" - ")[0]
            existing = get_user_policies(user_id)
            for p in existing:
                if p[1] == policy_name:
                    messagebox.showwarning("Warning", "You already have this policy!")
                    return
            purchase_policy(user_id, policy_id, date_db)
            messagebox.showinfo("Success", "Policy Purchased Successfully!")
            win.destroy()
            view_my_policies()

        btn = tk.Frame(form, bg="#4f8ef7", cursor="hand2")
        btn.pack(fill="x")
        btn_lbl = tk.Label(btn, text="Purchase", bg="#4f8ef7", fg="white",
                           font=("Helvetica", 11, "bold"), pady=10)
        btn_lbl.pack(fill="x")
        for w in (btn, btn_lbl):
            w.bind("<Enter>", lambda e: [btn.config(bg="#3a74d4"), btn_lbl.config(bg="#3a74d4")])
            w.bind("<Leave>", lambda e: [btn.config(bg="#4f8ef7"), btn_lbl.config(bg="#4f8ef7")])
            w.bind("<Button-1>", lambda e: purchase())

    # =============================
    # Apply Claim
    # =============================

    def open_claim_window():
        policies = get_user_policies(user_id)
        if not policies:
            messagebox.showinfo("Info", "You have no policies to claim on!")
            return

        win = tk.Toplevel(root)
        win.title("Apply Claim")
        win.geometry("400x340")
        win.configure(bg="#0f1117")
        win.resizable(False, False)

        tk.Frame(win, bg="#4f8ef7", height=4).pack(fill="x")
        tk.Label(win, text="Apply Claim",
                 bg="#0f1117", fg="white",
                 font=("Helvetica", 13, "bold")).pack(pady=(20, 15))

        form = tk.Frame(win, bg="#0f1117")
        form.pack(padx=30, fill="x")

        tk.Label(form, text="SELECT POLICY", bg="#0f1117", fg="#6b7280",
                 font=("Helvetica", 9, "bold")).pack(anchor="w")

        policy_dict = {"{} (ID:{})".format(p[1], p[0]): p[0] for p in policies}
        policy_options = list(policy_dict.keys())

        policy_combo = ttk.Combobox(form, values=policy_options, state="readonly",
                                    font=("Helvetica", 10))
        policy_combo.set(policy_options[0])
        policy_combo.pack(fill="x", pady=(4, 14), ipady=5)

        tk.Label(form, text="CLAIM AMOUNT", bg="#0f1117", fg="#6b7280",
                 font=("Helvetica", 9, "bold")).pack(anchor="w")
        amount_entry = tk.Entry(form, bg="#1a1d27", fg="white",
                                insertbackground="white", relief="flat",
                                font=("Helvetica", 11),
                                highlightthickness=1,
                                highlightbackground="#2e3250",
                                highlightcolor="#4f8ef7")
        amount_entry.pack(fill="x", ipady=7, pady=(4, 20))

        def submit_claim():
            selected = policy_combo.get()
            amount = amount_entry.get().strip()
            if not selected or not amount:
                messagebox.showwarning("Warning", "All fields required!")
                return
            try:
                amount_val = float(amount)
                purchase_id = policy_dict[selected]
                add_claim(purchase_id, amount_val)
                messagebox.showinfo("Success", "Claim Submitted Successfully!")
                win.destroy()
                view_my_claims()
            except ValueError:
                messagebox.showwarning("Warning", "Amount must be a number!")

        btn = tk.Frame(form, bg="#4f8ef7", cursor="hand2")
        btn.pack(fill="x")
        btn_lbl = tk.Label(btn, text="Submit Claim", bg="#4f8ef7", fg="white",
                           font=("Helvetica", 11, "bold"), pady=10)
        btn_lbl.pack(fill="x")
        for w in (btn, btn_lbl):
            w.bind("<Enter>", lambda e: [btn.config(bg="#3a74d4"), btn_lbl.config(bg="#3a74d4")])
            w.bind("<Leave>", lambda e: [btn.config(bg="#4f8ef7"), btn_lbl.config(bg="#4f8ef7")])
            w.bind("<Button-1>", lambda e: submit_claim())

    # =============================
    # Delete Pending Claim
    # =============================

    def delete_claim():
        if current_view["type"] != "claims":
            status_label.config(text="⚠  Switch to 'My Claims' view first!")
            return
        selected = tree.selection()
        if not selected:
            status_label.config(text="⚠  Select a claim first!")
            return
        values = tree.item(selected[0])["values"]
        if not values or len(values) < 4:
            return
        claim_id = values[0]
        status = values[3]
        if status != "Pending":
            status_label.config(text="⚠  Only Pending claims can be deleted!")
            return
        status_label.config(text="")
        confirm = messagebox.askyesno("Confirm Delete", "Delete this pending claim?")
        if not confirm:
            return
        try:
            delete_claim_by_id(claim_id)
            messagebox.showinfo("Success", "Claim Deleted!")
            view_my_claims()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    # =============================
    # Change Password
    # =============================

    def open_change_password():
        win = tk.Toplevel(root)
        win.title("Change Password")
        win.geometry("380x320")
        win.configure(bg="#0f1117")
        win.resizable(False, False)

        tk.Frame(win, bg="#4f8ef7", height=4).pack(fill="x")
        tk.Label(win, text="Change Password",
                 bg="#0f1117", fg="white",
                 font=("Helvetica", 13, "bold")).pack(pady=(20, 15))

        form = tk.Frame(win, bg="#0f1117")
        form.pack(padx=30, fill="x")

        tk.Label(form, text="CURRENT PASSWORD", bg="#0f1117", fg="#6b7280",
                 font=("Helvetica", 9, "bold")).pack(anchor="w")
        current_entry = tk.Entry(form, show="*", bg="#1a1d27", fg="white",
                                 insertbackground="white", relief="flat",
                                 font=("Helvetica", 11),
                                 highlightthickness=1,
                                 highlightbackground="#2e3250",
                                 highlightcolor="#4f8ef7")
        current_entry.pack(fill="x", ipady=7, pady=(4, 14))

        tk.Label(form, text="NEW PASSWORD", bg="#0f1117", fg="#6b7280",
                 font=("Helvetica", 9, "bold")).pack(anchor="w")
        new_entry = tk.Entry(form, show="*", bg="#1a1d27", fg="white",
                             insertbackground="white", relief="flat",
                             font=("Helvetica", 11),
                             highlightthickness=1,
                             highlightbackground="#2e3250",
                             highlightcolor="#4f8ef7")
        new_entry.pack(fill="x", ipady=7, pady=(4, 20))

        def change():
            current_pass = current_entry.get()
            new_pass = new_entry.get()
            if not current_pass or not new_pass:
                messagebox.showwarning("Warning", "All fields required!")
                return
            if len(new_pass) < 4:
                messagebox.showwarning("Warning", "Password must be at least 4 characters!")
                return
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT user_id FROM USERS WHERE user_id = %s AND password = %s",
                    (user_id, hash_password(current_pass))
                )
                result = cursor.fetchone()
                cursor.close()
                conn.close()
                if not result:
                    messagebox.showwarning("Warning", "Current password is incorrect!")
                    return
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE USERS SET password = %s WHERE user_id = %s",
                    (hash_password(new_pass), user_id)
                )
                conn.commit()
                cursor.close()
                conn.close()
                messagebox.showinfo("Success", "Password Updated Successfully!")
                win.destroy()
            except Exception as e:
                messagebox.showerror("Database Error", str(e))

        btn = tk.Frame(form, bg="#4f8ef7", cursor="hand2")
        btn.pack(fill="x")
        btn_lbl = tk.Label(btn, text="Update Password", bg="#4f8ef7", fg="white",
                           font=("Helvetica", 11, "bold"), pady=10)
        btn_lbl.pack(fill="x")
        for w in (btn, btn_lbl):
            w.bind("<Enter>", lambda e: [btn.config(bg="#3a74d4"), btn_lbl.config(bg="#3a74d4")])
            w.bind("<Leave>", lambda e: [btn.config(bg="#4f8ef7"), btn_lbl.config(bg="#4f8ef7")])
            w.bind("<Button-1>", lambda e: change())

    def logout():
        root.destroy()
        from gui.login import start_login
        start_login()

    # ==============================
    # Main Window
    # ==============================
    root = tk.Tk()
    root.title("User Dashboard")
    root.geometry("1150x700")
    root.configure(bg="#0f1117")

    style = ttk.Style()
    style.theme_use("clam")

    style.configure("Treeview",
                    background="#1a1d27",
                    foreground="white",
                    fieldbackground="#1a1d27",
                    rowheight=30,
                    font=("Helvetica", 10))
    style.configure("Treeview.Heading",
                    background="#2e3250",
                    foreground="#7ec8e3",
                    font=("Helvetica", 10, "bold"),
                    relief="flat")
    style.map("Treeview",
              background=[("selected", "#4f8ef7")],
              foreground=[("selected", "white")])

    # Dark combobox dropdown list
    root.option_add("*TCombobox*Listbox.background", "#1a1d27")
    root.option_add("*TCombobox*Listbox.foreground", "white")
    root.option_add("*TCombobox*Listbox.selectBackground", "#4f8ef7")
    root.option_add("*TCombobox*Listbox.selectForeground", "white")
    root.option_add("*TCombobox*Listbox.font", "Helvetica 10")

    # ── Sidebar button helper ──
    def make_sidebar_btn(parent, text, bg, fg, hover_bg, command):
        f = tk.Frame(parent, bg=bg, cursor="hand2")
        f.pack(fill="x", pady=2, padx=10)
        l = tk.Label(f, text=text, bg=bg, fg=fg,
                     font=("Helvetica", 10), pady=10, anchor="w", padx=14)
        l.pack(fill="x")
        for w in (f, l):
            w.bind("<Enter>", lambda e: [f.config(bg=hover_bg), l.config(bg=hover_bg)])
            w.bind("<Leave>", lambda e: [f.config(bg=bg), l.config(bg=bg)])
            w.bind("<Button-1>", lambda e: command())

    # ==============================
    # Sidebar
    # ==============================
    sidebar = tk.Frame(root, bg="#0d1117", width=230)
    sidebar.pack(side="left", fill="y")
    sidebar.pack_propagate(False)

    tk.Frame(sidebar, bg="#4f8ef7", height=4).pack(fill="x")

    tk.Label(sidebar, text="User Panel",
             bg="#0d1117", fg="white",
             font=("Helvetica", 14, "bold")).pack(pady=(20, 5))

    tk.Label(sidebar, text="Welcome, {}".format(username),
             bg="#0d1117", fg="#3a3f55",
             font=("Helvetica", 9)).pack(pady=(0, 20))

    tk.Frame(sidebar, bg="#1e2130", height=1).pack(fill="x", padx=15, pady=5)

    tk.Label(sidebar, text="POLICIES", bg="#0d1117", fg="#3a3f55",
             font=("Helvetica", 8, "bold")).pack(anchor="w", padx=20, pady=(10, 4))

    make_sidebar_btn(sidebar, "   My Policies",
                     "#0d1117", "#c9d1d9", "#1e2130", view_my_policies)
    make_sidebar_btn(sidebar, "   Purchase Policy",
                     "#0d1117", "#c9d1d9", "#1e2130", open_purchase_window)

    tk.Frame(sidebar, bg="#1e2130", height=1).pack(fill="x", padx=15, pady=10)

    tk.Label(sidebar, text="CLAIMS", bg="#0d1117", fg="#3a3f55",
             font=("Helvetica", 8, "bold")).pack(anchor="w", padx=20, pady=(0, 4))

    make_sidebar_btn(sidebar, "   My Claims",
                     "#0d1117", "#c9d1d9", "#1e2130", view_my_claims)
    make_sidebar_btn(sidebar, "   Apply Claim",
                     "#0d1117", "#c9d1d9", "#1e2130", open_claim_window)
    make_sidebar_btn(sidebar, "   Delete Pending Claim",
                     "#3d1a1a", "#ff6b6b", "#5c2020", delete_claim)

    tk.Frame(sidebar, bg="#1e2130", height=1).pack(fill="x", padx=15, pady=10)

    tk.Label(sidebar, text="ACCOUNT", bg="#0d1117", fg="#3a3f55",
             font=("Helvetica", 8, "bold")).pack(anchor="w", padx=20, pady=(0, 4))

    make_sidebar_btn(sidebar, "   Change Password",
                     "#0d1117", "#c9d1d9", "#1e2130", open_change_password)

    tk.Frame(sidebar, bg="#0d1117").pack(expand=True, fill="both")
    tk.Frame(sidebar, bg="#1e2130", height=1).pack(fill="x", padx=15, pady=5)

    make_sidebar_btn(sidebar, "   Logout",
                     "#3d1a1a", "#ff6b6b", "#5c2020", logout)

    # ==============================
    # Content Area
    # ==============================
    content = tk.Frame(root, bg="#0f1117")
    content.pack(side="right", expand=True, fill="both")

    # Top bar
    topbar = tk.Frame(content, bg="#0d1117", height=55)
    topbar.pack(fill="x")
    topbar.pack_propagate(False)

    section_label = tk.Label(topbar, text="Welcome, {}".format(username),
                             bg="#0d1117", fg="white",
                             font=("Helvetica", 13, "bold"))
    section_label.pack(side="left", padx=20, pady=15)

    status_label = tk.Label(topbar, text="",
                            bg="#0d1117", fg="#e76f51",
                            font=("Helvetica", 10))
    status_label.pack(side="left", padx=10, pady=15)

    # Stats Panel
    stats_frame = tk.Frame(content, bg="#0f1117")
    stats_frame.pack(fill="x", padx=15, pady=(12, 5))

    def make_stat_card(parent, color):
        card = tk.Frame(parent, bg="#1a1d27",
                        highlightbackground="#2e3250",
                        highlightthickness=1)
        card.pack(side="left", padx=6, pady=4, ipadx=16, ipady=10)
        lbl = tk.Label(card, text="", bg="#1a1d27", fg=color,
                       font=("Helvetica", 11, "bold"))
        lbl.pack()
        return lbl

    total_policies_label = make_stat_card(stats_frame, "#7ec8e3")
    total_claims_label   = make_stat_card(stats_frame, "#b5e48c")
    pending_label        = make_stat_card(stats_frame, "#f4a261")
    total_premium_label  = make_stat_card(stats_frame, "#e9c46a")
    success_label        = make_stat_card(stats_frame, "#90e0ef")

    # Search Bar
    search_frame = tk.Frame(content, bg="#0f1117")
    search_frame.pack(fill="x", pady=8, padx=15)

    tk.Label(search_frame, text="Search:", bg="#0f1117",
             fg="#6b7280", font=("Helvetica", 10)).pack(side="left", padx=(0, 8))

    search_entry = tk.Entry(search_frame, bg="#1a1d27",
                            fg="white", insertbackground="white",
                            relief="flat", font=("Helvetica", 11),
                            highlightthickness=1,
                            highlightbackground="#2e3250",
                            highlightcolor="#4f8ef7",
                            width=30)
    search_entry.pack(side="left", ipady=6)

    search_btn = tk.Frame(search_frame, bg="#4f8ef7", cursor="hand2")
    search_btn.pack(side="left", padx=8)
    search_btn_lbl = tk.Label(search_btn, text="Search",
                              bg="#4f8ef7", fg="white",
                              font=("Helvetica", 10, "bold"),
                              padx=16, pady=6)
    search_btn_lbl.pack()
    for w in (search_btn, search_btn_lbl):
        w.bind("<Enter>", lambda e: [search_btn.config(bg="#3a74d4"), search_btn_lbl.config(bg="#3a74d4")])
        w.bind("<Leave>", lambda e: [search_btn.config(bg="#4f8ef7"), search_btn_lbl.config(bg="#4f8ef7")])
        w.bind("<Button-1>", lambda e: search_data())

    # Table
    tree_frame = tk.Frame(content, bg="#0f1117")
    tree_frame.pack(expand=True, fill="both", padx=15, pady=(5, 15))

    scrollbar_y = ttk.Scrollbar(tree_frame, orient="vertical")
    scrollbar_y.pack(side="right", fill="y")

    scrollbar_x = ttk.Scrollbar(tree_frame, orient="horizontal")
    scrollbar_x.pack(side="bottom", fill="x")

    tree = ttk.Treeview(tree_frame, yscrollcommand=scrollbar_y.set,
                        xscrollcommand=scrollbar_x.set)
    tree.pack(expand=True, fill="both")

    scrollbar_y.config(command=tree.yview)
    scrollbar_x.config(command=tree.xview)

    tree.tag_configure("Approved", foreground="lightgreen")
    tree.tag_configure("Rejected", foreground="#ff6b6b")
    tree.tag_configure("Pending", foreground="orange")

    update_statistics()
    root.mainloop()