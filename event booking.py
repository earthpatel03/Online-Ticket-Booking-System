import mysql.connector
import qrcode
import os
import random
from datetime import datetime, timedelta


# ---------------- DATABASE CONNECTION ----------------
try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1111",
        database="event_system"
    )
    cursor = conn.cursor()
except:
    print("❌ Database connection failed")
    exit()

# ---------------- QR CODE FUNCTION ----------------
def generate_qr(booking_id, user_name, event_name, tickets):
    data = f"""
    🎟 EVENT TICKET
    -----------------------
    Booking ID: {booking_id}
    Name: {user_name}
    Event: {event_name}
    Tickets: {tickets}
    Status: CONFIRMED
    """

    qr = qrcode.make(data)

    if not os.path.exists("tickets"):
        os.makedirs("tickets")

    file_name = f"tickets/ticket_{booking_id}.png"
    qr.save(file_name)

    print(f"📱 QR Code Saved: {file_name}")

# ---------------- REGISTER ----------------
def register():
    name = input("Enter Name: ")
    email = input("Enter Email: ")
    password = input("Enter Password: ")

    try:
        cursor.execute(
            "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
            (name, email, password)
        )
        conn.commit()
        print("✅ Registration Successful")
    except:
        print("❌ Email already exists")

# ---------------- LOGIN ----------------
def login():
    email = input("Enter Email: ")
    password = input("Enter Password: ")

    cursor.execute(
        "SELECT user_id, name FROM users WHERE email=%s AND password=%s",
        (email, password)
    )
    user = cursor.fetchone()

    if user:
        print("✅ Login Successful")
        return user  # (user_id, name)
    else:
        print("❌ Invalid Credentials")
        return None

# ---------------- VIEW EVENTS ----------------
def view_events():
    cursor.execute("SELECT * FROM events")
    events = cursor.fetchall()

    print("\n🎟 Available Events:")
    for e in events:
        print(f"ID: {e[0]} | {e[1]} | Date: {e[2]} | Seats Left: {e[4]}")

# ---------------- BOOK TICKET ----------------
def book_ticket(user_id, user_name):
    view_events()

    try:
        event_id = int(input("Enter Event ID: "))
        tickets = int(input("Enter Number of Tickets: "))
    except:
        print("❌ Invalid input")
        return

    cursor.execute("SELECT event_name, available_seats FROM events WHERE event_id=%s", (event_id,))
    result = cursor.fetchone()

    if result:
        event_name, available = result

        if available >= tickets:
            cursor.execute(
                "INSERT INTO bookings (user_id, event_id, tickets) VALUES (%s, %s, %s)",
                (user_id, event_id, tickets)
            )

            booking_id = cursor.lastrowid

            cursor.execute(
                "UPDATE events SET available_seats = available_seats - %s WHERE event_id=%s",
                (tickets, event_id)
            )

            conn.commit()

            print("🎉 Ticket Booked Successfully")

            # QR CODE
            generate_qr(booking_id, user_name, event_name, tickets)

        else:
            print("❌ Not enough seats available")
    else:
        print("❌ Event not found")

# ---------------- CANCEL TICKET ----------------
def cancel_ticket(user_id):
    cursor.execute("SELECT * FROM bookings WHERE user_id=%s", (user_id,))
    bookings = cursor.fetchall()

    if not bookings:
        print("❌ No bookings found")
        return

    for b in bookings:
        print(f"Booking ID: {b[0]} | Event ID: {b[2]} | Tickets: {b[3]}")

    try:
        booking_id = int(input("Enter Booking ID to cancel: "))
    except:
        print("❌ Invalid input")
        return

    cursor.execute(
        "SELECT event_id, tickets FROM bookings WHERE booking_id=%s AND user_id=%s",
        (booking_id, user_id)
    )
    data = cursor.fetchone()

    if data:
        event_id, tickets = data

        cursor.execute("DELETE FROM bookings WHERE booking_id=%s", (booking_id,))
        cursor.execute(
            "UPDATE events SET available_seats = available_seats + %s WHERE event_id=%s",
            (tickets, event_id)
        )

        conn.commit()
        print("✅ Booking Cancelled")
    else:
        print("❌ Invalid Booking ID")

# ---------------- ADMIN VIEW ----------------
def admin_view():
    cursor.execute("""
        SELECT b.booking_id, u.name, e.event_name, b.tickets
        FROM bookings b
        JOIN users u ON b.user_id = u.user_id
        JOIN events e ON b.event_id = e.event_id
    """)

    data = cursor.fetchall()

    print("\n📊 All Bookings:")
    for d in data:
        print(f"Booking ID: {d[0]} | User: {d[1]} | Event: {d[2]} | Tickets: {d[3]}")

# ---------------- MAIN MENU ----------------
def main():
    while True:
        print("\n===== EVENT SYSTEM =====")
        print("1. Register")
        print("2. Login")
        print("3. Admin View")
        print("4. Exit")

        choice = input("Enter choice: ")

        if choice == "1":
            register()

        elif choice == "2":
            user = login()
            if user:
                user_id, user_name = user

                while True:
                    print("\n--- USER MENU ---")
                    print("1. View Events")
                    print("2. Book Ticket")
                    print("3. Cancel Ticket")
                    print("4. Logout")

                    user_choice = input("Enter choice: ")

                    if user_choice == "1":
                        view_events()
                    elif user_choice == "2":
                        book_ticket(user_id, user_name)
                    elif user_choice == "3":
                        cancel_ticket(user_id)
                    elif user_choice == "4":
                        break
                    else:
                        print("❌ Invalid Choice")

        elif choice == "3":
            admin_view()

        elif choice == "4":
            print("👋 Exit")
            break

        else:
            print("❌ Invalid Choice")

# ---------------- RUN ----------------
main()