import tkinter as tk
from tkinter import messagebox, ttk
from database.user_queries import verify_user


def start_login():

    def login(event=None):
        username = username_entry.get().strip()
        password = password_entry.get()
        role = role_var.get()

        if not username or not password:
            messagebox.showerror("Error", "All fields are required!")
            return

        user = verify_user(username, password, role)

        if user:
            user_id, username_db, role_db = user
            root.destroy()

            if role_db == "admin":
                from gui.admin_dash import open_admin_dashboard
                open_admin_dashboard(user_id)
            elif role_db == "user":
                from gui.user_dash import open_user_dashboard
                open_user_dashboard(user_id, username_db)
            elif role_db == "agent":
                from gui.agent_dash import open_agent_dashboard
                open_agent_dashboard(user_id)
        else:
            messagebox.showerror("Error", "Invalid credentials or role!")

    # ==============================
    # Main Window
    # ==============================
    root = tk.Tk()
    root.title("Insurance Management System")
    root.geometry("520x620")
    root.configure(bg="#0f1117")
    root.resizable(False, False)

    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (520 // 2)
    y = (root.winfo_screenheight() // 2) - (620 // 2)
    root.geometry("520x620+{}+{}".format(x, y))

    # ==============================
    # Styles
    # ==============================
    style = ttk.Style()
    style.theme_use("clam")

    style.configure("Login.TButton",
                    background="#4f8ef7",
                    foreground="white",
                    font=("Helvetica", 11, "bold"),
                    padding=10,
                    borderwidth=0,
                    relief="flat")
    style.map("Login.TButton",
              background=[("active", "#3a74d4")],
              foreground=[("active", "white")])

    style.configure("Role.TCombobox",
                    fieldbackground="#1e2130",
                    background="#1e2130",
                    foreground="white",
                    selectbackground="#1e2130",
                    selectforeground="white",
                    borderwidth=0)

    # ==============================
    # Background top accent bar
    # ==============================
    top_bar = tk.Frame(root, bg="#4f8ef7", height=6)
    top_bar.pack(fill="x", side="top")

    # ==============================
    # Outer wrapper (centers the card)
    # ==============================
    wrapper = tk.Frame(root, bg="#0f1117")
    wrapper.pack(expand=True, fill="both")

    # ==============================
    # Card
    # ==============================
    card = tk.Frame(wrapper, bg="#1a1d27",
                    padx=45, pady=40,
                    highlightbackground="#2e3250",
                    highlightthickness=1)
    card.place(relx=0.5, rely=0.5, anchor="center")

    # Shield icon (unicode, no image needed)
    tk.Label(card,
             text="🛡",
             font=("Helvetica", 38),
             bg="#1a1d27",
             fg="#4f8ef7").pack(pady=(0, 8))

    tk.Label(card,
             text="Insurance Management",
             font=("Helvetica", 17, "bold"),
             bg="#1a1d27",
             fg="white").pack()

    tk.Label(card,
             text="Sign in to your account",
             font=("Helvetica", 10),
             bg="#1a1d27",
             fg="#6b7280").pack(pady=(4, 28))

    # ── Username ──
    tk.Label(card,
         text="USERNAME",
         font=("Helvetica", 9, "bold"),
         bg="#1a1d27",
         fg="#6b7280").pack(anchor="w")

    username_entry = tk.Entry(card,
                              bg="#0f1117",
                              fg="white",
                              insertbackground="white",
                              relief="flat",
                              font=("Helvetica", 11),
                              highlightthickness=1,
                              highlightbackground="#2e3250",
                              highlightcolor="#4f8ef7")
    username_entry.pack(fill="x", pady=(6, 18), ipady=8)

    # ── Password ──
    tk.Label(card,
             text="PASSWORD",
             font=("Helvetica", 9, "bold"),
             bg="#1a1d27",
             fg="#6b7280").pack(anchor="w")

    password_entry = tk.Entry(card,
                              show="●",
                              bg="#0f1117",
                              fg="white",
                              insertbackground="white",
                              relief="flat",
                              font=("Helvetica", 11),
                              highlightthickness=1,
                              highlightbackground="#2e3250",
                              highlightcolor="#4f8ef7")
    password_entry.pack(fill="x", pady=(6, 18), ipady=8)

    # ── Role ──
    tk.Label(card,
             text="ROLE",
             font=("Helvetica", 9, "bold"),
             bg="#1a1d27",
             fg="#6b7280").pack(anchor="w")

    role_var = tk.StringVar(value="user")

    # Style the dropdown to match the dark theme
    style.configure("Role.TCombobox",
                    fieldbackground="#0f1117",
                    background="#0f1117",
                    foreground="white",
                    selectbackground="#0f1117",
                    selectforeground="white",
                    borderwidth=0,
                    arrowcolor="#4f8ef7")
    style.map("Role.TCombobox",
            fieldbackground=[("readonly", "#0f1117")],
            selectbackground=[("readonly", "#0f1117")],
            foreground=[("readonly", "white")])

    role_combo = ttk.Combobox(card,
                            textvariable=role_var,
                            values=["user", "admin", "agent"],
                            state="readonly",
                            font=("Helvetica", 11),
                            style="Role.TCombobox")
    role_combo.pack(fill="x", pady=(6, 24), ipady=6)

    # Force dark dropdown list colors
    root.option_add("*TCombobox*Listbox.background", "#1a1d27")
    root.option_add("*TCombobox*Listbox.foreground", "white")
    root.option_add("*TCombobox*Listbox.selectBackground", "#4f8ef7")
    root.option_add("*TCombobox*Listbox.selectForeground", "white")
    root.option_add("*TCombobox*Listbox.font", "Helvetica 11")

    # ── Login Button ──
    ttk.Button(card,
               text="LOGIN  →",
               command=login,
               style="Login.TButton").pack(fill="x", pady=(4, 0))

    # ── Footer ──
    tk.Label(wrapper,
             text="© 2025 Insurance Management System",
             font=("Helvetica", 9),
             bg="#0f1117",
             fg="#3a3f55").pack(side="bottom", pady=15)

    root.bind("<Return>", login)
    username_entry.focus_set()

    root.mainloop()