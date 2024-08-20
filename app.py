from flask import Flask, request, jsonify
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import mimetypes
from flask_cors import CORS
from flask import url_for
import json
from datetime import datetime, timedelta
import os

APPLICATIONS_FILE = 'applications.json'

def get_current_time():
    return datetime.now().isoformat()

def save_applications():
    with open(APPLICATIONS_FILE, 'w') as f:
        json.dump(applications, f)

def load_applications():
    global applications
    if os.path.exists(APPLICATIONS_FILE):
        with open(APPLICATIONS_FILE, 'r') as f:
            applications = json.load(f)

def is_application_expired(timestamp, hours=48):
    application_time = datetime.fromisoformat(timestamp)
    return datetime.now() - application_time > timedelta(hours=hours)

def add_application(app_id, pg_details, user_details):
    timestamp = get_current_time()
    applications[app_id] = {
        'pg_details': pg_details,
        'user_details': user_details,
        'timestamp': timestamp,
        'status': 'pending'
    }
    save_applications()

def is_application_expired(timestamp, hours=48):
    try:
        application_time = datetime.fromisoformat(timestamp)
    except ValueError:
        return True  

    return datetime.now() - application_time > timedelta(hours=hours)

app = Flask(__name__)
CORS(app)

SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USER = 'mypghelp@gmail.com'
SMTP_PASSWORD = 'obnp zraz uqcq jbuo'
SENDER_EMAIL = 'mypghelp@gmail.com'
ADMIN_EMAIL = 'mypghelp@gmail.com' 

otp_storage = {}

@app.route('/send-otp', methods=['POST'])
def send_otp():
    data = request.get_json()
    email = data.get('email')
    name = data.get('name')
    phone = data.get('phone')

    if not email or not name or not phone:
        return jsonify({'success': False, 'message': 'Missing required fields'})

    otp = str(random.randint(100000, 999999))  

    otp_storage[email] = {'otp': otp, 'name': name, 'phone': phone}
    
    subject = 'Your OTP Code'
    body = f"Hi {name},\n\nYour OTP code is {otp}.\n\n" + \
       "Visit here: https://mypgspace.netlify.app/\n\n" + \
       "We would appreciate your feedback. Please provide it here: https://mypgspace.netlify.app/feedback\n\n" + \
       "Please make sure to read our terms and conditions here: https://mypgspace.netlify.app/terms\n\n" + \
       "Best regards,\nMY PG 🏠 Team"

    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = SENDER_EMAIL
        msg['To'] = email

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SENDER_EMAIL, email, msg.as_string())

        return jsonify({'success': True})
    except Exception as e:
        print(e)
        return jsonify({'success': False, 'message': 'Failed to send OTP'})

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    otp = data.get('otp')

    user_data = otp_storage.get(email)

    if user_data and otp == user_data['otp']:
        name = user_data['name']
        phone = user_data['phone']

        subject_user = 'Login Successful'
        body_user = f"Hi {name},\n\nYou have successfully logged in.\n\nDetails:\nName: {name}\nEmail: {email}\nPhone: {phone}\n\n" + \
                    "Now, hurry up and apply for PG with an 80% discount! Visit here: https://mypgspace.netlify.app/\n\n" + \
                    "We would appreciate your feedback. Please provide it here: https://mypgspace.netlify.app/feedback\n\n" + \
                    "Visit here: https://mypgspace.netlify.app/\n\n" + \
                    "Please make sure to read our terms and conditions here: https://mypgspace.netlify.app/terms\n\n" + \
                    "Best regards,\nMY PG 🏠 Team"
        
        try:
            msg_user = MIMEText(body_user)
            msg_user['Subject'] = subject_user
            msg_user['From'] = SENDER_EMAIL
            msg_user['To'] = email

            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.sendmail(SENDER_EMAIL, email, msg_user.as_string())
        except Exception as e:
            print(e)
            return jsonify({'success': False, 'message': 'Failed to send user confirmation email'})

        subject_admin = 'User Logged In'
        body_admin = f'Hi Admin,\n\nA user has successfully logged in.\n\nDetails:\nName: {name}\nEmail: {email}\nPhone: {phone}\n\nBest regards,\nMY PG 🏠 Team'
        
        try:
            msg_admin = MIMEText(body_admin)
            msg_admin['Subject'] = subject_admin
            msg_admin['From'] = SENDER_EMAIL
            msg_admin['To'] = ADMIN_EMAIL

            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.sendmail(SENDER_EMAIL, ADMIN_EMAIL, msg_admin.as_string())
        except Exception as e:
            print(e)
            return jsonify({'success': False, 'message': 'Failed to send admin notification email'})

        otp_storage.pop(email, None)

        return jsonify({'success': True, 'message': 'Login successful'})
    else:
        return jsonify({'success': False, 'message': 'Invalid OTP'})
    
