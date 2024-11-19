import qrcode
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

# SQLite database setup
conn = sqlite3.connect('seat_booking.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS bookings (
    seat_no INTEGER PRIMARY KEY,
    passenger_name TEXT,
    class_type TEXT,
    UNIQUE(seat_no)
)
''')
conn.commit()

total_rows = 10
total_columns = 10
booked_seats = set()
passengers = {}

class BookingDialog(tk.simpledialog.Dialog):
    def body(self, master):
        tk.Label(master, text="Class:").grid(row=0, sticky=tk.W)
        tk.Label(master, text="Number of Passengers:").grid(row=1, sticky=tk.W)
        tk.Label(master, text="Payment Method (Credit Card/Debit Card/Net Banking/UPI):").grid(row=2, sticky=tk.W)

        self.class_entry = tk.Entry(master)
        self.num_passengers_entry = tk.Entry(master)
        self.payment_entry = tk.Entry(master)

        self.class_entry.grid(row=0, column=1)
        self.num_passengers_entry.grid(row=1, column=1)
        self.payment_entry.grid(row=2, column=1)

        return self.class_entry  # Initial focus

    def apply(self):
        self.result = {
            'class': self.class_entry.get().lower(),
            'num_passengers': int(self.num_passengers_entry.get()),
            'payment_method': self.payment_entry.get().lower()
        }

class SeatBookingApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Seat Booking System")

        self.create_widgets()

    def create_widgets(self):
        style = ttk.Style()
        style.theme_use("clam")  # You can change the theme as per your preference

        self.label = tk.Label(self.master, text="Seat Booking System", font=("Helvetica", 16))
        self.label.grid(row=0, column=0, columnspan=2, pady=10)

        self.book_button = tk.Button(self.master, text="Book Seats", command=self.book_seats)
        self.book_button.grid(row=1, column=0, columnspan=2, pady=10)

        self.cancel_button = tk.Button(self.master, text="Cancel Ticket", command=self.cancel_ticket)
        self.cancel_button.grid(row=2, column=0, columnspan=2, pady=10)

    def book_seats(self):
        booking_info = BookingDialog(self.master).result

        class_type = booking_info['class']
        num_passengers = booking_info['num_passengers']
        total_amount = 500 * num_passengers

        for _ in range(num_passengers):
            name = self.show_input_dialog("Enter name of the passenger:")
            gender = self.show_input_dialog("Enter gender (M/F/O):")
            age = int(self.show_input_dialog("Enter age of the passenger:"))

            while True:
                try:
                    seat_input = self.show_input_dialog("Please enter the seat number:")
                    seat_no = int(seat_input)
                    if 1 <= seat_no <= total_rows * total_columns and self.book_seat(seat_no, name, class_type):
                        break
                    else:
                        self.show_error_message(f"Seat {seat_no} is already booked or invalid. Please choose another seat.")
                except ValueError:
                    self.show_error_message("Please enter a valid integer for the seat number.")

        payment = booking_info['payment_method']

        if payment.lower() == 'upi':
            upi_id = "6205935955@paytm"  # Your UPI ID
            self.generate_upi_qr(upi_id, total_amount)
            message = f"Your payment is complete.\nYour seats are booked.\nHappy journey!\n"
            
            # Save data to the database
            self.save_to_database()
        elif payment.lower() == 'credit card':
            # Placeholder for credit card payment
            message = "Credit card payment is a placeholder and not implemented."
        elif payment.lower() == 'debit card':
            # Placeholder for debit card payment
            message = "Debit card payment is a placeholder and not implemented."
        elif payment.lower() == 'net banking':
            # Placeholder for net banking payment
            message = "Net banking payment is a placeholder and not implemented."
        else:
            message = "Invalid payment method entered."
        
        self.show_info_message(message)

    def book_seat(self, seat_no, passenger_name, class_type):
        global total_rows, total_columns, booked_seats, passengers
        if seat_no in booked_seats or seat_no > total_rows * total_columns:
            self.show_error_message(f"Seat {seat_no} is already booked or an invalid seat number.")
            return False
        else:
            booked_seats.add(seat_no)
            passengers[seat_no] = {'name': passenger_name, 'class': class_type}
            return True

    def generate_upi_qr(self, upi_id, amount):
        upi_url = f"upi://pay?pa={upi_id}&am={amount}"  # Dynamic amount for seat payment
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(upi_url)
        qr.make(fit=True)
        qr_img = qr.make_image(fill='black', back_color='white')
        qr_img.show()  # Display QR code
        print(f"Scan the QR code to pay {amount} using UPI.")

    def save_to_database(self):
        for seat_no, data in passengers.items():
            cursor.execute('INSERT INTO bookings (seat_no, passenger_name, class_type) VALUES (?, ?, ?)',
                           (seat_no, data['name'], data['class']))
        conn.commit()

    def cancel_ticket(self):
        seat_input = self.show_input_dialog("Enter the seat number to cancel:")
        try:
            seat_no = int(seat_input)
            if seat_no in passengers:
                booked_seats.remove(seat_no)
                del passengers[seat_no]
                cursor.execute('DELETE FROM bookings WHERE seat_no = ?', (seat_no,))
                conn.commit()
                self.show_info_message(f"Ticket for Seat {seat_no} has been canceled.")
            else:
                self.show_error_message(f"No booking found for Seat {seat_no}.")
        except ValueError:
            self.show_error_message("Please enter a valid integer for the seat number.")

    def show_input_dialog(self, prompt):
        return simpledialog.askstring("Input", prompt)

    def show_error_message(self, message):
        messagebox.showerror("Error", message)

    def show_info_message(self, message):
        messagebox.showinfo("Information", message)


# Create the main window
root = tk.Tk()
app = SeatBookingApp(root)
root.mainloop()

# Close the database connection when the program exits
conn.close()
