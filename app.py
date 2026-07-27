from flask import Flask, request, jsonify, render_template, session, redirect, url_for
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta # Add timedelta here
import csv
from io import StringIO
from flask import Response # Make sure Response is added to your existing flask imports!

app = Flask(__name__)
app.secret_key = "2b7d8f9a4c5e6d7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d"

app.permanent_session_lifetime = timedelta(minutes=30)

# --- Admin Credentials ---
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin@123"

# --- Email Configuration ---
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "mahdeeali1111@gmail.com"
SENDER_PASSWORD = "udvg wjsz eabh zhvp" 
OWNER_EMAIL = "mahdeeali1111@gmail.com"

# --- MySQL Database Configuration ---
DB_CONFIG = {
    'host': 'localhost',      # Change if your MySQL is hosted elsewhere
    'user': 'root',           # Your MySQL username
    'password': 'root',           # Your MySQL password
    'database': 'portfolio_db'
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

def init_db():
    try:
        # 1. Connect without targeting a specific database first
        conn = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        c = conn.cursor()
        # Create the database if it doesn't exist
        c.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
        conn.close()

        # 2. Reconnect directly to the new database
        conn = get_db_connection()
        c = conn.cursor()
        
        # Create the table using MySQL syntax
        c.execute('''
            CREATE TABLE IF NOT EXISTS bookings (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL,
                project_type VARCHAR(255) NOT NULL,
                budget VARCHAR(255),
                message TEXT,
                status VARCHAR(50) DEFAULT 'Pending',
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
        print("MySQL Database Initialized Successfully!")
    except Error as e:
        print(f"Error connecting to MySQL: {e}")

# Initialize the database on startup
init_db()

# --- Public Routes ---
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/submit-booking', methods=['POST'])
def submit_booking():
    data = request.json
    name = data.get('name')
    client_email = data.get('email')
    project_type = data.get('project_type')
    
    # 1. FIXED BUDGET LOGIC: Catches empty strings ("") sent from the frontend
    raw_budget = data.get('budget')
    budget = raw_budget if raw_budget else 'Not specified'
    
    message_content = data.get('message')

    # --- Save to MySQL Database ---
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('''
            INSERT INTO bookings (name, email, project_type, budget, message, status)
            VALUES (%s, %s, %s, %s, %s, 'Pending')
        ''', (name, client_email, project_type, budget, message_content))
        conn.commit()
        conn.close()
    except Error as e:
        print(f"Database Error: {e}")
        return jsonify({"status": "error", "message": "Failed to save booking."}), 500

    # --- Send HTML Emails ---
    email_errors = False
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)

        # 2A. Email Notification to YOU (The Admin)
        try:
            msg_owner = MIMEMultipart('alternative')
            msg_owner['From'] = SENDER_EMAIL
            msg_owner['To'] = OWNER_EMAIL
            msg_owner['Subject'] = f"🚨 New Project Lead: {name}"
            
            html_owner = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f9f9f9; border: 1px solid #ddd; border-radius: 8px;">
                <h2 style="color: #8b5cf6; margin-top: 0; text-transform: uppercase;">New Project Inquiry</h2>
                <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
                    <tr><td style="padding: 10px 0; border-bottom: 1px solid #eee;"><strong>Client Name:</strong></td><td style="padding: 10px 0; border-bottom: 1px solid #eee;">{name}</td></tr>
                    <tr><td style="padding: 10px 0; border-bottom: 1px solid #eee;"><strong>Email:</strong></td><td style="padding: 10px 0; border-bottom: 1px solid #eee;"><a href="mailto:{client_email}" style="color: #3b82f6;">{client_email}</a></td></tr>
                    <tr><td style="padding: 10px 0; border-bottom: 1px solid #eee;"><strong>Project Type:</strong></td><td style="padding: 10px 0; border-bottom: 1px solid #eee;">{project_type}</td></tr>
                    <tr><td style="padding: 10px 0; border-bottom: 1px solid #eee;"><strong>Estimated Budget:</strong></td><td style="padding: 10px 0; border-bottom: 1px solid #eee; color: #10b981; font-weight: bold;">${budget}</td></tr>
                </table>
                <h3 style="margin-bottom: 10px; color: #333;">Client Message:</h3>
                <p style="background: #ffffff; padding: 15px; border-radius: 6px; border: 1px solid #eee; white-space: pre-wrap; color: #555; line-height: 1.5;">{message_content}</p>
            </div>
            """
            msg_owner.attach(MIMEText(html_owner, 'html'))
            server.send_message(msg_owner)
        except Exception as e:
            print(f"Failed to send owner email: {e}")
            email_errors = True

        # 2B. Confirmation Email to the CUSTOMER
        try:
            msg_client = MIMEMultipart('alternative')
            msg_client['From'] = SENDER_EMAIL 
            msg_client['To'] = client_email
            msg_client['Subject'] = "Your Project Request Received!"
            
            # 1. Create the Plain Text version (For the Spam Filters)
            text_client = f"""
            Hi {name},
            
            Thank you for reaching out! I have successfully received your project inquiry for {project_type}.
            
            I will review your project details and the estimated budget of ${budget}. If it's a good fit, I will get back to you within 24-48 hours.
            
            Best regards,
            Cloudious Fernandez
            """
            
            # 2. Create the HTML version (For the User)
            html_client = f"""
            <div style="font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; max-width: 600px; margin: 0 auto; color: #333333; padding: 20px;">
                <h2 style="color: #8b5cf6;">Request Received!</h2>
                <p style="font-size: 16px; line-height: 1.6;">Hi {name},</p>
                <p style="font-size: 16px; line-height: 1.6;">Thank you for reaching out! This is an automated confirmation that I have successfully received your project inquiry for <strong>{project_type}</strong>.</p>
                
                <div style="background-color: #f4f4f5; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <p style="margin: 0; font-weight: bold; margin-bottom: 10px;">Here is what happens next:</p>
                    <ul style="margin: 0; padding-left: 20px; line-height: 1.6;">
                        <li>I will personally review your project details and the estimated budget of <strong>${budget}</strong>.</li>
                        <li>If the project is a good fit, I will get back to you within 24-48 hours with some initial thoughts or a link to schedule a quick discovery call.</li>
                    </ul>
                </div>
                
                <p style="font-size: 16px; line-height: 1.6;">I'm looking forward to potentially collaborating with you!</p>
                <br>
                <p style="font-size: 16px; margin-bottom: 5px;">Best regards,</p>
                <p style="font-size: 16px; margin-top: 0;">
                    <strong>Cloudious Fernandez</strong><br>
                    <span style="color: #71717a; font-size: 14px;">Video Editor & Motion Graphics Artist</span>
                </p>
            </div>
            """
            
            # 3. Attach BOTH! (Order matters: attach text first, then HTML)
            msg_client.attach(MIMEText(text_client, 'plain'))
            msg_client.attach(MIMEText(html_client, 'html'))
            
            server.send_message(msg_client)
        except Exception as e:
            print(f"Failed to send customer email: {e}")
            email_errors = True

        server.quit()
        
        if email_errors:
            return jsonify({"status": "success", "message": "Booking saved (some emails failed)."}), 200
        return jsonify({"status": "success", "message": "Booking saved and emails sent!"}), 200
        
    except Exception as e:
        print(f"SMTP Connection Error: {e}")
        return jsonify({"status": "success", "message": "Booking saved (SMTP connection failed)."}), 200
        
# --- Admin Auth Routes ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session.permanent = True # <--- ADD THIS LINE
            session['admin_logged_in'] = True
            return redirect(url_for('admin'))
        else:
            return render_template('login.html', error="Invalid username or password.")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('login'))

# --- Main Admin Dashboard ---
@app.route('/admin')
def admin():
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    # dictionary=True acts like sqlite3.Row, allowing column name access in HTML
    c = conn.cursor(dictionary=True) 
    c.execute("SELECT * FROM bookings WHERE status NOT IN ('Deleted', 'Archived') ORDER BY timestamp DESC")
    bookings = c.fetchall()
    conn.close()
    
    columns = {'Pending': [], 'In Progress': [], 'Done': []}
    
    for b in bookings:
        # Convert MySQL datetime object to string for the frontend slicing ([:16])
        b['timestamp'] = str(b['timestamp'])
        status = b['status'] if b['status'] in columns else 'Pending'
        columns[status].append(b)
    
    return render_template('admin.html', columns=columns)

@app.route('/update-status/<int:id>', methods=['POST'])
def update_status(id):
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    new_status = request.json.get('status')
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("UPDATE bookings SET status = %s WHERE id = %s", (new_status, id))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

# --- Soft Delete (Move to Trash) ---
@app.route('/delete-booking/<int:id>', methods=['DELETE'])
def delete_booking(id):
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("UPDATE bookings SET status = 'Deleted' WHERE id = %s", (id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

# --- Trash & Recovery Routes ---
@app.route('/admin/trash')
def trash():
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    c = conn.cursor(dictionary=True)
    c.execute("SELECT * FROM bookings WHERE status = 'Deleted' ORDER BY timestamp DESC")
    deleted_bookings = c.fetchall()
    conn.close()

    for b in deleted_bookings:
        b['timestamp'] = str(b['timestamp'])
    
    return render_template('trash.html', bookings=deleted_bookings)

@app.route('/recover-booking/<int:id>', methods=['POST'])
def recover_booking(id):
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("UPDATE bookings SET status = 'Pending' WHERE id = %s", (id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/hard-delete-booking/<int:id>', methods=['DELETE'])
def hard_delete_booking(id):
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("DELETE FROM bookings WHERE id = %s", (id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

# --- Archive Routes ---
@app.route('/admin/archive')
def archive():
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    c = conn.cursor(dictionary=True)
    c.execute("SELECT * FROM bookings WHERE status = 'Archived' ORDER BY timestamp DESC")
    archived_bookings = c.fetchall()
    conn.close()

    for b in archived_bookings:
        b['timestamp'] = str(b['timestamp'])
    
    return render_template('archive.html', bookings=archived_bookings)

@app.route('/archive-booking/<int:id>', methods=['POST'])
def archive_booking(id):
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("UPDATE bookings SET status = 'Archived' WHERE id = %s", (id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/unarchive-booking/<int:id>', methods=['POST'])
def unarchive_booking(id):
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = get_db_connection()
    c = conn.cursor()
    # Sends it back to the "Done" column on the main board
    c.execute("UPDATE bookings SET status = 'Done' WHERE id = %s", (id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/export-archive')
def export_archive():
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    c = conn.cursor(dictionary=True)
    # Select only the relevant data to export
    c.execute("SELECT name, email, project_type, budget, message, timestamp FROM bookings WHERE status = 'Archived' ORDER BY timestamp DESC")
    archived_bookings = c.fetchall()
    conn.close()

    # Create a virtual file in the server's memory
    si = StringIO()
    cw = csv.writer(si)
    
    # Write the Excel Header Row
    cw.writerow(['Client Name', 'Email', 'Project Type', 'Budget', 'Client Message', 'Date Booked'])
    
    # Write all the archived data rows
    for b in archived_bookings:
        cw.writerow([b['name'], b['email'], b['project_type'], b['budget'], b['message'], b['timestamp']])
    
    output = si.getvalue()
    
    # Send the file to the browser as a downloadable CSV
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=archived_projects.csv"}
    )

if __name__ == '__main__':
    app.run(debug=True, port=5000)