def send_email(to_email, subject, body, attachments=None, html_body=None):
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = SENDER_EMAIL
    msg['To'] = to_email

    if html_body:
        msg.attach(MIMEText(html_body, 'html'))
    else:
        msg.attach(MIMEText(body, 'plain'))

    if attachments:
        for filename, file_data in attachments.items():
            mime_type, _ = mimetypes.guess_type(filename)
            if mime_type is None:
                mime_type = 'application/octet-stream'
            maintype, subtype = mime_type.split('/', 1)

            part = MIMEBase(maintype, subtype)
            part.set_payload(file_data.read())
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename="{filename}"',
            )
            msg.attach(part)

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SENDER_EMAIL, to_email, msg.as_string())
    except Exception as e:
        print(e)
        return False
    return True

applications = {}

@app.route('/apply', methods=['POST'])
def apply():
    data = request.form
    user_email = data.get('userEmail')
    pg_email = data.get('pgEmail')
    admin_email = ADMIN_EMAIL

    pg_details = {
        'PG Name': data.get('pgName'),
        'City': data.get('city'),
        'Area': data.get('area'),
        'Room Type': data.get('roomType'),
        'Food': data.get('food'),
        'Room Size': data.get('roomSize'),
        'Price per Month': data.get('pgPrice'),
        'Address': data.get('address'),
        'Facilities': data.get('facilities'),
        'Rules': data.get('rules'),
        'State': data.get('state'),
        'Country': data.get('country'),
        'PG Phone': data.get('pgPhone'),
        'PG Email': data.get('pgEmail')
    }

    user_details = {
        'Name': data.get('userName'),
        'Phone': data.get('userPhone'),
        'Email': data.get('userEmail'),
        'Duration': data.get('duration'),
    }

    url = f"mypgspace.netlify.app/display.html?pgName={pg_details['PG Name']}&country={pg_details['Country']}&state={pg_details['State']}&city={pg_details['City']}&area={pg_details['Area']}&roomType={pg_details['Room Type']}&food={pg_details['Food']}&roomSize={pg_details['Room Size']}&pgPrice={pg_details['Price per Month']}&address={pg_details['Address']}&facilities={pg_details['Facilities']}&rules={pg_details['Rules']}&pgPhone={pg_details['PG Phone']}&pgEmail={pg_details['PG Email']}&userName={user_details['Name']}&userPhone={user_details['Phone']}&userEmail={user_details['Email']}&duration={user_details['Duration']}"

    application_id = str(len(applications) + 1) 
    applications[application_id] = {
        'pg_details': pg_details,
        'user_details': user_details,
        'status': 'pending'
    }

    body_user = f"Hi {user_details['Name']},\n\nYour application has been received.\n\nPG Details:\n" + \
            '\n'.join([f"{key}: {value}" for key, value in pg_details.items() if key not in ['PG Phone', 'PG Email']]) + \
            "\n\nUser Details:\n" + \
            '\n'.join([f"{key}: {value}" for key, value in user_details.items() if key not in ['Phone', 'Email']]) + \
            "\n\nNow, you will need to wait up to 48 hours for approval, but you should receive it soon.\n\n" + \
                    "We would appreciate your feedback. Please provide it here: https://mypgspace.netlify.app/feedback\n\n" + \
                    "Visit here: https://mypgspace.netlify.app/\n\n" + \
                    "Please make sure to read our terms and conditions here: https://mypgspace.netlify.app/terms\n\n" + \
                    "Best regards,\nMY PG 🏠 Team"

    body_pg = f"Hi PG Owner,\n\nA new application has been received.\n\nPG Details:\n" + \
              '\n'.join([f"{key}: {value}" for key, value in pg_details.items()]) + \
              "\n\nUser Details:\n" + \
              '\n'.join([f"{key}: {value}" for key, value in user_details.items() if key not in ['Phone', 'Email']]) + \
            "\n\nBest regards,\nMY PG 🏠 Team"

    body_admin = f"Hi Admin,\n\nA new application has been received.\n\nPG Details:\n" + \
                 '\n'.join([f"{key}: {value}" for key, value in pg_details.items()]) + \
                 "\n\nUser Details:\n" + \
                 '\n'.join([f"{key}: {value}" for key, value in user_details.items()])

    send_email(user_email, 'Application Confirmation', body_user)
    
    confirm_url = url_for('confirm_application', app_id=application_id, _external=True)
    reject_url = url_for('reject_application', app_id=application_id, _external=True)
    
    html_body_pg = f"""
<html>
<body>
    <p>Hi PG Owner,</p>
    <p>A new application has been received.</p>
    <p>PG Details:</p>
    <ul>
        {''.join([f'<li>{key}: {value}</li>' for key, value in pg_details.items()])}
    </ul>
    <p>User Details:</p>
    <ul>
        {''.join([f'<li>{key}: {value}</li>' for key, value in user_details.items() if key not in ['Phone', 'Email']])}
    </ul>

    <p>Please confirm or reject the application:</p>
    <p>Please <a href="{url}">click here</a> to view the full details. After reviewing, please confirm or reject your decision.</p>
    <a href="{confirm_url}">Confirm</a> | <a href="{reject_url}">Reject</a>
    <p>We would appreciate your feedback. Please provide it here: <a href="https://mypgspace.netlify.app/feedback">Feedback</a></p>
    <p>Visit here: <a href="https://mypgspace.netlify.app/">MY PG 🏠</a></p>
    <p>Please make sure to read our terms and conditions here: <a href="https://mypgspace.netlify.app/terms">Terms and Conditions</a></p>
    <p>Best regards,<br>MY PG 🏠 Team</p>
</body>
</html>
"""

    attachments = {}
    for file_key in ['userPhoto', 'adharCard', 'studentId', 'otherDoc']:
        if file_key in request.files:
            file = request.files[file_key]
            if file and file.filename:
                attachments[file.filename] = file
    
    send_email(pg_email, 'New Application Received', body_pg, attachments, html_body=html_body_pg)
    send_email(admin_email, 'New Application Received', body_admin, attachments)

    return jsonify({'success': True, 'message': 'Application submitted successfully'})

