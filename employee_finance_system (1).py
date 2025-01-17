import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import pandas as pd

class CustomStyle:
    # Color scheme
    PRIMARY_COLOR = "#2196F3"
    SECONDARY_COLOR = "#1976D2"
    BACKGROUND_COLOR = "#F5F5F5"
    TEXT_COLOR = "#333333"
    HOVER_COLOR = "#1565C0"
    SUCCESS_COLOR = "#4CAF50"
    ERROR_COLOR = "#F44336"
    
    @staticmethod
    def apply_button_style(button):
        button.configure(
            bg=CustomStyle.PRIMARY_COLOR,
            fg="white",
            font=('Arial', 10, 'bold'),
            relief=tk.FLAT,
            padx=20,
            pady=5
        )
        
        def on_enter(e):
            button['background'] = CustomStyle.HOVER_COLOR
            
        def on_leave(e):
            button['background'] = CustomStyle.PRIMARY_COLOR
            
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)

class EmployeeFinanceSystem:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Employee Financial Management System")
        self.root.geometry("1000x700")
        self.root.configure(bg=CustomStyle.BACKGROUND_COLOR)
        
        # Configure style for ttk widgets
        self.style = ttk.Style()
        self.style.configure("Custom.TEntry", padding=5)
        self.style.configure(
            "Custom.TCombobox",
            padding=5,
            selectbackground=CustomStyle.PRIMARY_COLOR
        )
        
        # Initialize database
        self.init_database()
        
        # Start with login frame
        self.current_frame = None
        self.show_login()

    def init_database(self):
        conn = sqlite3.connect('employee_finance.db')
        c = conn.cursor()
        
        # Create users table
        c.execute('''CREATE TABLE IF NOT EXISTS users
                    (id INTEGER PRIMARY KEY,
                     username TEXT UNIQUE NOT NULL,
                     password TEXT NOT NULL,
                     role TEXT NOT NULL)''')
        
        # Create employees table
        c.execute('''CREATE TABLE IF NOT EXISTS employees
                    (id INTEGER PRIMARY KEY,
                     name TEXT UNIQUE NOT NULL,
                     position TEXT NOT NULL,
                     base_salary REAL NOT NULL,
                     join_date DATE NOT NULL)''')
        
        # Create financial_records table
        c.execute('''CREATE TABLE IF NOT EXISTS financial_records
                    (id INTEGER PRIMARY KEY,
                     employee_id INTEGER,
                     month TEXT NOT NULL,
                     year INTEGER NOT NULL,
                     base_salary REAL NOT NULL,
                     overtime_hours REAL DEFAULT 0,
                     overtime_pay REAL DEFAULT 0,
                     incentives REAL DEFAULT 0,
                     advances REAL DEFAULT 0,
                     loans REAL DEFAULT 0,
                     net_salary REAL NOT NULL,
                     FOREIGN KEY (employee_id) REFERENCES employees (id))''')
        
        conn.commit()
        conn.close()

    def create_custom_entry(self, parent, placeholder=""):
        entry_frame = tk.Frame(parent, bg=CustomStyle.BACKGROUND_COLOR)
        entry_frame.pack(pady=5)
        
        entry = tk.Entry(
            entry_frame,
            font=('Arial', 10),
            bg="white",
            relief=tk.FLAT,
            width=30
        )
        entry.insert(0, placeholder)
        entry.pack(pady=2, ipady=5)
        
        # Add underline
        underline = tk.Frame(entry_frame, height=2, bg=CustomStyle.PRIMARY_COLOR)
        underline.pack(fill=tk.X, pady=(0, 5))
        
        def on_enter(e):
            underline.configure(bg=CustomStyle.HOVER_COLOR)
            
        def on_leave(e):
            underline.configure(bg=CustomStyle.PRIMARY_COLOR)
            
        entry.bind("<Enter>", on_enter)
        entry.bind("<Leave>", on_leave)
        
        return entry

    def show_manage_finances(self):
        self.clear_frame()
        
        # Create main container
        container = tk.Frame(self.current_frame, bg=CustomStyle.BACKGROUND_COLOR)
        container.pack(expand=True, fill=tk.BOTH, padx=50, pady=20)
        
        tk.Label(
            container,
            text="Manage Financial Records",
            font=('Arial', 20, 'bold'),
            bg=CustomStyle.BACKGROUND_COLOR,
            fg=CustomStyle.TEXT_COLOR
        ).pack(pady=20)
        
        # Create employee selection dropdown
        try:
            conn = sqlite3.connect('employee_finance.db')
            c = conn.cursor()
            c.execute("SELECT id, name FROM employees")
            employees = c.fetchall()
            conn.close()
            
            if not employees:
                messagebox.showerror("Error", "No employees found. Please add employees first.")
                self.show_admin_dashboard()
                return
            
            # Employee selection
            tk.Label(
                container,
                text="Select Employee:",
                font=('Arial', 12),
                bg=CustomStyle.BACKGROUND_COLOR,
                fg=CustomStyle.TEXT_COLOR
            ).pack(pady=5)
            
            employee_var = tk.StringVar()
            employee_dict = {emp[1]: emp[0] for emp in employees}
            
            employee_dropdown = ttk.Combobox(
                container,
                textvariable=employee_var,
                values=list(employee_dict.keys()),
                state="readonly",
                width=28,
                style="Custom.TCombobox"
            )
            employee_dropdown.pack(pady=5)
            
            # Month and Year entries
            month_entry = self.create_custom_entry(container, "Month (MM)")
            year_entry = self.create_custom_entry(container, "Year (YYYY)")
            
            # Financial entries
            fields = {'Overtime Hours': '', 'Incentives': '', 'Advances': '', 'Loans': ''}
            entries = {}
            
            for field, value in fields.items():
                entries[field] = self.create_custom_entry(container, field)
            
            # Buttons
            button_frame = tk.Frame(container, bg=CustomStyle.BACKGROUND_COLOR)
            button_frame.pack(pady=20)
            
            save_button = tk.Button(
                button_frame,
                text="Save Record",
                command=lambda: self.save_financial_record(
                    employee_dict.get(employee_var.get()),
                    month_entry.get(),
                    year_entry.get(),
                    entries
                )
            )
            CustomStyle.apply_button_style(save_button)
            save_button.pack(side=tk.LEFT, padx=10)
            
            back_button = tk.Button(
                button_frame,
                text="Back",
                command=self.show_admin_dashboard
            )
            CustomStyle.apply_button_style(back_button)
            back_button.pack(side=tk.LEFT, padx=10)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load employees: {str(e)}")
            self.show_admin_dashboard()

    def save_financial_record(self, employee_id, month, year, entries):
        # Input validation
        if not employee_id:
            messagebox.showerror("Error", "Please select an employee")
            return
        
        try:
            # Get base salary
            conn = sqlite3.connect('employee_finance.db')
            c = conn.cursor()
            c.execute("SELECT base_salary FROM employees WHERE id=?", (employee_id,))
            result = c.fetchone()
            
            if not result:
                messagebox.showerror("Error", "Employee not found in database")
                return
                
            base_salary = result[0]
            
            # Calculate overtime pay (assuming 1.5x hourly rate)
            hourly_rate = base_salary / 160  # assuming 160 working hours per month
            overtime_hours = float(entries['Overtime Hours'].get() or 0)
            overtime_pay = overtime_hours * hourly_rate * 1.5
            
            # Calculate net salary
            net_salary = (base_salary +
                         overtime_pay +
                         float(entries['Incentives'].get() or 0) -
                         float(entries['Advances'].get() or 0) -
                         float(entries['Loans'].get() or 0))
            
            # Save record
            c.execute("""INSERT INTO financial_records 
                        (employee_id, month, year, base_salary, overtime_hours,
                         overtime_pay, incentives, advances, loans, net_salary)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                     (employee_id, month, year, base_salary, overtime_hours,
                      overtime_pay, float(entries['Incentives'].get() or 0),
                      float(entries['Advances'].get() or 0),
                      float(entries['Loans'].get() or 0), net_salary))
            
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Financial record saved successfully!")
            self.show_admin_dashboard()
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for all financial fields")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    
    def show_add_employee(self):
        self.clear_frame()
        
        tk.Label(self.current_frame, text="Add New Employee", font=('Arial', 14, 'bold')).pack(pady=20)
        
        fields = {'Name': '', 'Position': '', 'Base Salary': '', 'Join Date': ''}
        entries = {}
        
        for field, value in fields.items():
            tk.Label(self.current_frame, text=field).pack(pady=5)
            entry = tk.Entry(self.current_frame)
            entry.insert(0, value)
            entry.pack(pady=5)
            entries[field] = entry
        
        tk.Button(self.current_frame, text="Add Employee", 
                 command=lambda: self.add_employee(entries)).pack(pady=10)
        tk.Button(self.current_frame, text="Back", 
                 command=self.show_admin_dashboard).pack(pady=5)

    def add_employee(self, entries):
        try:
            conn = sqlite3.connect('employee_finance.db')
            c = conn.cursor()
            c.execute("""INSERT INTO employees (name, position, base_salary, join_date)
                        VALUES (?, ?, ?, ?)""",
                     (entries['Name'].get(),
                      entries['Position'].get(),
                      float(entries['Base Salary'].get()),
                      entries['Join Date'].get()))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Employee added successfully!")
            self.show_admin_dashboard()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")


    def show_login(self):
        self.clear_frame()
        
        tk.Label(self.current_frame, text="Employee Financial Management System", font=('Arial', 16, 'bold')).pack(pady=20)
        
        tk.Label(self.current_frame, text="Username:").pack(pady=5)
        username_entry = tk.Entry(self.current_frame)
        username_entry.pack(pady=5)
        
        tk.Label(self.current_frame, text="Password:").pack(pady=5)
        password_entry = tk.Entry(self.current_frame, show="*")
        password_entry.pack(pady=5)
        
        tk.Button(self.current_frame, text="Login", command=lambda: self.login(username_entry.get(), password_entry.get())).pack(pady=10)
        tk.Button(self.current_frame, text="Register", command=self.show_register).pack(pady=5)
    def clear_frame(self):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = tk.Frame(self.root)
        self.current_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    def show_register(self):
        self.clear_frame()
        
        tk.Label(self.current_frame, text="Register New User", font=('Arial', 14, 'bold')).pack(pady=20)
        
        tk.Label(self.current_frame, text="Username:").pack(pady=5)
        username_entry = tk.Entry(self.current_frame)
        username_entry.pack(pady=5)
        
        tk.Label(self.current_frame, text="Password:").pack(pady=5)
        password_entry = tk.Entry(self.current_frame, show="*")
        password_entry.pack(pady=5)
        
        role_var = tk.StringVar(value="employee")
        tk.Radiobutton(self.current_frame, text="Employee", variable=role_var, value="employee").pack()
        tk.Radiobutton(self.current_frame, text="HR Admin", variable=role_var, value="admin").pack()
        
        tk.Button(self.current_frame, text="Register", 
                 command=lambda: self.register_user(username_entry.get(), 
                                                  password_entry.get(), 
                                                  role_var.get())).pack(pady=10)
        tk.Button(self.current_frame, text="Back to Login", command=self.show_login).pack(pady=5)
    def register_user(self, username, password, role):
        if not username or not password:
            messagebox.showerror("Error", "Please fill in all fields")
            return
            
        try:
            conn = sqlite3.connect('employee_finance.db')
            c = conn.cursor()
            c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                     (username, password, role))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Registration successful!")
            self.show_login()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def show_admin_dashboard(self):
        self.clear_frame()
        
        tk.Label(self.current_frame, text="Admin Dashboard", font=('Arial', 16, 'bold')).pack(pady=20)
        
        # Create buttons for different admin functions
        tk.Button(self.current_frame, text="Add New Employee", 
                 command=self.show_add_employee).pack(pady=5)
        tk.Button(self.current_frame, text="Manage Financial Records", 
                 command=self.show_manage_finances).pack(pady=5)
        tk.Button(self.current_frame, text="Generate Reports", 
                 command=self.show_reports).pack(pady=5)
        tk.Button(self.current_frame, text="Logout", 
                 command=self.show_login).pack(pady=20)        
    def login(self, username, password):
        if not username or not password:
            messagebox.showerror("Error", "Please fill in all fields")
            return
            
        conn = sqlite3.connect('employee_finance.db')
        c = conn.cursor()
        c.execute("SELECT role FROM users WHERE username=? AND password=?", (username, password))
        result = c.fetchone()
        conn.close()
        
        if result:
            self.current_user = {'username': username, 'role': result[0]}
            if result[0] == 'admin':
                self.show_admin_dashboard()
            else:
                self.show_employee_dashboard(username)
        else:
            messagebox.showerror("Error", "Invalid username or password")
    
    def show_reports(self):
        self.clear_frame()
        
        tk.Label(self.current_frame, text="Generate Reports", 
                font=('Arial', 14, 'bold')).pack(pady=20)
        
        # Create report type selection
        report_types = ["Monthly Payroll", "Employee Summary", "Department Summary"]
        report_var = tk.StringVar(value=report_types[0])
        
        for report_type in report_types:
            tk.Radiobutton(self.current_frame, text=report_type,
                          variable=report_var, value=report_type).pack()
        
        tk.Label(self.current_frame, text="Month (MM):").pack(pady=5)
        month_entry = tk.Entry(self.current_frame)
        month_entry.pack(pady=5)
        
        tk.Label(self.current_frame, text="Year (YYYY):").pack(pady=5)
        year_entry = tk.Entry(self.current_frame)
        year_entry.pack(pady=5)
        
        tk.Button(self.current_frame, text="Generate Report",
                 command=lambda: self.generate_report(
                     report_var.get(),
                     month_entry.get(),
                     year_entry.get())).pack(pady=10)
        tk.Button(self.current_frame, text="Back",
                 command=self.show_admin_dashboard).pack(pady=5)

    def generate_report(self, report_type, month, year):
        try:
            conn = sqlite3.connect('employee_finance.db')
            
            if report_type == "Monthly Payroll":
                query = """
                    SELECT e.name, e.position, f.base_salary, f.overtime_pay,
                           f.incentives, f.advances, f.loans, f.net_salary
                    FROM employees e
                    JOIN financial_records f ON e.id = f.employee_id
                    WHERE f.month = ? AND f.year = ?
                """
            elif report_type == "Employee Summary":
                query = """
                    SELECT e.name, e.position,
                           AVG(f.net_salary) as avg_salary,
                           SUM(f.overtime_pay) as total_overtime,
                           SUM(f.incentives) as total_incentives
                    FROM employees e
                    JOIN financial_records f ON e.id = f.employee_id
                    WHERE f.year = ?
                    GROUP BY e.id
                """
            else:  # Department Summary
                query = """
                    SELECT e.position as department,
                           COUNT(DISTINCT e.id) as employee_count,
                           AVG(f.net_salary) as avg_salary,
                           SUM(f.net_salary) as total_salary
                    FROM employees e
                    JOIN financial_records f ON e.id = f.employee_id
                    WHERE f.month = ? AND f.year = ?
                    GROUP BY e.position
                """
            
            params = (month, year) if report_type != "Employee Summary" else (year,)
            df = pd.read_sql_query(query, conn, params=params)
            conn.close()

            # Create a new window for the report
            report_window = tk.Toplevel(self.root)
            report_window.title(f"{report_type} Report")
            report_window.geometry("800x600")
            
            # Create a treeview to display the report
            tree = ttk.Treeview(report_window)
            tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Configure columns based on DataFrame
            tree["columns"] = list(df.columns)
            tree["show"] = "headings"
            
            for column in df.columns:
                tree.heading(column, text=column.replace('_', ' ').title())
                tree.column(column, width=100)
            
            # Add data to treeview
            for _, row in df.iterrows():
                tree.insert("", tk.END, values=list(row))
            
            # Add export button
            tk.Button(report_window, text="Export to Excel",
                     command=lambda: self.export_to_excel(df, report_type)).pack(pady=10)
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def export_to_excel(self, df, report_type):
        try:
            filename = f"{report_type.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            df.to_excel(filename, index=False)
            messagebox.showinfo("Success", f"Report exported successfully to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export report: {str(e)}")

    def show_employee_dashboard(self, username):
        self.clear_frame()
        
        tk.Label(self.current_frame, text=f"Welcome, {username}!", 
                font=('Arial', 16, 'bold')).pack(pady=20)
        
        # Get employee details
        conn = sqlite3.connect('employee_finance.db')
        c = conn.cursor()
        c.execute("""SELECT e.* 
                    FROM employees e
                    JOIN users u ON e.name = u.username
                    WHERE u.username = ?""", (username,))
        employee = c.fetchone()
        
        if employee:
            # Display employee information
            info_frame = tk.LabelFrame(self.current_frame, text="Employee Information", padx=10, pady=10)
            info_frame.pack(fill="x", padx=20, pady=10)
            
            labels = ["ID", "Name", "Position", "Base Salary", "Join Date"]
            for i, label in enumerate(labels):
                tk.Label(info_frame, text=f"{label}: {employee[i]}").pack(anchor="w")
            
            # Show recent financial records
            tk.Label(self.current_frame, text="Recent Financial Records", 
                    font=('Arial', 12, 'bold')).pack(pady=10)
            
            # Create treeview for financial records
            tree = ttk.Treeview(self.current_frame)
            tree.pack(fill=tk.BOTH, expand=True, padx=20)
            
            tree["columns"] = ["Month", "Year", "Base Salary", "Overtime", "Incentives", 
                             "Advances", "Loans", "Net Salary"]
            tree["show"] = "headings"
            
            for column in tree["columns"]:
                tree.heading(column, text=column)
                tree.column(column, width=100)
            
            # Get recent financial records
            c.execute("""SELECT month, year, base_salary, overtime_pay, incentives,
                               advances, loans, net_salary
                        FROM financial_records
                        WHERE employee_id = ?
                        ORDER BY year DESC, month DESC LIMIT 12""", (employee[0],))
            
            for record in c.fetchall():
                tree.insert("", tk.END, values=record)
        
        conn.close()
        
        # Add logout button
        tk.Button(self.current_frame, text="Logout", 
                 command=self.show_login).pack(pady=20)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = EmployeeFinanceSystem()
    app.run()