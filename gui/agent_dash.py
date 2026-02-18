import tkinter as tk
from tkinter import ttk, messagebox
from database.user_queries import add_user, get_all_users
from database.policy_queries import get_all_policies, purchase_policy


def open_agent_dashboard(agent_id):

    current_view = {"type": None}

    def clear_table():
        for row in tree.get_children():
            tree.delete(row)

    def view_customers():
        clear_table()
        tree["columns"] = ("User ID", "Username", "Role")
        tree["show"] = "headings"
        for col in tree["columns"]:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=160)
        users = get_all_users()
        for user in users:
            if user[2] == "user":
                tree.insert("", "end", values=user)
        section_label.config(text="Customers")
        status_label.config(text="")

    def view_policies():
        clear_table()
        tree["columns"] = ("Policy ID", "Policy Name", "Premium")
        tree["show"] = "headings"
        for col in tree["columns"]:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=180)
        policies = get_all_policies()
        for policy in policies:
            tree.insert("", "end", values=policy)
        section_label.config(text="All Policies")
        status_label.config(text="")

    # =============================
    # Register Customer Window
    # =============================

    def open_add_customer():
        win = tk.Toplevel(root)
        win.title("Register Customer")
        win.geometry("380x320")
        win.configure(bg="#0f1117")
        win.resizable(False, False)

        tk.Frame(win, bg="#4f8ef7", height=4).pack(fill="x")
        tk.Label(win, text="Register Customer",
                 bg="#0f1117", fg="white",
                 font=("Helvetica", 13, "bold")).pack(pady=(20, 15))

        form = tk.Frame(win, bg="#0f1117")
        form.pack(padx=30, fill="x")

        tk.Label(form, text="USERNAME", bg="#0f1117", fg="#6b7280",
                 font=("Helvetica", 9, "bold")).pack(anchor="w")
        username_entry = tk.Entry(form, bg="#1a1d27", fg="white",
                                  insertbackground="white", relief="flat",
                                  font=("Helvetica", 11),
                                  highlightthickness=1,
                                  highlightbackground="#2e3250",
                                  highlightcolor="#4f8ef7")
        username_entry.pack(fill="x", ipady=7, pady=(4, 14))

        tk.Label(form, text="PASSWORD", bg="#0f1117", fg="#6b7280",
                 font=("Helvetica", 9, "bold")).pack(anchor="w")
        password_entry = tk.Entry(form, show="*", bg="#1a1d27", fg="white",
                                  insertbackground="white", relief="flat",
                                  font=("Helvetica", 11),
                                  highlightthickness=1,
                                  highlightbackground="#2e3250",
                                  highlightcolor="#4f8ef7")
        password_entry.pack(fill="x", ipady=7, pady=(4, 20))

        def register():
            username = username_entry.get().strip()
            password = password_entry.get()
            if not username or not password:
                return
            add_user(username, password, "user")
            messagebox.showinfo("Success", "Customer Registered!")
            win.destroy()
            view_customers()

        btn = tk.Frame(form, bg="#4f8ef7", cursor="hand2")
        btn.pack(fill="x")
        btn_lbl = tk.Label(btn, text="Register", bg="#4f8ef7", fg="white",
                           font=("Helvetica", 11, "bold"), pady=10)
        btn_lbl.pack(fill="x")
        for w in (btn, btn_lbl):
            w.bind("<Enter>", lambda e: [btn.config(bg="#3a74d4"), btn_lbl.config(bg="#3a74d4")])
            w.bind("<Leave>", lambda e: [btn.config(bg="#4f8ef7"), btn_lbl.config(bg="#4f8ef7")])
            w.bind("<Button-1>", lambda e: register())

    # =============================
    # Sell Policy Window
    # =============================

    def open_sell_policy():
        users = get_all_users()
        customers = [u for u in users if u[2] == "user"]
        if not customers:
            status_label.config(text="⚠  No customers found! Register a customer first.")
            return

        policies = get_all_policies()
        if not policies:
            status_label.config(text="⚠  No policies found! Add a policy first.")
            return

        win = tk.Toplevel(root)
        win.title("Sell Policy")
        win.geometry("400x400")
        win.configure(bg="#0f1117")
        win.resizable(False, False)

        tk.Frame(win, bg="#4f8ef7", height=4).pack(fill="x")
        tk.Label(win, text="Sell Policy",
                 bg="#0f1117", fg="white",
                 font=("Helvetica", 13, "bold")).pack(pady=(20, 15))

        form = tk.Frame(win, bg="#0f1117")
        form.pack(padx=30, fill="x")

        tk.Label(form, text="SELECT CUSTOMER", bg="#0f1117", fg="#6b7280",
                 font=("Helvetica", 9, "bold")).pack(anchor="w")

        customer_dict = {"{} (ID:{})".format(u[1], u[0]): u[0] for u in customers}
        customer_options = list(customer_dict.keys())
        customer_combo = ttk.Combobox(form, values=customer_options, state="readonly",
                                      font=("Helvetica", 10))
        customer_combo.set(customer_options[0])
        customer_combo.pack(fill="x", pady=(4, 14), ipady=5)

        tk.Label(form, text="SELECT POLICY", bg="#0f1117", fg="#6b7280",
                 font=("Helvetica", 9, "bold")).pack(anchor="w")

        policy_dict = {"{} - Rs.{}".format(p[1], p[2]): p[0] for p in policies}
        policy_options = list(policy_dict.keys())
        policy_combo = ttk.Combobox(form, values=policy_options, state="readonly",
                                    font=("Helvetica", 10))
        policy_combo.set(policy_options[0])
        policy_combo.pack(fill="x", pady=(4, 14), ipady=5)

        tk.Label(form, text="START DATE (YYYY-MM-DD)", bg="#0f1117", fg="#6b7280",
                 font=("Helvetica", 9, "bold")).pack(anchor="w")
        date_entry = tk.Entry(form, bg="#1a1d27", fg="white",
                              insertbackground="white", relief="flat",
                              font=("Helvetica", 11),
                              highlightthickness=1,
                              highlightbackground="#2e3250",
                              highlightcolor="#4f8ef7")
        date_entry.pack(fill="x", ipady=7, pady=(4, 20))

        def sell():
            selected_customer = customer_combo.get()
            selected_policy = policy_combo.get()
            date = date_entry.get().strip()
            if not selected_customer or not selected_policy or not date:
                messagebox.showwarning("Warning", "All fields required!")
                return
            user_id = customer_dict[selected_customer]
            policy_id = policy_dict[selected_policy]
            purchase_policy(user_id, policy_id, date)
            messagebox.showinfo("Success", "Policy Sold Successfully!")
            win.destroy()

        btn = tk.Frame(form, bg="#4f8ef7", cursor="hand2")
        btn.pack(fill="x")
        btn_lbl = tk.Label(btn, text="Sell Policy", bg="#4f8ef7", fg="white",
                           font=("Helvetica", 11, "bold"), pady=10)
        btn_lbl.pack(fill="x")
        for w in (btn, btn_lbl):
            w.bind("<Enter>", lambda e: [btn.config(bg="#3a74d4"), btn_lbl.config(bg="#3a74d4")])
            w.bind("<Leave>", lambda e: [btn.config(bg="#4f8ef7"), btn_lbl.config(bg="#4f8ef7")])
            w.bind("<Button-1>", lambda e: sell())

    def logout():
        root.destroy()
        from gui.login import start_login
        start_login()

    # ==============================
    # Main Window
    # ==============================
    root = tk.Tk()
    root.title("Agent Dashboard")
    root.geometry("1050x620")
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

    tk.Label(sidebar, text="Agent Panel",
             bg="#0d1117", fg="white",
             font=("Helvetica", 14, "bold")).pack(pady=(20, 5))

    tk.Label(sidebar, text="Insurance Management System",
             bg="#0d1117", fg="#3a3f55",
             font=("Helvetica", 8)).pack(pady=(0, 20))

    tk.Frame(sidebar, bg="#1e2130", height=1).pack(fill="x", padx=15, pady=5)

    tk.Label(sidebar, text="CUSTOMERS", bg="#0d1117", fg="#3a3f55",
             font=("Helvetica", 8, "bold")).pack(anchor="w", padx=20, pady=(10, 4))

    make_sidebar_btn(sidebar, "   View Customers",
                     "#0d1117", "#c9d1d9", "#1e2130", view_customers)
    make_sidebar_btn(sidebar, "   Register Customer",
                     "#0d1117", "#c9d1d9", "#1e2130", open_add_customer)

    tk.Frame(sidebar, bg="#1e2130", height=1).pack(fill="x", padx=15, pady=10)

    tk.Label(sidebar, text="POLICIES", bg="#0d1117", fg="#3a3f55",
             font=("Helvetica", 8, "bold")).pack(anchor="w", padx=20, pady=(0, 4))

    make_sidebar_btn(sidebar, "   View Policies",
                     "#0d1117", "#c9d1d9", "#1e2130", view_policies)
    make_sidebar_btn(sidebar, "   Sell Policy",
                     "#1a3d2e", "#b5e48c", "#1f5c3d", open_sell_policy)

    tk.Frame(sidebar, bg="#0d1117").pack(expand=True, fill="both")
    tk.Frame(sidebar, bg="#1e2130", height=1).pack(fill="x", padx=15, pady=5)

    make_sidebar_btn(sidebar, "   Logout",
                     "#3d1a1a", "#ff6b6b", "#5c2020", logout)

    # ==============================
    # Content Area
    # ==============================
    content = tk.Frame(root, bg="#0f1117")
    content.pack(side="right", expand=True, fill="both")

    topbar = tk.Frame(content, bg="#0d1117", height=55)
    topbar.pack(fill="x")
    topbar.pack_propagate(False)

    section_label = tk.Label(topbar, text="Welcome, Agent",
                             bg="#0d1117", fg="white",
                             font=("Helvetica", 13, "bold"))
    section_label.pack(side="left", padx=20, pady=15)

    status_label = tk.Label(topbar, text="",
                            bg="#0d1117", fg="#e76f51",
                            font=("Helvetica", 10))
    status_label.pack(side="left", padx=10, pady=15)

    # Table
    tree_frame = tk.Frame(content, bg="#0f1117")
    tree_frame.pack(expand=True, fill="both", padx=15, pady=15)

    scrollbar_y = ttk.Scrollbar(tree_frame, orient="vertical")
    scrollbar_y.pack(side="right", fill="y")

    scrollbar_x = ttk.Scrollbar(tree_frame, orient="horizontal")
    scrollbar_x.pack(side="bottom", fill="x")

    tree = ttk.Treeview(tree_frame, yscrollcommand=scrollbar_y.set,
                        xscrollcommand=scrollbar_x.set)
    tree.pack(expand=True, fill="both")

    scrollbar_y.config(command=tree.yview)
    scrollbar_x.config(command=tree.xview)

    root.mainloop()