@app.route('/confirm_application', methods=['GET'])
def confirm_application():
    app_id = request.args.get('app_id')
    application = applications.get(app_id)

    if not application:
        return "Application not found!", 404
    
    if 'timestamp' not in application:
        application['timestamp'] = get_current_time()
        save_applications()
    
    print(f"Application Data: {application}")

    if is_application_expired(application['timestamp']):
        return "Application confirmation window has expired.", 400

    pg_details = application['pg_details']
    user_details = application['user_details']

    application['status'] = 'confirmed'
    save_applications()

    user_subject = 'PG Application Status'
    user_body = f"Hi {user_details['Name']},\n\nCongratulations! Your application has been approved.\n\nPG Details:\n" + \
            '\n'.join([f"{key}: {value}" for key, value in pg_details.items()]) + \
            "\n\nYour details are:\n" + \
            '\n'.join([f"{key}: {value}" for key, value in user_details.items()]) + \
            "\n\nYou have been allocated a PG. You can now move in by visiting the address provided. The contact details of the PG are also given; please reach out to them if needed.\n\n" + \
            "We would love to hear your feedback. Please provide it here: https://mypgspace.netlify.app/feedback\n\n" + \
            "\n\nVisit here: https://mypgspace.netlify.app/" + \
            "\n\nPlease make sure to read our terms and conditions here: https://mypgspace.netlify.app/terms" + \
            "\n\nBest regards,\nMY PG 🏠 Team"

    send_email(user_details['Email'], user_subject, user_body)

    owner_subject = 'PG Application Status'
    owner_body = f"Hi,\n\nThe application for the following user has been confirmed:\n\n" + \
             "User Details:\n" + '\n'.join([f"{key}: {value}" for key, value in user_details.items()]) + \
             "\n\nPG Details:\n" + '\n'.join([f"{key}: {value}" for key, value in pg_details.items()]) + \
             "\n\nThe user has thanked you for this and will be contacting you soon. If you'd like, you can also reach out to the user using the provided contact details." + \
             "\n\nWe would love to hear your feedback. Please provide it here: https://mypgspace.netlify.app/feedback" + \
             "\n\nVisit here: https://mypgspace.netlify.app/" + \
             "\n\nPlease make sure to read our terms and conditions here: https://mypgspace.netlify.app/terms" + \
             "\n\nBest regards,\nMY PG 🏠 Team"

    admin_subject = 'PG Application Status'
    admin_body = f"Hi Admin,\n\nThe application for the following user has been confirmed:\n\n" + \
                 "User Details:\n" + '\n'.join([f"{key}: {value}" for key, value in user_details.items()]) + \
                 "\n\nPG Details:\n" + '\n'.join([f"{key}: {value}" for key, value in pg_details.items()]) + \
                 "\n\nBest regards,\nMY PG 🏠 Team"

    send_email(pg_details['PG Email'], owner_subject, owner_body)
    send_email(ADMIN_EMAIL, admin_subject, admin_body)

    return "Application confirmed!"

