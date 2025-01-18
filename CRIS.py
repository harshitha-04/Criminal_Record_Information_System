import tkinter as tk
from tkinter import messagebox
import mysql.connector
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates


# Database connection configuration
db_config = {
    'host': 'localhost',
    'user': 'your_mysql_username',
    'password': 'your_mysql_password',
    'database': 'criminal_record_db'
}


# Database connection function
def connect_to_db():
    create_trigger(mysql.connector.connect(**db_config))
    return mysql.connector.connect(**db_config)

def create_trigger(connection):
    trigger_query = """
    CREATE TRIGGER after_case_update
    AFTER UPDATE ON Cases
    FOR EACH ROW
    BEGIN
        IF OLD.case_status != NEW.case_status THEN
            INSERT INTO CaseHistory (case_id, old_status, new_status, updated_at)
            VALUES (OLD.case_id, OLD.case_status, NEW.case_status, NOW());
        END IF;
    END;
    """
    cursor = connection.cursor()
    try:
        cursor.execute("DROP TRIGGER IF EXISTS after_case_update")
        cursor.execute(trigger_query)
        connection.commit()
    except mysql.connector.Error as err:
        print(f"Trigger creation failed: {err}")
    finally:
        cursor.close()

        
#Home Window
class HomePage(tk.Tk):
    def _init_(self):
        super()._init_()
        self.title("Home Page")
        self.geometry("800x600")
        #self.configure(bg="black")

        # Logo
        self.logo_label = tk.Label(self, text="Your Logo Here", font=("Helvetica", 24))
        self.logo_label.pack(pady=100)

        # Continue Button
        self.continue_button = tk.Button(self, text="Continue", command=self.open_login, font=("Helvetica", 16))
        self.continue_button.pack(pady=20)

    def open_login(self):
        self.destroy()  # Close the home page
        login_window = LoginWindow()
        login_window.mainloop()
        
