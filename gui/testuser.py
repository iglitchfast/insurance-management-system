import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from database.policy_queries import get_all_policies, purchase_policy, get_user_policies
from database.claim_queries import add_claim, get_user_claims
from utils.hash_utils import hash_password
from database.connection import get_connection


def open_user_dashboard(user_id, username):

    current_view = {"type": None, "data": []}

    # =============================
    # Helper Functions
    # =============================

    def clear_table():
        for row in tree.get_children():
            tree.delete(row)

    def populate_table(columns, data, claim_view=False):
        clear_table()
        tree["columns"] = columns
        tree["show"] = "headings"

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=150)

        for row in data:
            if claim_view:
                tree.insert("", "end", values=row, tags=(row[3],))
            else:
                tree.insert("", "end", values=row)

    # =============================
    # Statistics
    # =============================

    def update_statistics():
        policies = get_user_policies(user_id)
        claims = get_user_claims(user_id)

        total_policies_label.config(text=f"My Policies: {len(policies)}")
        total_claims_label.config(text=f"My Claims: {len(claims)}")

        pending = sum(1 for c in claims if c[3] == "Pending")
        approved = sum(1 for c in claims if c[3] == "Approved")

        pending_label.config(text=f"Pending: {pending}")

        invested = sum(float(p[2]) for p in policies)
        total_premium_label.config(text=f"Total Premium Invested: ₹{invested:.2f}")

        success_rate = (approved / len(claims) * 100) if claims else 0
        success_label.config(text=f"Claim Success Rate: {success_rate:.1f}%")

    # =============================
    # Views
    # =============================

    def view_my_policies():
        policies = get_user_policies(user_id)
        current_view["type"] = "policies"
        current_view["data"] = policies
        populate_table(("Purchase ID", "Policy Name", "Premium", "Start Date"), policies)
        update_statistics()

    def view_my_claims():
        claims = get_user_claims(user_id)
        current_view["type"] = "claims"
        current_view["data"] = claims
        populate_table(("Claim ID", "Policy Name", "Amount", "Status"), claims, claim_view=True)
        update_statistics()

    # =============================
    # Search
    # =============================

    def search_data():
        query = search_entry.get().lower()
        if not query:
            populate_table(tree["columns"], current_view["data"],
                           claim_view=(current_view["type"] == "claims"))
            return

        filtered = [
            row for row in current_view["data"]
            if any(query in str(item).lower() for item in row)
        ]

        populate_table(tree["columns"], filtered,
                       claim_view=(current_view["type"] == "claims"))

    # =============================
    # Purchase Policy
    # =============================

    def open_purchase_window():
        win = tk.Toplevel(root)
        win.title("Purchase Policy")
        win.geometry("400x320")
        win.configure(bg="#2b2b2b")

        tk.Label(win, text="Select Policy",
                 bg="#2b2b2b", fg="white").pack(pady=10)

        policies = get_all_policies()
        policy_dict = {f"{p[1]} - ₹{p[2]}": p[0] for p in policies}

        policy_var = tk.StringVar()
        ttk.OptionMenu(win, policy_var, *policy_dict.keys()).pack(pady=10)

        tk.Label(win, text="Start Date (DD-MM-YYYY)",
                 bg="#2b2b2b", fg="white").pack(pady=10)

        date_entry = tk.Entry(win, bg="#3c3f41",
                              fg="white", insertbackground="white")
        date_entry.pack(pady=5, ipady=4)

        def purchase():
            selected = policy_var.get()
            date_str = date_entry.get()

            if not selected or not date_str:
                messagebox.showerror("Error", "All fields required!")
                return

            try:
                date_obj = datetime.strptime(date_str, "%d-%m-%Y")
                date_db = date_obj.strftime("%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Error", "Date must be DD-MM-YYYY")
                return

            policy_id = policy_dict[selected]

            # Prevent duplicate
            existing = get_user_policies(user_id)
            for p in existing:
                if p[1] == selected.split(" - ")[0]:
                    messagebox.showerror("Error", "Policy already purchased!")
                    return

            purchase_policy(user_id, policy_id, date_db)
            messagebox.showinfo("Success", "Policy Purchased!")
            win.destroy()
            view_my_policies()

        ttk.Button(win, text="Purchase", command=purchase).pack(pady=20)

    # =============================
    # Apply Claim
    # =============================

    def open_claim_window():
        win = tk.Toplevel(root)
        win.title("Apply Claim")
        win.geometry("400x320")
        win.configure(bg="#2b2b2b")

        tk.Label(win, text="Select Purchased Policy",
                 bg="#2b2b2b", fg="white").pack(pady=10)

        policies = get_user_policies(user_id)
        policy_dict = {f"{p[1]} (ID:{p[0]})": p[0] for p in policies}

        policy_var = tk.StringVar()
        ttk.OptionMenu(win, policy_var, *policy_dict.keys()).pack(pady=10)

        tk.Label(win, text="Claim Amount",
                 bg="#2b2b2b", fg="white").pack(pady=10)

        amount_entry = tk.Entry(win, bg="#3c3f41",
                                fg="white", insertbackground="white")
        amount_entry.pack(pady=5, ipady=4)

        def submit_claim():
            selected = policy_var.get()
            amount = amount_entry.get()

            if not selected or not amount:
                messagebox.showerror("Error", "All fields required!")
                return

            try:
                amount = float(amount)
                purchase_id = policy_dict[selected]
                add_claim(purchase_id, amount)
                messagebox.showinfo("Success", "Claim Submitted!")
                win.destroy()
                view_my_claims()
            except ValueError:
                messagebox.showerror("Error", "Amount must be numeric!")

        ttk.Button(win, text="Submit Claim", command=submit_claim).pack(pady=20)

    # =============================
    # Delete Pending Claim
    # =============================

    def delete_claim():
        # Ensure user is in claims view
        if current_view["type"] != "claims":
            messagebox.showerror("Error", "Switch to 'My Claims' view first!")
            return

        selected = tree.selection()

        if not selected:
            messagebox.showerror("Error", "Select a claim first!")
            return

        item_id = selected[0]
        values = tree.item(item_id)["values"]

        if not values or len(values) < 4:
            messagebox.showerror("Error", "Invalid selection!")
            return

        claim_id = values[0]
        status = values[3]

        if status != "Pending":
            messagebox.showerror("Error", "Only Pending claims can be deleted!")
            return

        confirm = messagebox.askyesno("Confirm", "Delete this claim?")
        if not confirm:
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM CLAIMS WHERE claim_id=%s", (claim_id,))
            conn.commit()
            cursor.close()
            conn.close()

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
        win.geometry("350x250")
        win.configure(bg="#2b2b2b")

        tk.Label(win, text="New Password",
                 bg="#2b2b2b", fg="white").pack(pady=15)

        new_entry = tk.Entry(win, show="*", bg="#3c3f41",
                             fg="white", insertbackground="white")
        new_entry.pack(pady=5, ipady=4)

        def change():
            new_pass = new_entry.get()
            if not new_pass:
                return

            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE USERS SET password=%s WHERE user_id=%s",
                (hash_password(new_pass), user_id)
            )
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Password Updated!")
            win.destroy()

        ttk.Button(win, text="Update", command=change).pack(pady=20)

    def logout():
        root.destroy()
        from gui.login import start_login
        start_login()

    # =============================
    # Main Window
    # =============================

    root = tk.Tk()
    root.title("User Dashboard")
    root.geometry("1150x700")
    root.configure(bg="#1e1e1e")

    style = ttk.Style()
    style.theme_use("clam")

    style.configure("Treeview",
                    background="#2b2b2b",
                    foreground="white",
                    fieldbackground="#2b2b2b")

    style.map("Treeview",
              background=[("selected", "#007acc")])

    # Layout
    sidebar = tk.Frame(root, bg="#2b2b2b", width=220)
    sidebar.pack(side="left", fill="y")

    tk.Label(sidebar, text="User Panel",
             bg="#2b2b2b", fg="white",
             font=("Helvetica", 15, "bold")).pack(pady=20)

    ttk.Button(sidebar, text="My Policies",
               command=view_my_policies).pack(fill="x", pady=6, padx=15)

    ttk.Button(sidebar, text="Purchase Policy",
               command=open_purchase_window).pack(fill="x", pady=6, padx=15)

    ttk.Button(sidebar, text="My Claims",
               command=view_my_claims).pack(fill="x", pady=6, padx=15)

    ttk.Button(sidebar, text="Delete Pending Claim",
               command=delete_claim).pack(fill="x", pady=6, padx=15)

    ttk.Button(sidebar, text="Apply Claim",
               command=open_claim_window).pack(fill="x", pady=6, padx=15)

    ttk.Button(sidebar, text="Change Password",
               command=open_change_password).pack(fill="x", pady=6, padx=15)

    tk.Frame(sidebar, bg="#2b2b2b").pack(expand=True, fill="both")

    ttk.Button(sidebar, text="Logout",
               command=logout).pack(fill="x", pady=20, padx=15)

    # Content
    content = tk.Frame(root, bg="#1e1e1e")
    content.pack(side="right", expand=True, fill="both")

    tk.Label(content, text=f"Welcome, {username}",
             bg="#1e1e1e", fg="white",
             font=("Helvetica", 16, "bold")).pack(pady=10)

    stats_frame = tk.Frame(content, bg="#1e1e1e")
    stats_frame.pack(fill="x", pady=10)

    total_policies_label = tk.Label(stats_frame, fg="white", bg="#1e1e1e")
    total_policies_label.pack(side="left", padx=20)

    total_claims_label = tk.Label(stats_frame, fg="white", bg="#1e1e1e")
    total_claims_label.pack(side="left", padx=20)

    pending_label = tk.Label(stats_frame, fg="white", bg="#1e1e1e")
    pending_label.pack(side="left", padx=20)

    total_premium_label = tk.Label(stats_frame, fg="white", bg="#1e1e1e")
    total_premium_label.pack(side="left", padx=20)

    success_label = tk.Label(stats_frame, fg="white", bg="#1e1e1e")
    success_label.pack(side="left", padx=20)

    # Search
    search_frame = tk.Frame(content, bg="#1e1e1e")
    search_frame.pack(fill="x", pady=10)

    tk.Label(search_frame, text="Search:",
             fg="white", bg="#1e1e1e").pack(side="left", padx=10)

    search_entry = tk.Entry(search_frame,
                            bg="#3c3f41",
                            fg="white",
                            insertbackground="white")
    search_entry.pack(side="left", padx=10)

    ttk.Button(search_frame, text="Search",
               command=search_data).pack(side="left", padx=10)

    # Table
    tree = ttk.Treeview(content)
    tree.tag_configure("Approved", foreground="lightgreen")
    tree.tag_configure("Rejected", foreground="red")
    tree.tag_configure("Pending", foreground="orange")

    tree.pack(expand=True, fill="both", padx=25, pady=20)

    update_statistics()
    root.mainloop()