@app.route('/reject_application', methods=['GET'])
def reject_application():
    app_id = request.args.get('app_id')
    application = applications.get(app_id)

    if not application:
        return "Application not found!", 404
    
    if 'timestamp' not in application:
        application['timestamp'] = get_current_time()
        save_applications()
    
    print(f"Application Data: {application}")

    if is_application_expired(application['timestamp']):
        return "Application confirmation window has expired.", 400

    pg_details = application['pg_details']
    user_details = application['user_details']

    application['status'] = 'rejected'
    save_applications()

    user_subject = 'PG Application Status'
    user_body = f"Hi {user_details['Name']},\n\nUnfortunately, your application has been rejected.\n\nPG Details:\n" + \
            '\n'.join([f"{key}: {value}" for key, value in pg_details.items()]) + \
            "\n\nYour details were:\n" + \
            '\n'.join([f"{key}: {value}" for key, value in user_details.items()]) + \
            "\n\nWe're sorry, but there is no availability in our PG at the moment, which is why your application couldn't be accepted. However, you can apply to another PG.\n\n" + \
            "We would appreciate your feedback. Please provide it here: https://mypgspace.netlify.app/feedback\n\n" + \
            "Visit here: https://mypgspace.netlify.app/\n\n" + \
            "Please make sure to read our terms and conditions here: https://mypgspace.netlify.app/terms\n\n" + \
            "Best regards,\nMY PG 🏠 Team"

    send_email(user_details['Email'], user_subject, user_body)

    owner_subject = 'PG Application Status'
    owner_body = f"Hi,\n\nThe application for the following user has been rejected:\n\n" + \
             "User Details:\n" + '\n'.join([f"{key}: {value}" for key, value in user_details.items()]) + \
             "\n\nPG Details:\n" + '\n'.join([f"{key}: {value}" for key, value in pg_details.items()]) + \
             "\n\nWe understand that you may have rejected the application due to a lack of availability. When you have availability in the future, you can inform us via email at mypghelp@gmail.com or directly upload the PG details here: https://mypgspace.netlify.app/pg-details-upload.\n\n" + \
             "We would appreciate your feedback. Please provide it here: https://mypgspace.netlify.app/feedback\n\n" + \
             "Visit here: https://mypgspace.netlify.app/\n\n" + \
             "Please make sure to read our terms and conditions here: https://mypgspace.netlify.app/terms\n\n" + \
             "Best regards,\nMY PG 🏠 Team"

    admin_subject = 'PG Application Status'
    admin_body = f"Hi Admin,\n\nThe application for the following user has been rejected:\n\n" + \
                 "User Details:\n" + '\n'.join([f"{key}: {value}" for key, value in user_details.items()]) + \
                 "\n\nPG Details:\n" + '\n'.join([f"{key}: {value}" for key, value in pg_details.items()]) + \
                 "Best regards,\nMY PG 🏠 Team"

    send_email(pg_details['PG Email'], owner_subject, owner_body)
    send_email(ADMIN_EMAIL, admin_subject, admin_body)

    return "Application rejected!"