# Login Window
class LoginWindow(tk.Tk):
    def _init_(self):
        super()._init_()
        self.title("Login")
        self.geometry("800x600")
        #self.configure(bg="black")  # Set window background to black

        tk.Label(self, text="Username:").pack(pady=10)
        self.username_entry = tk.Entry(self)
        self.username_entry.pack()

        tk.Label(self, text="Password:").pack(pady=10)
        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.pack()

        tk.Button(self, text="Login", command=self.login).pack(pady=20)  # Set button color to white


    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password.")
            return

        db = connect_to_db()
        cursor = db.cursor()

        cursor.execute("SELECT user_id, username, role FROM Users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()

        if user:
            user_id, username, role = user
            self.grant_privileges(role, db, cursor)  # Grant privileges based on the role
            self.destroy()
            if role == 'police':
                PoliceDashboard(user_id).mainloop()
            elif role == 'victim':
                VictimDashboard(user_id).mainloop()
            else:
                messagebox.showerror("Error", "Access restricted to police officers and victims only.")
        else:
            messagebox.showerror("Error", "Invalid username or password.")

        db.close()

    def grant_privileges(self, role, db, cursor):
        """ Grant privileges based on the user's role """
        if role == 'police':
            grant_query = """
        GRANT ALL PRIVILEGES ON criminal_record_db.* TO 'police'@'localhost';
        """
        elif role == 'victim':
            grant_query = """
            GRANT SELECT ON criminal_record_db.Users TO 'victim'@'localhost';
        """
        try:
            cursor.execute(grant_query)
            db.commit()
            print(f"Privileges granted successfully for role: {role}")
        except mysql.connector.Error as err:
            db.rollback()
            print(f"Error granting privileges: {err}")


class PoliceDashboard(tk.Tk):
    def _init_(self, user_id):
        super()._init_()
        self.user_id = user_id
        self.title("Police Dashboard")
        self.geometry("600x400")
      #  self.configure(bg='black')

        tk.Button(self, text="Manage Cases", command=self.manage_cases).pack()
        tk.Button(self, text="Manage Complaints", command=self.manage_complaints).pack()
        tk.Button(self, text="Related", command=self.show_related_cases_and_complaints).pack()  # Added Related Button
        tk.Button(self, text="Show Cases Graph", command=self.display_case_status_bar_graph).pack(pady=20)

    def manage_cases(self):
        CaseManagement(self.user_id)

    def manage_complaints(self):
        ComplaintManagement(self.user_id)
        
    def show_related_cases_and_complaints(self):
        # Function to show related cases and complaints where status is not 'Resolved'
        db = connect_to_db()
        cursor = db.cursor()

        query = """
        SELECT C.case_id, C.case_type, C.description, C.case_status, 
               Compl.complaint_id, Compl.description AS complaint_description, Compl.status AS complaint_status
        FROM Cases C
        JOIN Complaints Compl ON C.case_id = Compl.case_id
        WHERE Compl.status != 'Resolved'
        """
        cursor.execute(query)
        related_data = cursor.fetchall()
        db.close()

        if related_data:
            self.show_related_data(related_data)
        else:
            messagebox.showinfo("No Data", "No related cases and complaints found.")

    def show_related_data(self, related_data):
        """ Display related case and complaint data in a new window """
        related_window = tk.Toplevel(self)
        related_window.title("Related Cases and Complaints")
        related_window.geometry("600x400")

        listbox = tk.Listbox(related_window, width=80, height=20)
        listbox.pack(pady=10)

        for data in related_data:
            case_id, case_type, case_description, case_status, complaint_id, complaint_description, complaint_status = data
            listbox.insert(tk.END, f"Case ID: {case_id} - {case_type} - {case_description} - Status: {case_status}")
            listbox.insert(tk.END, f"Complaint ID: {complaint_id} - {complaint_description} - Status: {complaint_status}")
            listbox.insert(tk.END, "-" * 80)  # Add separator between cases and complaints

    def display_case_status_bar_graph(self):
        """ Display a bar graph of case statuses """
        db = connect_to_db()
        cursor = db.cursor()

        # Query to count the number of cases by status
        cursor.execute("""
            SELECT case_status, COUNT(*) 
            FROM Cases 
            GROUP BY case_status
        """)
        case_status_data = cursor.fetchall()
        db.close()

        if case_status_data:
            # Prepare data for the graph
            statuses = [status for status, _ in case_status_data]
            case_counts = [count for _, count in case_status_data]

            # Create a bar graph
            fig, ax = plt.subplots(figsize=(6, 4))
            ax.bar(statuses, case_counts, color='black')

            ax.set_xlabel('Case Status')
            ax.set_ylabel('Number of Cases')
            ax.set_title('Number of Cases by Status')

            # Embed the graph in the tkinter window
            canvas = FigureCanvasTkAgg(fig, self)
            canvas.get_tk_widget().pack(pady=20)
            canvas.draw()
        else:
            messagebox.showinfo("No Data", "No case status data found.")

            
# Complaint Management
class ComplaintManagement(tk.Toplevel):
    def _init_(self, user_id):
        super()._init_()
        self.user_id = user_id
        self.title("Complaint Management")
        self.geometry("500x400")
        #self.configure(bg='black')

        tk.Label(self, text="Complaint Description:").grid(row=0, column=0, sticky='e')
        self.complaint_description_entry = tk.Entry(self, width=30)
        self.complaint_description_entry.grid(row=0, column=1)

        tk.Label(self, text="Complainant Name:").grid(row=1, column=0, sticky='e')
        self.complainant_name_entry = tk.Entry(self, width=30)
        self.complainant_name_entry.grid(row=1, column=1)

        tk.Button(self, text="Add Complaint", command=self.add_complaint).grid(row=2, column=1, pady=10)
        
        self.complaint_listbox = tk.Listbox(self, width=60, height=15)
        self.complaint_listbox.grid(row=3, column=0, columnspan=2, padx=10, pady=5)

        tk.Button(self, text="Mark as Resolved", command=lambda: self.update_complaint_status("Resolved")).grid(row=4, column=0, sticky='e', padx=5, pady=10)
        tk.Button(self, text="Mark as In Progress", command=lambda: self.update_complaint_status("In Progress")).grid(row=4, column=1, sticky='w', padx=5, pady=10)

        self.fetch_complaints()
        self.create_stored_procedure()

    def create_stored_procedure(self):
        """ Create the AddComplaint stored procedure if it does not exist """
        db = connect_to_db()
        cursor = db.cursor()

        try:
            # SQL to create the stored procedure
            procedure_sql = """

            CREATE PROCEDURE IF NOT EXISTS AddComplaint(
                IN complaint_desc VARCHAR(255),
                IN complainant_name VARCHAR(255),
                IN police_id INT
            )
            BEGIN
                INSERT INTO Complaints (description, complainant_name, status, police_id)
                VALUES (complaint_desc, complainant_name, 'Pending', police_id);
            END ;
            """

            # Execute the stored procedure creation
            cursor.execute(procedure_sql)
            db.commit()
            print("Stored procedure created successfully.")
        except mysql.connector.Error as err:
            db.rollback()
            print(f"Error creating procedure: {err}")
        finally:
            db.close()

    def add_complaint(self):
        description = self.complaint_description_entry.get()
        complainant_name = self.complainant_name_entry.get()

        if not description or not complainant_name:
            messagebox.showerror("Error", "Please fill in all fields.")
            return

        db = connect_to_db()
        cursor = db.cursor()

        try:
            # Call the stored procedure to add the complaint
            cursor.callproc('AddComplaint', (description, complainant_name, self.user_id))
            db.commit()
            messagebox.showinfo("Success", "Complaint added successfully.")
            self.fetch_complaints()
        except mysql.connector.Error as err:
            db.rollback()
            messagebox.showerror("Error", f"Error adding complaint: {err}")
        finally:
            db.close()

    def fetch_complaints(self):
        db = connect_to_db()
        cursor = db.cursor()

        cursor.execute("SELECT complaint_id, description, complainant_name, status FROM Complaints WHERE police_id = %s", (self.user_id,))
        complaints = cursor.fetchall()
        db.close()

        self.complaint_listbox.delete(0, tk.END)
        for complaint in complaints:
            complaint_id, description, complainant_name, status = complaint
            self.complaint_listbox.insert(tk.END, f"ID: {complaint_id} - {description} by {complainant_name} - Status: {status}")

    def update_complaint_status(self, status):
        selected_item = self.complaint_listbox.curselection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a complaint from the list.")
            return

        complaint_text = self.complaint_listbox.get(selected_item[0])
        complaint_id = complaint_text.split(" - ")[0].split(": ")[1]

        db = connect_to_db()
        cursor = db.cursor()

        try:
            cursor.execute("UPDATE Complaints SET status = %s WHERE complaint_id = %s", (status, complaint_id))
            db.commit()
            messagebox.showinfo("Success", f"Complaint marked as {status}.")
            self.fetch_complaints()
        except mysql.connector.Error as err:
            db.rollback()
            messagebox.showerror("Error", f"Error updating complaint: {err}")
        finally:
            db.close()

# Victim Dashboard
class VictimDashboard(tk.Tk):
    def _init_(self, user_id):
        super()._init_()
        self.user_id = user_id
        self.title("Victim Dashboard")
        self.geometry("600x400")
        #self.configure(bg='black')

        tk.Label(self, text="Your Cases and Complaints").pack(pady=10)
        tk.Button(self, text="View Your Cases and Complaints", command=self.view_cases_and_complaints).pack(pady=20)

        self.listbox = tk.Listbox(self, width=80, height=20)
        self.listbox.pack(pady=10)

    def view_cases_and_complaints(self):
        self.listbox.delete(0, tk.END)
        self.fetch_cases()
        self.fetch_complaints()

    def fetch_cases(self):
        db = connect_to_db()
        cursor = db.cursor()

        # Fetch cases related to the victim
        cursor.execute("SELECT case_id, case_type, description, place, accused, lawyer, case_status FROM Cases WHERE victim_id = %s", (self.user_id,))
        cases = cursor.fetchall()
        db.close()

        self.listbox.insert(tk.END, "Your Cases:")
        for case in cases:
            case_id, case_type, description, place, accused, lawyer, status = case
            self.listbox.insert(tk.END, f"ID: {case_id} - Type: {case_type} - Desc: {description} - Status: {status}")
        self.listbox.insert(tk.END, "")  # Add space between cases and complaints

    def fetch_complaints(self):
        db = connect_to_db()
        cursor = db.cursor()

        # Fetch complaints related to the victim
        cursor.execute("SELECT complaint_id, description, status FROM Complaints WHERE complainant_id = %s", (self.user_id,))
        complaints = cursor.fetchall()
        db.close()

        self.listbox.insert(tk.END, "Your Complaints:")
        for complaint in complaints:
            complaint_id, description, status = complaint
            self.listbox.insert(tk.END, f"ID: {complaint_id} - Desc: {description} - Status: {status}")

# Case Management with Victim List
class CaseManagement(tk.Toplevel):
    def _init_(self, user_id, victim_view=False):
        super()._init_()
        self.user_id = user_id
        self.victim_view = victim_view
        self.title("Case Management")
        self.geometry("600x400")
        #self.configure(bg='black')

        if not self.victim_view:
            tk.Label(self, text="Case Type:").grid(row=0, column=0, sticky='e')
            self.case_type_entry = tk.Entry(self)
            self.case_type_entry.grid(row=0, column=1)

            tk.Label(self, text="Description:").grid(row=1, column=0, sticky='e')
            self.description_entry = tk.Entry(self)
            self.description_entry.grid(row=1, column=1)

            tk.Label(self, text="Place:").grid(row=2, column=0, sticky='e')
            self.place_entry = tk.Entry(self)
            self.place_entry.grid(row=2, column=1)

            tk.Label(self, text="Accused:").grid(row=3, column=0, sticky='e')
            self.accused_entry = tk.Entry(self)
            self.accused_entry.grid(row=3, column=1)

            tk.Label(self, text="Lawyer:").grid(row=4, column=0, sticky='e')
            self.lawyer_entry = tk.Entry(self)
            self.lawyer_entry.grid(row=4, column=1)

            tk.Label(self, text="Victim ID (Select victim):").grid(row=5, column=0, sticky='e')
            self.victim_id_entry = tk.Entry(self)
            self.victim_id_entry.grid(row=5, column=1)

            # Adding case status input field
            tk.Label(self, text="Case Status:").grid(row=6, column=0, sticky='e')
            self.case_status_entry = tk.Entry(self)
            self.case_status_entry.grid(row=6, column=1)

            tk.Button(self, text="Add Case", command=self.add_case).grid(row=7, column=1, pady=10)
            tk.Button(self, text="Update Case", command=self.update_case).grid(row=7, column=0, pady=10)
            tk.Button(self, text="Delete Case", command=self.delete_case).grid(row=8, column=1, pady=10)  # Delete button


        self.case_listbox = tk.Listbox(self, width=60, height=15)
        self.case_listbox.grid(row=1, column=2, rowspan=5, padx=10, pady=5)
        self.fetch_cases()

    def fetch_cases(self):
        db = connect_to_db()
        cursor = db.cursor()

        cursor.execute("SELECT case_id, case_type, description, place, accused, lawyer, case_status FROM Cases WHERE police_id = %s", (self.user_id,))
        cases = cursor.fetchall()
        db.close()

        self.case_listbox.delete(0, tk.END)
        for case in cases:
            case_id, case_type, description, place, accused, lawyer, status = case
            self.case_listbox.insert(tk.END, f"ID: {case_id} - {case_type} - {description} - Status: {status}")

    def add_case(self):
        case_type = self.case_type_entry.get()
        description = self.description_entry.get()
        place = self.place_entry.get()
        accused = self.accused_entry.get()
        lawyer = self.lawyer_entry.get()
        victim_id = self.victim_id_entry.get()
        case_status = self.case_status_entry.get()

        if not case_type or not description or not place or not accused or not lawyer or not victim_id or not case_status:
            messagebox.showerror("Error", "Please fill in all fields.")
            return

        db = connect_to_db()
        cursor = db.cursor()

        try:
            cursor.execute(
                "INSERT INTO Cases (case_type, description, place, accused, lawyer, case_status, police_id, victim_id) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (case_type, description, place, accused, lawyer, case_status, self.user_id, victim_id)
            )
            db.commit()
            messagebox.showinfo("Success", "Case added successfully.")
            self.fetch_cases()
        except mysql.connector.Error as err:
            db.rollback()
            messagebox.showerror("Error", f"Error adding case: {err}")
        finally:
            db.close()

    def update_case(self):
        selected_item = self.case_listbox.curselection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a case from the list to update.")
            return

        case_text = self.case_listbox.get(selected_item[0])
        case_id = case_text.split(" - ")[0].split(": ")[1]

        db = connect_to_db()
        cursor = db.cursor()

        cursor.execute("SELECT case_type, description, place, accused, lawyer, case_status FROM Cases WHERE case_id = %s", (case_id,))
        case = cursor.fetchone()

        if case:
            case_type, description, place, accused, lawyer, case_status = case
            # Populate the entry fields with current case details
            self.case_type_entry.delete(0, tk.END)
            self.case_type_entry.insert(0, case_type)

            self.description_entry.delete(0, tk.END)
            self.description_entry.insert(0, description)

            self.place_entry.delete(0, tk.END)
            self.place_entry.insert(0, place)

            self.accused_entry.delete(0, tk.END)
            self.accused_entry.insert(0, accused)

            self.lawyer_entry.delete(0, tk.END)
            self.lawyer_entry.insert(0, lawyer)

            self.case_status_entry.delete(0, tk.END)
            self.case_status_entry.insert(0, case_status)

            # Change the "Add Case" button to "Save Changes"
            tk.Button(self, text="Save Changes", command=lambda: self.save_case_changes(case_id)).grid(row=7, column=1, pady=10)

    def save_case_changes(self, case_id):
    # Retrieve updated values from the entry fields
        updated_case_type = self.case_type_entry.get()
        updated_description = self.description_entry.get()
        updated_place = self.place_entry.get()
        updated_accused = self.accused_entry.get()
        updated_lawyer = self.lawyer_entry.get()
        updated_case_status = self.case_status_entry.get()

    # Connect to the database
        db = connect_to_db()
        cursor = db.cursor()

        try:
        # Execute the update query
            cursor.execute("""
                UPDATE Cases 
                SET case_type = %s, description = %s, place = %s, accused = %s, lawyer = %s, case_status = %s
                WHERE case_id = %s
            """, (updated_case_type, updated_description, updated_place, updated_accused, updated_lawyer, updated_case_status, case_id))

        # Commit changes to the database
            db.commit()

        # Provide feedback to the user
            messagebox.showinfo("Success", "Case details updated successfully.")

        # Optionally, refresh the case listbox or clear the fields
            self.clear_fields()
            self.refresh_case_listbox()

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error updating case: {err}")
        finally:
            cursor.close()
            db.close()

    def delete_case(self):
        selected_item = self.case_listbox.curselection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a case from the list to delete.")
            return

        case_text = self.case_listbox.get(selected_item[0])
        case_id = case_text.split(" - ")[0].split(": ")[1]

        db = connect_to_db()
        cursor = db.cursor()

        try:
            cursor.execute("DELETE FROM Cases WHERE case_id = %s", (case_id,))
            db.commit()
            messagebox.showinfo("Success", "Case deleted successfully.")
            self.fetch_cases()
        except mysql.connector.Error as err:
            db.rollback()
            messagebox.showerror("Error", f"Error deleting case: {err}")
        finally:
            db.close()


if _name_ == "_main_":
    login_window = LoginWindow()
    login_window.mainloop()
