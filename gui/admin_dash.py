import tkinter as tk
from tkinter import ttk, messagebox
from database.user_queries import get_all_users
from database.policy_queries import get_all_policies, add_policy
from database.claim_queries import get_all_claims, update_claim_status
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def open_admin_dashboard(admin_id):

    current_view = {"type": None, "data": []}

    def clear_table():
        for row in tree.get_children():
            tree.delete(row)

    def update_stats():
        users = get_all_users()
        policies = get_all_policies()
        claims = get_all_claims()

        total_users_label.config(text="👤  Users: {}".format(len(users)))
        total_policies_label.config(text="📋  Policies: {}".format(len(policies)))
        total_claims_label.config(text="📁  Claims: {}".format(len(claims)))

        pending = sum(1 for c in claims if c[4] == "Pending")
        pending_claims_label.config(text="⏳  Pending: {}".format(pending))
        
    def show_charts():
        claims = get_all_claims()
        users = get_all_users()
        policies = get_all_policies()

        approved = sum(1 for c in claims if c[4] == "Approved")
        rejected = sum(1 for c in claims if c[4] == "Rejected")
        pending  = sum(1 for c in claims if c[4] == "Pending")

        chart_win = tk.Toplevel(root)
        chart_win.title("System Statistics")
        chart_win.geometry("900x500")
        chart_win.configure(bg="#0f1117")

        tk.Frame(chart_win, bg="#4f8ef7", height=4).pack(fill="x")
        tk.Label(chart_win, text="System Statistics",
                 bg="#0f1117", fg="white",
                 font=("Helvetica", 13, "bold")).pack(pady=(15, 5))

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
        fig.patch.set_facecolor("#0f1117")

        # ── Bar Chart ──
        ax1.set_facecolor("#1a1d27")
        categories = ["Users", "Policies", "Claims"]
        values     = [len(users), len(policies), len(claims)]
        colors     = ["#7ec8e3", "#b5e48c", "#f4a261"]
        bars = ax1.bar(categories, values, color=colors, width=0.5)
        ax1.set_title("System Overview", color="white", pad=10)
        ax1.tick_params(colors="white")
        ax1.spines["bottom"].set_color("#2e3250")
        ax1.spines["left"].set_color("#2e3250")
        ax1.spines["top"].set_visible(False)
        ax1.spines["right"].set_visible(False)
        for bar, val in zip(bars, values):
            ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1,
                     str(val), ha="center", va="bottom", color="white", fontsize=10)

        # ── Line Dot Chart ──
        ax2.set_facecolor("#1a1d27")
        claim_labels  = ["Approved", "Rejected", "Pending"]
        claim_values  = [approved, rejected, pending]
        claim_colors  = ["lightgreen", "#ff6b6b", "orange"]
        ax2.plot(claim_labels, claim_values,
                 color="#4f8ef7", linewidth=2, zorder=1)
        for i, (lbl, val, col) in enumerate(zip(claim_labels, claim_values, claim_colors)):
            ax2.scatter(i, val, color=col, s=100, zorder=2)
            ax2.text(i, val + 0.1, str(val),
                     ha="center", va="bottom", color="white", fontsize=10)
        ax2.set_title("Claims Breakdown", color="white", pad=10)
        ax2.tick_params(colors="white")
        ax2.spines["bottom"].set_color("#2e3250")
        ax2.spines["left"].set_color("#2e3250")
        ax2.spines["top"].set_visible(False)
        ax2.spines["right"].set_visible(False)

        plt.tight_layout(pad=2)

        canvas = FigureCanvasTkAgg(fig, master=chart_win)
        canvas.draw()
        canvas.get_tk_widget().pack(expand=True, fill="both", padx=15, pady=10)

    def populate_table(columns, data):
        clear_table()
        tree["columns"] = columns
        tree["show"] = "headings"
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=160)
        for row in data:
            tree.insert("", "end", values=row)

    def show_users():
        users = get_all_users()
        current_view["type"] = "users"
        current_view["data"] = users
        populate_table(("ID", "Username", "Role"), users)
        section_label.config(text="👤  All Users")

    def show_policies():
        policies = get_all_policies()
        current_view["type"] = "policies"
        current_view["data"] = policies
        populate_table(("ID", "Policy Name", "Premium"), policies)
        section_label.config(text="📋  All Policies")

    def show_claims():
        claims = get_all_claims()
        current_view["type"] = "claims"
        current_view["data"] = claims
        populate_table(("Claim ID", "Username", "Policy", "Amount", "Status"), claims)
        section_label.config(text="📁  All Claims")
        tree.tag_configure("Approved", foreground="lightgreen")
        tree.tag_configure("Rejected", foreground="#ff6b6b")
        tree.tag_configure("Pending", foreground="orange")
        for item in tree.get_children():
            status = tree.item(item)["values"][4]
            tree.item(item, tags=(status,))

    def search_data():
        query = search_entry.get().lower()
        if not query:
            return
        filtered = [row for row in current_view["data"]
                    if any(query in str(item).lower() for item in row)]
        if current_view["type"] == "users":
            populate_table(("ID", "Username", "Role"), filtered)
        elif current_view["type"] == "policies":
            populate_table(("ID", "Policy Name", "Premium"), filtered)
        elif current_view["type"] == "claims":
            populate_table(("Claim ID", "Username", "Policy", "Amount", "Status"), filtered)

    def approve_claim():
        if current_view["type"] != "claims":
            messagebox.showerror("Error", "Switch to 'View Claims' first!")
            return
        selected = tree.selection()
        if not selected:
            messagebox.showerror("Error", "Select a claim first!")
            return
        claim_id = tree.item(selected[0])["values"][0]
        update_claim_status(claim_id, "Approved")
        show_claims()
        update_stats()

    def reject_claim():
        if current_view["type"] != "claims":
            messagebox.showerror("Error", "Switch to 'View Claims' first!")
            return
        selected = tree.selection()
        if not selected:
            messagebox.showerror("Error", "Select a claim first!")
            return
        claim_id = tree.item(selected[0])["values"][0]
        update_claim_status(claim_id, "Rejected")
        show_claims()
        update_stats()

    def open_add_policy_window():
        add_win = tk.Toplevel(root)
        add_win.title("Add Policy")
        add_win.geometry("380x280")
        add_win.configure(bg="#0f1117")
        add_win.resizable(False, False)

        # Accent bar
        tk.Frame(add_win, bg="#4f8ef7", height=4).pack(fill="x")

        tk.Label(add_win, text="📋  Add New Policy",
                 bg="#0f1117", fg="white",
                 font=("Helvetica", 13, "bold")).pack(pady=(20, 15))

        form = tk.Frame(add_win, bg="#0f1117")
        form.pack(padx=30, fill="x")

        tk.Label(form, text="POLICY NAME", bg="#0f1117", fg="#6b7280",
                 font=("Helvetica", 9, "bold")).pack(anchor="w")
        name_entry = tk.Entry(form, bg="#1a1d27", fg="white",
                              insertbackground="white", relief="flat",
                              font=("Helvetica", 11),
                              highlightthickness=1,
                              highlightbackground="#2e3250",
                              highlightcolor="#4f8ef7")
        name_entry.pack(fill="x", ipady=7, pady=(4, 14))

        tk.Label(form, text="BASE PREMIUM (₹)", bg="#0f1117", fg="#6b7280",
                 font=("Helvetica", 9, "bold")).pack(anchor="w")
        premium_entry = tk.Entry(form, bg="#1a1d27", fg="white",
                                 insertbackground="white", relief="flat",
                                 font=("Helvetica", 11),
                                 highlightthickness=1,
                                 highlightbackground="#2e3250",
                                 highlightcolor="#4f8ef7")
        premium_entry.pack(fill="x", ipady=7, pady=(4, 20))

        def save_policy():
            name = name_entry.get().strip()
            premium = premium_entry.get().strip()
            if not name or not premium:
                messagebox.showerror("Error", "All fields required!")
                return
            try:
                add_policy(name, float(premium))
                add_win.destroy()
                update_stats()
                show_policies()
            except ValueError:
                messagebox.showerror("Error", "Premium must be a number!")

        save_btn = tk.Frame(form, bg="#4f8ef7", cursor="hand2")
        save_btn.pack(fill="x")
        save_btn_lbl = tk.Label(save_btn, text="Save Policy",
                                bg="#4f8ef7", fg="white",
                                font=("Helvetica", 11, "bold"),
                                pady=10)
        save_btn_lbl.pack(fill="x")
        for w in (save_btn, save_btn_lbl):
            w.bind("<Enter>", lambda e: [save_btn.config(bg="#3a74d4"), save_btn_lbl.config(bg="#3a74d4")])
            w.bind("<Leave>", lambda e: [save_btn.config(bg="#4f8ef7"), save_btn_lbl.config(bg="#4f8ef7")])
            w.bind("<Button-1>", lambda e: save_policy())

    def logout():
        root.destroy()
        from gui.login import start_login
        start_login()

    # ==============================
    # Main Window
    # ==============================
    root = tk.Tk()
    root.title("Admin Dashboard")
    root.geometry("1100x660")
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

    style.configure("Sidebar.TButton",
                    background="#1a1d27",
                    foreground="#c9d1d9",
                    font=("Helvetica", 10),
                    padding=10,
                    borderwidth=0,
                    relief="flat")
    style.map("Sidebar.TButton",
              background=[("active", "#2e3250")],
              foreground=[("active", "white")])

    style.configure("Danger.TButton",
                    background="#3d1a1a",
                    foreground="#ff6b6b",
                    font=("Helvetica", 10),
                    padding=10,
                    borderwidth=0)
    style.map("Danger.TButton",
              background=[("active", "#5c2020")],
              foreground=[("active", "#ff9999")])

    style.configure("Success.TButton",
                    background="#1a3d2e",
                    foreground="#b5e48c",
                    font=("Helvetica", 10),
                    padding=10,
                    borderwidth=0)
    style.map("Success.TButton",
              background=[("active", "#1f5c3d")],
              foreground=[("active", "#d4f5a0")])

    # ==============================
    # Sidebar
    # ==============================
    sidebar = tk.Frame(root, bg="#0d1117", width=230)
    sidebar.pack(side="left", fill="y")
    sidebar.pack_propagate(False)

    # Top accent
    tk.Frame(sidebar, bg="#4f8ef7", height=4).pack(fill="x")

    tk.Label(sidebar, text="🛡  Admin Panel",
             bg="#0d1117", fg="white",
             font=("Helvetica", 14, "bold")).pack(pady=(20, 5))

    tk.Label(sidebar, text="Insurance Management System",
             bg="#0d1117", fg="#3a3f55",
             font=("Helvetica", 8)).pack(pady=(0, 20))

    # Divider
    tk.Frame(sidebar, bg="#1e2130", height=1).pack(fill="x", padx=15, pady=5)

    tk.Label(sidebar, text="MANAGE", bg="#0d1117", fg="#3a3f55",
             font=("Helvetica", 8, "bold")).pack(anchor="w", padx=20, pady=(10, 4))

    ttk.Button(sidebar, text="👤   View Users",
               command=show_users,
               style="Sidebar.TButton").pack(fill="x", pady=2, padx=10)

    ttk.Button(sidebar, text="📋   View Policies",
               command=show_policies,
               style="Sidebar.TButton").pack(fill="x", pady=2, padx=10)

    ttk.Button(sidebar, text="➕   Add Policy",
               command=open_add_policy_window,
               style="Sidebar.TButton").pack(fill="x", pady=2, padx=10)

    ttk.Button(sidebar, text="📁   View Claims",
               command=show_claims,
               style="Sidebar.TButton").pack(fill="x", pady=2, padx=10)

    ttk.Button(sidebar, text="📊   View Statistics",
               command=show_charts,
               style="Sidebar.TButton").pack(fill="x", pady=2, padx=10)

    tk.Frame(sidebar, bg="#1e2130", height=1).pack(fill="x", padx=15, pady=10)

    tk.Label(sidebar, text="ACTIONS", bg="#0d1117", fg="#3a3f55",
             font=("Helvetica", 8, "bold")).pack(anchor="w", padx=20, pady=(0, 4))

    ttk.Button(sidebar, text="✅   Approve Claim",
               command=approve_claim,
               style="Success.TButton").pack(fill="x", pady=2, padx=10)

    ttk.Button(sidebar, text="❌   Reject Claim",
               command=reject_claim,
               style="Danger.TButton").pack(fill="x", pady=2, padx=10)

    tk.Frame(sidebar, bg="#0d1117").pack(expand=True, fill="both")

    tk.Frame(sidebar, bg="#1e2130", height=1).pack(fill="x", padx=15, pady=5)

    ttk.Button(sidebar, text="⏻   Logout",
               command=logout,
               style="Danger.TButton").pack(fill="x", pady=15, padx=10)

    # ==============================
    # Content Area
    # ==============================
    content = tk.Frame(root, bg="#0f1117")
    content.pack(side="right", expand=True, fill="both")

    # Top bar
    topbar = tk.Frame(content, bg="#0d1117", height=55)
    topbar.pack(fill="x")
    topbar.pack_propagate(False)

    section_label = tk.Label(topbar, text="Welcome, Admin",
                             bg="#0d1117", fg="white",
                             font=("Helvetica", 13, "bold"))
    section_label.pack(side="left", padx=20, pady=15)

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

    total_users_label    = make_stat_card(stats_frame, "#7ec8e3")
    total_policies_label = make_stat_card(stats_frame, "#b5e48c")
    total_claims_label   = make_stat_card(stats_frame, "#f4a261")
    pending_claims_label = make_stat_card(stats_frame, "#e76f51")

    # Search Bar
    search_frame = tk.Frame(content, bg="#0f1117")
    search_frame.pack(fill="x", pady=8, padx=15)

    tk.Label(search_frame, text="🔍", bg="#0f1117",
             fg="#6b7280", font=("Helvetica", 12)).pack(side="left", padx=(0, 4))

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
                              padx=14, pady=6)
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

    tree = ttk.Treeview(tree_frame,
                        yscrollcommand=scrollbar_y.set,
                        xscrollcommand=scrollbar_x.set)
    tree.pack(expand=True, fill="both")

    scrollbar_y.config(command=tree.yview)
    scrollbar_x.config(command=tree.xview)

    update_stats()
    root.mainloop()