@app.route('/view_application/<app_id>', methods=['GET'])
def view_application(app_id):
    application = applications.get(app_id)

    if not application:
        return "Application not found!", 404

    pg_details = application['pg_details']
    user_details = application['user_details']

    return render_template('confirm_reject.html', 
                           app_id=app_id,
                           pg_details=pg_details, 
                           user_details=user_details)

@app.route('/upload-pg-details', methods=['POST'])
def upload_pg_details():
    pg_email = request.form.get('ownerEmail')
    admin_email = ADMIN_EMAIL 

    pg_details = {
        'PG Name': request.form.get('pgName'),
        'Country': request.form.get('country'),
        'State': request.form.get('state'),
        'City': request.form.get('city'),
        'Area': request.form.get('area'),
        'Room Type': request.form.get('roomType'),
        'Food': request.form.get('food'),
        'Room Size': request.form.get('size'),
        'Price': request.form.get('currentPrice'),
        'Address': request.form.get('address'),
        'Facilities': request.form.get('facilities'),
        'Rules': request.form.get('rules'),
        'Available Seats': request.form.get('availableSeats'),
    }

    user_details = {
        'Name': request.form.get('ownerName'),
        'Phone': request.form.get('ownerPhone'),
        'Email': request.form.get('ownerEmail'),
    }

    body_pg_owner = f"Hi {user_details['Name']},\n\nThank you for submitting the details of your PG.\n\n" + \
                "We have received the following details:\n\nPG Details:\n" + \
                '\n'.join([f"{key}: {value}" for key, value in pg_details.items()]) + \
                "\n\nYour Details:\n" + \
                '\n'.join([f"{key}: {value}" for key, value in user_details.items()]) + \
                "\n\nIf a user applies for your PG, we will notify you via email. Please make sure to confirm the application promptly.\n\n" + \
                "We would appreciate your feedback. Please provide it here: https://mypgspace.netlify.app/feedback\n\n" + \
                "Visit here: https://mypgspace.netlify.app/\n\n" + \
                "Please make sure to read our terms and conditions here: https://mypgspace.netlify.app/terms\n\n" + \
                "Best regards,\nMY PG 🏠 Team"

    body_admin = f"Hi Admin,\n\nA new application has been received.\n\nPG Details:\n" + \
                 '\n'.join([f"{key}: {value}" for key, value in pg_details.items()]) + \
                 "\n\nUser Details:\n" + \
                 '\n'.join([f"{key}: {value}" for key, value in user_details.items()]) + \
                "Best regards,\nMY PG 🏠 Team"

    attachments = {}
    for file_key in ['images']:  
        if file_key in request.files:
            files = request.files.getlist(file_key)
            for file in files:
                if file and file.filename:
                    attachments[file.filename] = file

    send_email(pg_email, 'PG Details Confirmation', body_pg_owner)

    send_email(admin_email, 'New Application Received', body_admin, attachments)

    return jsonify({'success': True, 'message': 'PG details submitted successfully'})

@app.route('/pg-accommodation-request', methods=['POST'])
def pg_accommodation_request():
    email = request.form.get('Email')
    admin_email = ADMIN_EMAIL  

    details = {
        'Name': request.form.get('Name'),
        'Country': request.form.get('country'),
        'State': request.form.get('state'),
        'City': request.form.get('city'),
        'Area': request.form.get('area'),
        'Room Type': request.form.get('roomType'),
        'Food': request.form.get('food'),
        'Room Size': request.form.get('size'),
    }

    user_details = {
        'Name': request.form.get('Name'),
        'Phone': request.form.get('Phone'),
        'Email': request.form.get('Email'),
    }

    body_user_owner = f"Hi {user_details['Name']},\n\nThank you for submitting the request. When a PG becomes available, we will inform you.\n\n" + \
                    "We have received the following details:\n\nDetails:\n" + \
                    '\n'.join([f"{key}: {value}" for key, value in details.items()]) + \
                    "\n\nYour Details:\n" + \
                    '\n'.join([f"{key}: {value}" for key, value in user_details.items()]) + \
                    "\n\nWe will certainly contact you if we find a suitable PG based on your request. We apologize for the current lack of availability.\n\n" + \
                    "We would appreciate your feedback. Please provide it here: https://mypgspace.netlify.app/feedback\n\n" + \
                    "Visit here: https://mypgspace.netlify.app/\n\n" + \
                    "Please make sure to read our terms and conditions here: https://mypgspace.netlify.app/terms\n\n" + \
                    "Best regards,\nMY PG 🏠 Team"

    body_admin = f"Hi Admin,\n\nA new PG request has been received.\n\nDetails:\n" + \
                 '\n'.join([f"{key}: {value}" for key, value in details.items()]) + \
                 "\n\nUser Details:\n" + \
                 '\n'.join([f"{key}: {value}" for key, value in user_details.items()]) + \
                "Best regards,\nMY PG 🏠 Team"

    send_email(email, 'Details Confirmation', body_user_owner)

    send_email(admin_email, 'New Application Received', body_admin)

    return jsonify({'success': True, 'message': 'Your details submitted successfully'})

@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    email = request.form.get('email')
    message = request.form.get('message')
    rating = request.form.get('rating')

    if not email or not message or not rating:
        return jsonify({'success': False, 'message': 'Missing required fields'})

    subject_user = 'Thank You for Your Feedback'
    body_user = f"Hi,\n\nThank you for your feedback!\n\nMessage: {message}\nRating: {rating}\n\nWe appreciate your input.\n\n" + \
            "Visit here: https://mypgspace.netlify.app/\n\n" + \
            "Please make sure to read our terms and conditions here: https://mypgspace.netlify.app/terms\n\n" + \
            "Best regards,\nMY PG 🏠 Team"

    subject_admin = 'New Feedback Received'
    body_admin = f"A new feedback has been received.\n\nUser Email: {email}\nMessage: {message}\nRating: {rating}\n\nBest regards,\nMY PG 🏠 Team"

    send_email(email, subject_user, body_user)

    send_email(ADMIN_EMAIL, subject_admin, body_admin)

    return jsonify({'success': True, 'message': 'Feedback submitted successfully'})

@app.route('/submit_query', methods=['POST'])
def submit_query():
    email = request.form.get('email')
    message = request.form.get('message')

    if not email or not message:
        return jsonify({'success': False, 'message': 'Missing required fields'})

    subject_user = 'Thank You for Your query'
    body_user = f"Hi,\n\nThank you for your query!\n\nMessage: {message}\n\nWe appreciate your input.\n\n" + \
             "We would appreciate your feedback. Please provide it here: https://mypgspace.netlify.app/feedback\n\n" + \
            "Visit here: https://mypgspace.netlify.app/\n\n" + \
            "Please make sure to read our terms and conditions here: https://mypgspace.netlify.app/terms\n\n" + \
            "Best regards,\nMY PG 🏠 Team"

    subject_admin = 'New query Received'
    body_admin = f"A new query has been received.\n\nUser Email: {email}\nMessage: {message}\n\nBest regards,\nMY PG 🏠 Team"

    send_email(email, subject_user, body_user)

    send_email(ADMIN_EMAIL, subject_admin, body_admin)

    return jsonify({'success': True, 'message': 'Query submitted successfully'})

if __name__ == '__main__':
    load_applications()
    app.run(debug=True)
