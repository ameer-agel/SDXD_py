from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import pymysql
import jwt
import os
import datetime
from datetime import date, time, timedelta
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from gradio_client import Client, handle_file
import json

app = Flask(__name__, template_folder='templates')
CORS(app)

app.config['SECRET_KEY'] = 'SDXD_SUPER_SECRET_KEY_2026'
UPLOAD_FOLDER = "upload"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Monkey-patch gradio_client to support Gradio 5+ space info routing and JSON Schema boolean types
import gradio_client
import gradio_client.client
import gradio_client.utils

gradio_client.utils.RAW_API_INFO_URL = "gradio_api/info?serialize=False"
if hasattr(gradio_client.client, "utils"):
    gradio_client.client.utils.RAW_API_INFO_URL = "gradio_api/info?serialize=False"

_orig_schema_to_type = gradio_client.utils._json_schema_to_python_type
gradio_client.utils._json_schema_to_python_type = lambda s, d: "Any" if isinstance(s, bool) else _orig_schema_to_type(s, d)

HF_SPACE = "samarfuoad/modelProject"
print("DEBUG: RAW_API_INFO_URL in utils:", gradio_client.utils.RAW_API_INFO_URL)
try:
    hf_client = Client(HF_SPACE)
except Exception as e:
    print("DEBUG: Client initialization failed!")
    print("DEBUG: Exception:", e)
    print("DEBUG: RAW_API_INFO_URL on failure:", gradio_client.utils.RAW_API_INFO_URL)
    import httpx
    try:
        r = httpx.get("https://samarfuoad-modelproject.hf.space/gradio_api/info?serialize=False")
        print("DEBUG: Direct httpx fetch status:", r.status_code)
        print("DEBUG: Direct httpx fetch text:", r.text[:500])
    except Exception as fetch_err:
        print("DEBUG: Direct httpx fetch failed:", fetch_err)
    raise e

# ************************************************************
# دالة الاتصال بقاعدة البيانات
# ************************************************************
from db_configuration import get_db_connection

# ************************************************************
# دالة استخراج idDoctor من التوكن
# ************************************************************
def get_doctor_id_from_token():
    auth = request.headers.get('Authorization', '')
    if not auth:
        return None
    try:
        token = auth.replace('Bearer ', '').strip()
        decoded = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return decoded.get('user_id')
    except Exception as e:
        print("JWT ERROR:", e)
        return None

# ************************************************************
# دالة استخراج PatientId من التوكن (فقط لو role=patient)
# ************************************************************
def get_patient_id_from_token():
    auth = request.headers.get('Authorization', '')
    if not auth:
        return None
    try:
        token = auth.replace('Bearer ', '').strip()
        decoded = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        if decoded.get('role') != 'patient':
            return None
        return decoded.get('user_id')
    except Exception as e:
        print("JWT ERROR:", e)
        return None

# ************************************************************
# دالة تحويل PatientId (نصي) إلى patient_id (رقمي) من الداتابيز
# ************************************************************
def get_patient_internal_id():
    patient_identity = get_patient_id_from_token()
    if not patient_identity:
        return None
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT patient_id FROM patients WHERE PatientId=%s", (patient_identity,))
        result = cursor.fetchone()
        return result["patient_id"] if result else None
    finally:
        cursor.close(); conn.close()

# ************************************************************
# دالة تحويل حقول التاريخ/الوقت إلى نصوص قابلة للإرسال كـ JSON
# ************************************************************
def serialize_row(row):
    if not row:
        return None
    for k, v in row.items():
        if isinstance(v, datetime.datetime):
            row[k] = v.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(v, datetime.date):
            row[k] = v.strftime("%Y-%m-%d")
        elif isinstance(v, datetime.time):
            row[k] = v.strftime("%H:%M:%S")
        elif hasattr(v, "total_seconds"):
            ts = int(v.total_seconds())
            row[k] = f"{ts//3600:02d}:{(ts%3600)//60:02d}:{ts%60:02d}"
    return row

# ************************************************************
# صفحة تسجيل الدخول (الصفحة الرئيسية)
# ************************************************************
@app.route('/')
@app.route('/loginpat.html')
def login_page():           return render_template('loginpat.html')

# ************************************************************
# صفحة الطبيب الرئيسية
# ************************************************************
@app.route('/sreaj.html')
def doctor_dashboard():     return render_template('sreaj.html')

# ************************************************************
# صفحة إنشاء فحص جديد
# ************************************************************
@app.route('/newscan.html')
def new_scan_page():         return render_template('newscan.html')

# ************************************************************
# صفحة عرض نتيجة الذكاء الاصطناعي
# ************************************************************
@app.route('/views.html')
def views_page():            return render_template('views.html')

# ************************************************************
# صفحة سجلات المرضى
# ************************************************************
@app.route('/dashboard.html')
def dashboard_records_page():return render_template('dashboard.html')

# ************************************************************
# صفحة عرض تفاصيل فحص واحد
# ************************************************************
@app.route('/view.html')
def view_page():             return render_template('view.html')

# ************************************************************
# صفحة التحليلات
# ************************************************************
@app.route('/myanalysis.html')
def analysis_page():         return render_template('myanalysis.html')

# ************************************************************
# صفحة الحساب
# ************************************************************
@app.route('/account.html')
def account_page():          return render_template('account.html')

# ************************************************************
# صفحة لوحة تحكم المريض
# ************************************************************
@app.route('/patient-dashboard.html')
def patient_dashboard():     return render_template('patient-dashboard.html')

# ************************************************************
# صفحة فحوصات المريض
# ************************************************************
@app.route('/my-scans.html')
def myscans():               return render_template('my-scans.html')

# ************************************************************
# صفحة المواعيد
# ************************************************************
@app.route('/appointments.html')
def appointments_page():     return render_template('appointments.html')

# ************************************************************
# صفحة المساعدة الخاصة بالمريض
# ************************************************************
@app.route('/help_pat.html')
def help_pat():              return render_template('help_pat.html')

# ************************************************************
# صفحة المساعدة الخاصة بالطبيب
# ************************************************************
@app.route('/help.html')
def help_page():             return render_template('help.html')

# ************************************************************
# صفحة مساعدة نسيان بيانات الدخول
# ************************************************************
@app.route('/helpLog.html')
def helpLog_page():             return render_template('helpLog.html')

# ************************************************************
# دالة تقديم صور الأشعة المرفوعة من مجلد uploads
# ************************************************************
@app.route('/upload/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

# ************************************************************
# دالة تسجيل الدخول (مريض / طبيب / مدير)
# ************************************************************
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or 'loginId' not in data or 'password' not in data:
        return jsonify({"success": False, "message": "بيانات الدخول غير مكتملة"}), 400

    login_id = str(data['loginId']).strip()
    password = str(data['password']).strip()

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM patients WHERE PatientId = %s", (login_id,))
        patient = cursor.fetchone()

        if patient:
            stored = patient.get('password_hash') or ''
            password_ok = False
            if stored.startswith('scrypt:') or stored.startswith('pbkdf2:'):
                from werkzeug.security import check_password_hash
                try:
                    password_ok = check_password_hash(stored, password)
                except Exception:
                    password_ok = False
            else:
                password_ok = (stored == password)

            if password_ok:
                token = jwt.encode({
                    'user_id': patient['PatientId'],
                    'role': 'patient',
                    'name': patient.get('full_name', ''),
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)
                }, app.config['SECRET_KEY'], algorithm='HS256')
                return jsonify({
                    "success": True, "role": "patient",
                    "token": token,
                    "name": patient.get('full_name', ''),
                    "message": "تم تسجيل الدخول بنجاح"
                })
            else:
                return jsonify({"success": False, "message": "كلمة المرور أو بيانات الدخول خاطئة"}), 401
        

        doctor_id_part = login_id[1:]
        cursor.execute("SELECT * FROM doctors WHERE idDoctor = %s AND password_hash = %s",(doctor_id_part, password))
        doctor = cursor.fetchone()

        if doctor:
            expected = doctor['first_name'].strip()[0].lower() + str(doctor['idDoctor'])
            if login_id.lower() == expected.lower():
                token = jwt.encode({
                    'user_id':  doctor['idDoctor'],
                    'role':     'doctor',
                    'name':     f"{doctor['first_name'].strip()} {doctor['last_name']}",
                    'exp':      datetime.datetime.utcnow() + datetime.timedelta(days=7)
                }, app.config['SECRET_KEY'], algorithm='HS256')
                return jsonify({
                    "success": True, "role": "doctor",
                    "token": token,
                    "name": f"{doctor['first_name'].strip()} {doctor['last_name']}",
                    "message": "تم تسجيل الدخول بنجاح"
                })
        cursor.execute("SELECT * FROM admins WHERE username = %s", (login_id,))
        admin = cursor.fetchone()

        if admin:
            stored = admin['password'] if admin['password'] else ""

            if stored.startswith("scrypt:") or stored.startswith("pbkdf2:"):
               try:
                   password_ok = check_password_hash(stored, password)
               except Exception:
                  password_ok = False
            else:
                password_ok = (stored == password)

            if password_ok:
                token = jwt.encode({
                    'user_id': admin['username'],
                    'role': 'admin',
                    'name': admin.get('full_name', ''),
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)
                }, app.config['SECRET_KEY'], algorithm='HS256')
                return jsonify({
                    "success": True, "role": "admin",
                    "token": token,
                    "name": admin.get('full_name', ''),
                    "message": "تم تسجيل الدخول بنجاح"
                })

        return jsonify({"success": False, "message": "كلمة المرور أو بيانات الدخول خاطئة"}), 401

    except Exception as e:
        return jsonify({"success": False, "message": f"خطأ في الخادم: {str(e)}"}), 500
    finally:
        cursor.close(); conn.close()

# ************************************************************
# دالة جلب بيانات الطبيب الأساسية (الاسم + الصورة)
# ************************************************************
@app.route('/doctor-info')
def doctor_info():
    doctor_id = get_doctor_id_from_token()
    if not doctor_id:
        return jsonify({"success": False}), 401
    conn = get_db_connection(); cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT idDoctor, first_name, last_name, profile_photo FROM doctors WHERE idDoctor=%s",
            (doctor_id,)
        )
        doctor = cursor.fetchone()
        if not doctor:
            return jsonify({"success": False}), 404
        return jsonify({"success": True,
                        "first_name":    doctor["first_name"],
                        "last_name":     doctor["last_name"],
                        "profile_photo": doctor["profile_photo"]})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close(); conn.close()

# ************************************************************
# دالة عرض وتعديل بيانات حساب الطبيب
# ************************************************************
@app.route('/doctor/account', methods=['GET', 'PUT'])
def doctor_account():
    doctor_id = get_doctor_id_from_token()
    if not doctor_id:
        return jsonify({"message": "Unauthorized"}), 401
    conn = get_db_connection(); cursor = conn.cursor()
    try:
        if request.method == 'GET':
            cursor.execute("""
                SELECT first_name, email, clinic_name, specialty,
                       ai_filter, report_language, created_at,
                       license_number, profile_photo
                FROM doctors WHERE idDoctor=%s
            """, (doctor_id,))
            doctor = cursor.fetchone()
            return jsonify(serialize_row(doctor) if doctor else {})

        data = request.json
        cursor.execute("""
            UPDATE doctors
            SET first_name=%s, email=%s, clinic_name=%s,
                specialty=%s, ai_filter=%s, report_language=%s, profile_photo=%s
            WHERE idDoctor=%s
        """, (data["first_name"], data["email"], data["clinic_name"],
              data["specialty"], data["ai_filter"], data["report_language"],
              data["profile_photo"], doctor_id))
        conn.commit()
        return jsonify({"message": "Profile updated successfully"})
    except Exception as e:
        print("Error:", e)
        return jsonify({"message": "Internal Server Error"}), 500
    finally:
        cursor.close(); conn.close()

# ************************************************************
# دالة تغيير كلمة مرور الطبيب
# ************************************************************
@app.route('/doctor/change-password', methods=['PUT'])
def change_doctor_password():
    doctor_id = get_doctor_id_from_token()
    if not doctor_id:
        return jsonify({"message": "Unauthorized"}), 401

    data = request.get_json()
    current_password = data.get("currentPassword")
    new_password = data.get("newPassword")
    if not current_password or not new_password:
        return jsonify({"message": "All fields are required"}), 400

    conn = get_db_connection(); cursor = conn.cursor()
    try:
        cursor.execute("SELECT password_hash FROM doctors WHERE idDoctor=%s", (doctor_id,))
        doctor = cursor.fetchone()
        if not doctor:
            return jsonify({"message": "Doctor not found"}), 404
        if doctor["password_hash"] != current_password:
            return jsonify({"message": "Current password is incorrect"}), 400
        cursor.execute("UPDATE doctors SET password_hash=%s WHERE idDoctor=%s", (new_password, doctor_id))
        conn.commit()
        return jsonify({"message": "Password updated successfully"})
    finally:
        cursor.close(); conn.close()

# ************************************************************
# دالة رفع صورة البروفايل الخاصة بالطبيب
# ************************************************************
@app.route("/doctor/upload-photo", methods=["POST"])
def upload_photo():
    doctor_id = get_doctor_id_from_token()
    if not doctor_id:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    if "file" not in request.files or request.files["file"].filename == "":
        return jsonify({"success": False, "message": "No file sent"}), 400
    file = request.files["file"]
    final_name = f"{doctor_id}_{secure_filename(file.filename)}"
    file.save(os.path.join(app.config["UPLOAD_FOLDER"], final_name))
    return jsonify({"success": True, "filename": final_name, "url": f"/upload/{final_name}"})

# ************************************************************
# دالة إحصائيات لوحة تحكم الطبيب
# ************************************************************
@app.route('/dashboard-stats')
def dashboard_stats():
    doctor_id = get_doctor_id_from_token()
    if not doctor_id:
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    conn = get_db_connection(); cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT
                COUNT(DISTINCT s.scan_id)         AS total_scans,
                COUNT(DISTINCT s.patient_id)       AS active_patients,
                COUNT(DISTINCT CASE WHEN DATE(s.scan_date) = CURDATE() THEN s.scan_id END) AS reports_today,
                COALESCE(ROUND(AVG(a.confidence_score), 1), 0) AS ai_accuracy
            FROM scans s
            LEFT JOIN ai_results a  ON s.scan_id  = a.scan_id
            JOIN      doctors   d   ON d.doctor_id = s.doctor_id
            WHERE d.idDoctor = %s
        """, (doctor_id,))
        stats = cursor.fetchone()
        return jsonify({
            "success":         True,
            "total_scans":     stats["total_scans"]     or 0,
            "active_patients": stats["active_patients"] or 0,
            "reports_today":   stats["reports_today"]   or 0,
            "ai_accuracy":     float(stats["ai_accuracy"] or 0)
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close(); conn.close()

# ************************************************************
# دالة جلب آخر النشاطات (آخر 10 فحوصات) لعرضها في لوحة التحكم
# ************************************************************
@app.route('/recent-activity')
def recent_activity():
    doctor_id = get_doctor_id_from_token()
    if not doctor_id:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    conn = get_db_connection(); cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT scan_id, PatientId, patient_name,
                   diagnosis_label, confidence_score, scan_date
            FROM v_scan_summary
            WHERE doctor_id = (SELECT doctor_id FROM doctors WHERE idDoctor = %s)
            ORDER BY scan_date DESC LIMIT 10
        """, (doctor_id,))
        activities = cursor.fetchall()
        for act in activities:
            if act.get("scan_date"):
                act["scan_date"] = act["scan_date"].strftime("%Y-%m-%d %H:%M")
            if act.get("confidence_score") is not None:
                act["confidence_score"] = float(act["confidence_score"])
        return jsonify({"success": True, "activities": activities})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close(); conn.close()

# ************************************************************
# دالة البحث عن مريض عن طريق رقم الهوية
# ************************************************************
@app.route('/get-patient')
def get_patient():
    search_id = request.args.get('id', '').strip()
    if not search_id:
        return jsonify({"success": False, "message": "المعرف مطلوب"}), 400
    conn = get_db_connection(); cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT patient_id, PatientId, full_name FROM patients WHERE PatientId = %s",
            (search_id,)
        )
        patient = cursor.fetchone()
        if patient:
            return jsonify({"success": True, "patient": {
                "id":    patient["PatientId"],
                "db_id": patient["patient_id"],
                "name":  patient["full_name"]
            }})
        return jsonify({"success": False, "message": "المريض غير موجود"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close(); conn.close()

# ************************************************************



# ************************************************************
# دالة تسجيل مريض جديد بواسطة الطبيب
# ************************************************************
@app.route('/add-patient', methods=['POST'])
def add_patient():
    data = request.json
    if not data:
        return jsonify({"success": False, "message": "لم يتم استقبال بيانات"}), 400

    patient_id  = data.get('patient_id', '').strip()
    full_name   = data.get('full_name', '').strip()
    phone       = data.get('phone', '').strip()
    email       = data.get('email', '').strip()
    dob         = data.get('dob', '') or None

    if not patient_id or not full_name:
        return jsonify({"success": False, "message": "رقم الهوية والاسم حقول مطلوبة"}), 400

    conn = get_db_connection(); cursor = conn.cursor()
    try:
        cursor.execute("SELECT PatientId FROM patients WHERE PatientId = %s", (patient_id,))
        if cursor.fetchone():
            return jsonify({"success": False, "message": "رقم الهوية مسجل مسبقاً"}), 400

        cursor.execute("""
            INSERT INTO patients (PatientId, full_name, phone, emailP, date_of_birth, password_hash)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (patient_id, full_name, phone, email, dob, patient_id))
        conn.commit()
        return jsonify({"success": True, "message": "تم تسجيل المريض بنجاح"})
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close(); conn.close()


# ************************************************************
# دالة إنشاء فحص جديد: رفع صورة + تحليل AI + حفظ بقاعدة البيانات
# ************************************************************
@app.route('/api/new-scan', methods=['POST'])
def new_scan():
    doctor_id = get_doctor_id_from_token()

    if not doctor_id:
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    if 'image' not in request.files:
        return jsonify({"success": False, "message": "لم يتم رفع صورة"}), 400

    file = request.files['image']
    if not file or file.filename == '':
        return jsonify({"success": False, "message": "لم يتم اختيار صورة"}), 400

    patient_db_id = request.form.get('patient_id', '').strip()
    notes = request.form.get('notes', '').strip()

    if not patient_db_id:
        return jsonify({"success": False, "message": "المريض غير محدد"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    save_path = None

    try:
        cursor.execute("SELECT doctor_id FROM doctors WHERE idDoctor = %s", (doctor_id,))
        doctor = cursor.fetchone()
        if not doctor:
            return jsonify({"success": False, "message": "Doctor not found"}), 404

        cursor.execute("SELECT patient_id FROM patients WHERE patient_id = %s", (patient_db_id,))
        patient = cursor.fetchone()
        if not patient:
            return jsonify({"success": False, "message": "Patient not found"}), 404

        filename = secure_filename(file.filename)
        file_extension = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
        
        if file_extension not in {'png', 'jpg', 'jpeg'}:
            return jsonify({"success": False, "message": "نوع الصورة غير مدعوم"}), 400

        unique_name = f"{patient_db_id}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')}_{filename}"
        save_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_name)
        file.save(save_path)

        result = hf_client.predict(handle_file(save_path), api_name="/predict")

        if not isinstance(result, dict):
            raise ValueError("Invalid response received from AI model")
        if result.get("success") is False:
            raise ValueError(result.get("error", "AI model prediction failed"))

        diagnosis_label = result.get("diagnosis")
        confidence = result.get("confidence")
        ai_findings_text = result.get("ai_findings", "")
        all_predictions = result.get("all_predictions", {})

        if diagnosis_label is None or confidence is None:
            raise ValueError("Diagnosis or confidence was not returned by AI model")

        confidence_score = round(float(confidence) * 100, 2)

        ai_findings = {
            "diagnosis": diagnosis_label,
            "confidence": confidence_score,
            "ai_findings": ai_findings_text,
            "class_probabilities": {label: round(float(score) * 100, 2) for label, score in all_predictions.items()}
        }

        findings_json = json.dumps(ai_findings, ensure_ascii=False)

        cursor.execute("""
            INSERT INTO scans (patient_id, doctor_id, image_path, original_name, file_type, scan_date, status, notes, scan_type)
            VALUES (%s, %s, %s, %s, %s, NOW(), %s, %s, %s)
        """, (patient_db_id, doctor['doctor_id'], unique_name, filename, file_extension, 'done', notes, 'Dental X-Ray'))

        scan_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO ai_results (scan_id, diagnosis_label, confidence_score, findings_json, model_version, doctor_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (scan_id, diagnosis_label, confidence_score, findings_json, 'Dental_Xray_Final_Balanced', doctor['doctor_id']))

        cursor.execute("""
            INSERT INTO appointments
                (patient_id, doctor_id, preferred_date, preferred_time,
                 status, treatment_type, patient_notes, appointment_type,
                 created_at, updated_at)
            VALUES
                (%s, %s, CURDATE(), CURTIME(),
                 'completed', %s, %s, 'new_visit',
                 NOW(), NOW())
        """, (patient_db_id, doctor['doctor_id'], diagnosis_label, notes))

        conn.commit()

        return jsonify({
            "success": True,
            "message": "Scan analyzed and saved successfully",
            "scan_id": scan_id,
            "diagnosis_label": diagnosis_label,
            "confidence_score": confidence_score,
            "ai_findings": ai_findings_text,
            "all_predictions": ai_findings["class_probabilities"]
        }), 201

    except Exception as e:
        conn.rollback()
        if save_path and os.path.exists(save_path):
            try: os.remove(save_path)
            except Exception: pass
        
        print("NEW SCAN ERROR:", str(e))
        return jsonify({"success": False, "message": str(e)}), 500

    finally:
        cursor.close()
        conn.close()
        
# ************************************************************
# دالة جلب كل سجلات الفحوصات الخاصة بالطبيب
# ************************************************************
@app.route("/api/get-records")
def get_all_records():
    doctor_id = get_doctor_id_from_token()
    if not doctor_id:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    conn = get_db_connection(); cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT s.scan_id,
                   DATE_FORMAT(s.scan_date,'%%Y-%%m-%%d %%H:%%i') AS scan_date,
                   s.status, s.notes,
                   p.PatientId AS patient_national_id,
                   p.full_name AS patient_name
            FROM scans s
            JOIN patients p ON s.patient_id = p.patient_id
            JOIN doctors  d ON s.doctor_id  = d.doctor_id
            WHERE d.idDoctor = %s
            ORDER BY s.scan_date DESC
        """, (doctor_id,))
        return jsonify({"success": True, "records": cursor.fetchall()})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close(); conn.close()

# ************************************************************
# دالة جلب تفاصيل فحص واحد بالتحديد
# ************************************************************
@app.route('/api/get-scan-details')
def get_scan_details():
    scan_id = request.args.get('scan_id')
    if not scan_id:
        return jsonify({"success": False, "message": "Scan ID required"})
    conn = get_db_connection(); cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT s.scan_id, s.image_path, s.status,
                   DATE_FORMAT(s.scan_date,'%%Y-%%m-%%d %%H:%%i') AS scan_date,
                   s.notes,
                   p.full_name AS patient_name, p.PatientId AS patient_national_id,
                   ai.diagnosis_label, ai.confidence_score,ai.findings_json
            FROM scans s
            JOIN patients p ON s.patient_id = p.patient_id
            LEFT JOIN ai_results ai ON ai.scan_id = s.scan_id
            WHERE s.scan_id = %s
        """, (scan_id,))
        scan = cursor.fetchone()
        if not scan:
            return jsonify({"success": False, "message": "Scan not found"})
        if scan.get("confidence_score"):
            scan["confidence_score"] = float(scan["confidence_score"])
        return jsonify({"success": True, "scan": scan})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close(); conn.close()

# ************************************************************
# دالة تحديث بيانات/ملاحظات فحص موجود
# ************************************************************
@app.route('/api/update-scan', methods=['POST'])
def update_scan():
    data = request.json
    conn = get_db_connection(); cursor = conn.cursor()
    try:
        scan_id = data["scan_id"]
        cursor.execute("SELECT patient_id FROM scans WHERE scan_id=%s", (scan_id,))
        patient = cursor.fetchone()
        if not patient:
            return jsonify({"success": False, "message": "Scan not found"})
        cursor.execute(
            "UPDATE patients SET full_name=%s, PatientId=%s WHERE patient_id=%s",
            (data["patient_name"], data["patient_national_id"], patient["patient_id"])
        )
        cursor.execute("UPDATE scans SET notes=%s WHERE scan_id=%s", (data["doctor_notes"], scan_id))
        conn.commit()
        return jsonify({"success": True})
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close(); conn.close()

# ************************************************************
# دالة إحصائيات صفحة التحليلات (myanalysis.html)
# ************************************************************
@app.route("/myanalysis-stats")
def myanalysis_stats():
    doctor_identity = get_doctor_id_from_token()
    if not doctor_identity:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    conn = get_db_connection(); cursor = conn.cursor()
    try:
        cursor.execute("SELECT doctor_id FROM doctors WHERE idDoctor=%s", (doctor_identity,))
        doctor = cursor.fetchone()
        if not doctor:
            return jsonify({"success": False, "message": "Doctor not found"}), 404
        doctor_id = doctor["doctor_id"]
        cursor.execute("""
            SELECT COUNT(DISTINCT s.scan_id)    AS total_scans,
                   COUNT(DISTINCT s.patient_id) AS active_patients,
                   SUM(CASE WHEN a.diagnosis_label LIKE 'Caries%%' THEN 1 ELSE 0 END) AS caries_count,
                   COALESCE(ROUND(AVG(a.confidence_score),1), 0) AS ai_accuracy
            FROM scans s
            LEFT JOIN ai_results a ON a.scan_id = s.scan_id
            WHERE s.doctor_id=%s
        """, (doctor_id,))
        stats = cursor.fetchone()
        return jsonify({"success": True,
                        "total_scans":     stats["total_scans"]     or 0,
                        "active_patients": stats["active_patients"] or 0,
                        "caries_count":    stats["caries_count"]    or 0,
                        "ai_accuracy":     float(stats["ai_accuracy"] or 0)})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close(); conn.close()

# ************************************************************
# دالة توزيع أنواع التشخيص (لرسم بياني في myanalysis.html)
# ************************************************************
@app.route("/api/pathology-distribution")
def pathology_distribution():
    doctor_identity = get_doctor_id_from_token()
    if not doctor_identity:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    conn = get_db_connection(); cursor = conn.cursor()
    try:
        cursor.execute("SELECT doctor_id FROM doctors WHERE idDoctor=%s", (doctor_identity,))
        doctor = cursor.fetchone()
        if not doctor:
            return jsonify({"success": False}), 404
        cursor.execute("""
            SELECT IFNULL(a.diagnosis_label,'Unknown') AS diagnosis_label, COUNT(*) AS count
            FROM scans s
            LEFT JOIN ai_results a ON s.scan_id = a.scan_id
            WHERE s.doctor_id=%s
            GROUP BY a.diagnosis_label ORDER BY count DESC
        """, (doctor["doctor_id"],))
        return jsonify({"success": True, "data": cursor.fetchall()})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close(); conn.close()

# ************************************************************
# دالة مؤشرات أداء الطبيب العامة (عدد الفحوصات، الدقة، الساعات)
# ************************************************************
@app.route('/doctor-metrics')
def doctor_metrics():
    doctor_id_from_token = get_doctor_id_from_token()
    if not doctor_id_from_token:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    conn = get_db_connection(); cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT COUNT(s.scan_id) AS total_scans, AVG(a.confidence_score) AS avg_acc
            FROM doctors d
            LEFT JOIN scans s     ON d.doctor_id = s.doctor_id
            LEFT JOIN ai_results a ON s.scan_id  = a.scan_id
            WHERE d.idDoctor = %s
        """, (str(doctor_id_from_token),))
        result = cursor.fetchone()
        total  = result['total_scans'] if result and result['total_scans'] else 0
        acc    = result['avg_acc']     if result and result['avg_acc']     else 0
        return jsonify({"success": True,
                        "total_scans":    int(total),
                        "accuracy":       round(float(acc), 1),
                        "clinical_hours": round((int(total) * 15) / 60, 1)})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close(); conn.close()

# ************************************************************
# دالة جلب بيانات لوحة تحكم المريض (آخر فحص + أقرب موعد)
# ************************************************************
@app.route("/patient-dashboard-data")
def patient_dashboard_data():
    patient_identity = get_patient_id_from_token()
    if not patient_identity:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    conn = get_db_connection(); cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT patient_id, full_name FROM patients WHERE PatientId=%s",
            (patient_identity,)
        )
        patient = cursor.fetchone()
        if not patient:
            return jsonify({"success": False, "message": "Patient not found"}), 404

        cursor.execute("""
            SELECT s.image_path,
                   DATE_FORMAT(s.scan_date,'%%Y-%%m-%%d') AS scan_date,
                   ai.diagnosis_label, s.notes
            FROM scans s
            LEFT JOIN ai_results ai ON ai.scan_id = s.scan_id
            WHERE s.patient_id = %s
            ORDER BY s.scan_date DESC LIMIT 1
        """, (patient["patient_id"],))
        scan = cursor.fetchone()

        cursor.execute("""
    SELECT DATE_FORMAT(a.preferred_date,'%%Y-%%m-%%d') AS preferred_date,
           TIME_FORMAT(a.preferred_time,'%%H:%%i') AS preferred_time,
           d.first_name, d.last_name
    FROM appointments a
    LEFT JOIN doctors d ON d.doctor_id = a.doctor_id
    WHERE a.patient_id = %s
      AND a.status IN ('pending','confirmed')
      AND a.preferred_date >= CURDATE()
    ORDER BY a.preferred_date ASC, a.preferred_time ASC
    LIMIT 1
""", (patient["patient_id"],))
        appointment = cursor.fetchone()

        return jsonify({"success": True, "patient": {
            "full_name":       patient["full_name"],
            "diagnosis_label": scan["diagnosis_label"] if scan else "No Diagnosis",
            "notes":           scan["notes"]           if scan else "",
            "scan_date":       scan["scan_date"]       if scan else "",
            "image_path":      scan["image_path"]      if scan else None,
            "preferred_date":  appointment["preferred_date"]  if appointment else "No Appointment",
            "preferred_time":  appointment["preferred_time"]  if appointment else "",
            "first_name":      appointment["first_name"]       if appointment else "",
            "last_name":       appointment["last_name"]        if appointment else ""
        }})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close(); conn.close()

# ************************************************************
# دالة جلب كل فحوصات المريض
# ************************************************************
@app.route("/patient-scans")
def patient_scans():
    patient_identity = get_patient_id_from_token()
    if not patient_identity:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    conn = get_db_connection(); cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT s.scan_id, s.scan_type,
                   DATE_FORMAT(s.scan_date,'%%Y-%%m-%%d') AS scan_date,
                   s.image_path, s.notes, s.status,
                   ai.diagnosis_label, ai.confidence_score,ai.findings_json
            FROM scans s
            JOIN patients p     ON s.patient_id = p.patient_id
            LEFT JOIN ai_results ai ON ai.scan_id = s.scan_id
            LEFT JOIN clinical_notes n ON n.scan_id = s.scan_id
            WHERE p.PatientId = %s
            ORDER BY s.scan_date DESC
        """, (patient_identity,))
        scans = cursor.fetchall()
        for scan in scans:
            if scan.get("confidence_score") is not None:
                scan["confidence_score"] = float(scan["confidence_score"])
        return jsonify({"success": True, "scans": scans})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close(); conn.close()

# ************************************************************
# دالة جلب قائمة الأطباء (لعرضهم عند حجز موعد)
# ************************************************************
@app.route("/api/doctors")
def get_doctors():
    conn = get_db_connection(); cursor = conn.cursor()
    try:
        cursor.execute("SELECT idDoctor, doctor_id, first_name, last_name FROM doctors")
        return jsonify({"success": True, "doctors": cursor.fetchall()})
    finally:
        cursor.close(); conn.close()

# ************************************************************
# دالة جلب مواعيد المريض (القادم + السجل + الحجوزات المعلّقة)
# ************************************************************
@app.route("/api/appointments/my")
def my_appointments():
    patient_internal_id = get_patient_internal_id()
    if not patient_internal_id:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    conn = get_db_connection(); cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT a.*, d.first_name, d.last_name
            FROM appointments a
            JOIN doctors d ON a.doctor_id = d.doctor_id
            WHERE a.patient_id = %s AND a.status IN ('pending','confirmed')
              AND a.preferred_date >= CURDATE()
            ORDER BY a.preferred_date ASC, a.preferred_time ASC
            LIMIT 1
        """, (patient_internal_id,))
        upcoming = serialize_row(cursor.fetchone())

        cursor.execute("""
            SELECT a.*, d.first_name, d.last_name
            FROM appointments a
            JOIN doctors d ON a.doctor_id = d.doctor_id
            WHERE a.patient_id = %s AND a.status = 'completed'
            ORDER BY a.preferred_date DESC
        """, (patient_internal_id,))
        history = [serialize_row(r) for r in cursor.fetchall()]

        cursor.execute("""
            SELECT a.*, d.first_name, d.last_name
            FROM appointments a
            JOIN doctors d ON a.doctor_id = d.doctor_id
            WHERE a.patient_id = %s AND a.status = 'pending'
              AND a.preferred_date >= CURDATE()
            ORDER BY a.created_at DESC
        """, (patient_internal_id,))
        booking = [serialize_row(r) for r in cursor.fetchall()]

        return jsonify({"success": True, "upcoming": upcoming, "history": history, "booking": booking})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close(); conn.close()

# ************************************************************
# دالة حجز موعد جديد للمريض
# ************************************************************
@app.route("/api/appointments/book", methods=["POST"])
def book_appointment():
    patient_id = get_patient_internal_id()
    if not patient_id:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    data = request.json
    doctor_id      = data.get("doctor_id")
    preferred_date = data.get("preferred_date")
    preferred_time = data.get("preferred_time")
    if not all([doctor_id, preferred_date, preferred_time]):
        return jsonify({"success": False, "message": "Missing data"}), 400

    booking_date = datetime.datetime.strptime(preferred_date, "%Y-%m-%d").date()
    if booking_date < date.today() + timedelta(days=1):
        return jsonify({"success": False, "message": "Appointments start from tomorrow."})

    booking_time = datetime.datetime.strptime(preferred_time, "%H:%M").time()
    if booking_time < time(8, 0) or booking_time > time(14, 0):
        return jsonify({"success": False, "message": "Appointments available 08:00–14:00 only."})

    conn = get_db_connection(); cursor = conn.cursor()
    try:
        cursor.execute("SELECT doctor_id FROM doctors WHERE idDoctor=%s", (doctor_id,))
        doctor = cursor.fetchone()
        if not doctor:
            return jsonify({"success": False, "message": "Doctor not found"})

        cursor.execute("""
            SELECT appointment_id FROM appointments
            WHERE doctor_id=%s AND preferred_date=%s AND preferred_time=%s AND status<>'cancelled'
        """, (doctor["doctor_id"], preferred_date, preferred_time))
        if cursor.fetchone():
            return jsonify({"success": False, "message": "This slot is already booked."})

        cursor.execute("""
            INSERT INTO appointments (patient_id, doctor_id, preferred_date, preferred_time, status, appointment_type)
            VALUES (%s, %s, %s, %s, 'pending', 'new_visit')
        """, (patient_id, doctor["doctor_id"], preferred_date, preferred_time))
        conn.commit()
        return jsonify({"success": True, "message": "Appointment booked successfully."})
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close(); conn.close()

# ************************************************************
# دالة إلغاء موعد المريض
# ************************************************************
@app.route("/api/appointments/cancel/<int:appointment_id>", methods=["PUT"])
@app.route("/api/deletedd/<int:appointment_id>", methods=["PUT"])
def cancel_appointment(appointment_id):
    patient_id = get_patient_internal_id()
    if not patient_id:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    conn = get_db_connection(); cursor = conn.cursor()
    try:
        cursor.execute(
            "DELETE FROM appointments WHERE appointment_id=%s AND patient_id=%s",
            (appointment_id, patient_id)
        )
        conn.commit()
        return jsonify({"success": True, "message": "Appointment cancelled"})
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close(); conn.close()



# ************************************************************
# دالة استخراج username المدير من التوكن
# ************************************************************
def get_admin_username_from_token():
    auth = request.headers.get('Authorization', '')
    if not auth:
        return None
    try:
        token = auth.replace('Bearer ', '').strip()
        decoded = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        if decoded.get('role') != 'admin':
            return None
        return decoded.get('user_id')
    except Exception as e:
        print("JWT ERROR:", e)
        return None

# ************************************************************
# ديكوريتور للتحقق من صلاحية المدير قبل تنفيذ أي دالة إدارية
# ************************************************************
def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not get_admin_username_from_token():
            return jsonify({"success": False, "message": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return wrapper

# ************************************************************
# صفحة لوحة تحكم المدير
# ************************************************************
@app.route('/manager-dashboard.html')
def manager_dashboard_page():
    return render_template('manager_dashboard.html')

# ************************************************************
# صفحة حساب المدير
# ************************************************************
@app.route('/manager-page.html')
def manager_account_page():
    return render_template('manager_page.html')

# ************************************************************
# دالة جلب بيانات حساب المدير
# ************************************************************
@app.route('/manager/api/admin-info')
@admin_required
def manager_admin_info():
    username = get_admin_username_from_token()
    conn = get_db_connection(); cursor = conn.cursor()
    try:
        cursor.execute("SELECT full_name, id_number, username FROM admins WHERE username=%s", (username,))
        admin = cursor.fetchone()
        if not admin:
            return jsonify({"success": False}), 404
        return jsonify({"success": True, "admin": admin})
    finally:
        cursor.close(); conn.close()

# ************************************************************
# دالة تحديث بيانات حساب المدير
# ************************************************************
@app.route('/manager/api/update-admin', methods=['PUT'])
@admin_required
def manager_update_admin():
    current_username = get_admin_username_from_token()
    data = request.get_json()
    new_username = data.get('username', '').strip()
    new_password = data.get('password', '').strip()
    if not new_username:
        return jsonify({"success": False, "message": "اسم المستخدم مطلوب"}), 400
    conn = get_db_connection(); cursor = conn.cursor()
    try:
        if new_password:
            hashed = generate_password_hash(new_password)
            cursor.execute(
                "UPDATE admins SET username=%s, password=%s WHERE username=%s",
                (new_username, hashed, current_username)
            )
        else:
            cursor.execute(
                "UPDATE admins SET username=%s WHERE username=%s",
                (new_username, current_username)
            )
        conn.commit()
        new_token = jwt.encode({
            'user_id': new_username, 'role': 'admin',
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)
        }, app.config['SECRET_KEY'], algorithm='HS256')
        return jsonify({"success": True, "message": "تم تحديث بيانات المدير بنجاح", "token": new_token})
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close(); conn.close()

# ************************************************************
# دالة جلب قائمة الأطباء (لوحة المدير)
# ************************************************************
@app.route('/manager/api/doctors')
@admin_required
def manager_get_doctors():
    conn = get_db_connection(); cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT idDoctor, first_name, last_name, password_hash,
                   email, phone, specialty, clinic_name
            FROM doctors
        """)
        return jsonify({"success": True, "doctors": cursor.fetchall()})
    finally:
        cursor.close(); conn.close()

# ************************************************************
# دالة إضافة طبيب جديد من قبل المدير
# ************************************************************
@app.route('/manager/api/add-doctor', methods=['POST'])
@admin_required
def manager_add_doctor():
    data = request.get_json()
    id_doctor  = data.get('idDoctor', '').strip()
    first_name = data.get('first_name', '').strip()
    last_name  = data.get('last_name', '').strip()
    password   = data.get('password', '').strip()
    email      = data.get('email', '').strip()
    phone      = data.get('phone', '').strip()
    specialty  = data.get('specialty', '').strip()
    clinic     = data.get('clinic_name', '').strip()

    if not id_doctor or not first_name or not last_name or not password:
        return jsonify({"success": False, "message": "الحقول الأساسية مطلوبة"}), 400

    conn = get_db_connection(); cursor = conn.cursor()
    try:
        cursor.execute("SELECT idDoctor FROM doctors WHERE idDoctor=%s", (id_doctor,))
        if cursor.fetchone():
            return jsonify({"success": False, "message": "رقم الطبيب مستخدم بالفعل"}), 400

        cursor.execute("""
            INSERT INTO doctors (idDoctor, first_name, last_name, password_hash,
                                  email, phone, specialty, clinic_name, role)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,'doctor')
        """, (id_doctor, first_name, last_name, password, email, phone, specialty, clinic))
        conn.commit()
        login_id = first_name.strip()[0].lower() + str(id_doctor)
        return jsonify({"success": True, "message": f"تمت إضافة الطبيب. اسم الدخول: {login_id}"})
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close(); conn.close()

# ************************************************************
# دالة تعديل بيانات طبيب من قبل المدير
# ************************************************************
@app.route('/manager/api/update-doctor', methods=['PUT'])
@admin_required
def manager_update_doctor():
    data = request.get_json()
    id_doctor = data.get('idDoctor', '').strip()
    if not id_doctor:
        return jsonify({"success": False, "message": "رقم الطبيب مطلوب"}), 400
    conn = get_db_connection(); cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE doctors SET first_name=%s, last_name=%s, password_hash=%s,
                   email=%s, phone=%s, specialty=%s, clinic_name=%s
            WHERE idDoctor=%s
        """, (data.get('first_name','').strip(), data.get('last_name','').strip(),
              data.get('password','').strip(), data.get('email','').strip(),
              data.get('phone','').strip(), data.get('specialty','').strip(),
              data.get('clinic_name','').strip(), id_doctor))
        conn.commit()
        return jsonify({"success": True, "message": "تم تعديل بيانات الطبيب بنجاح"})
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close(); conn.close()

# ************************************************************
# دالة حذف طبيب من قبل المدير
# ************************************************************
@app.route('/manager/api/delete-doctor', methods=['DELETE'])
@admin_required
def manager_delete_doctor():
    data = request.get_json()
    id_doctor = data.get('idDoctor', '').strip()
    if not id_doctor:
        return jsonify({"success": False, "message": "رقم الطبيب مطلوب"}), 400
    conn = get_db_connection(); cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM doctors WHERE idDoctor=%s", (id_doctor,))
        conn.commit()
        return jsonify({"success": True, "message": "تم حذف الطبيب بنجاح"})
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close(); conn.close()

# ************************************************************
# دالة جلب قائمة المرضى (لوحة المدير)
# ************************************************************
@app.route('/manager/api/patients')
@admin_required
def manager_get_patients():
    conn = get_db_connection(); cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT patient_id, PatientId, full_name, phone, emailP, date_of_birth
            FROM patients
        """)
        return jsonify({"success": True, "patients": cursor.fetchall()})
    finally:
        cursor.close(); conn.close()

# ************************************************************
# دالة إضافة مريض جديد من قبل المدير
# ************************************************************
@app.route('/manager/api/add-patient', methods=['POST'])
@admin_required
def manager_add_patient():
    data = request.get_json()
    patient_id = data.get('PatientId', '').strip()
    full_name  = data.get('full_name', '').strip()
    phone      = data.get('phone', '').strip()
    email      = data.get('emailP', '').strip()
    dob        = data.get('date_of_birth', '') or None
    password   = data.get('password', '').strip() or patient_id

    if not patient_id or not full_name:
        return jsonify({"success": False, "message": "رقم الهوية والاسم مطلوبان"}), 400

    conn = get_db_connection(); cursor = conn.cursor()
    try:
        cursor.execute("SELECT PatientId FROM patients WHERE PatientId=%s", (patient_id,))
        if cursor.fetchone():
            return jsonify({"success": False, "message": "رقم الهوية مسجل مسبقاً"}), 400
        hashed = generate_password_hash(password)
        cursor.execute("""
            INSERT INTO patients (PatientId, full_name, phone, emailP, date_of_birth, password_hash)
            VALUES (%s,%s,%s,%s,%s,%s)
        """, (patient_id, full_name, phone, email, dob, hashed))
        conn.commit()
        return jsonify({"success": True, "message": "تم تسجيل المريض بنجاح"})
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close(); conn.close()

# ************************************************************
# دالة تعديل بيانات مريض من قبل المدير
# ************************************************************
@app.route('/manager/api/update-patient', methods=['PUT'])
@admin_required
def manager_update_patient():
    data = request.get_json()
    patient_id = data.get('PatientId', '').strip()
    if not patient_id:
        return jsonify({"success": False, "message": "رقم الهوية مطلوب"}), 400
    conn = get_db_connection(); cursor = conn.cursor()
    try:
        new_password = data.get('password', '').strip()
        if new_password:
            hashed = generate_password_hash(new_password)
            cursor.execute("""
                UPDATE patients SET full_name=%s, phone=%s, emailP=%s,
                       date_of_birth=%s, password_hash=%s WHERE PatientId=%s
            """, (data.get('full_name','').strip(), data.get('phone','').strip(),
                  data.get('emailP','').strip(), data.get('date_of_birth') or None,
                  hashed, patient_id))
        else:
            cursor.execute("""
                UPDATE patients SET full_name=%s, phone=%s, emailP=%s, date_of_birth=%s
                WHERE PatientId=%s
            """, (data.get('full_name','').strip(), data.get('phone','').strip(),
                  data.get('emailP','').strip(), data.get('date_of_birth') or None,
                  patient_id))
        conn.commit()
        return jsonify({"success": True, "message": "تم تعديل بيانات المريض بنجاح"})
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close(); conn.close()

# ************************************************************
# دالة حذف مريض من قبل المدير
# ************************************************************
@app.route('/manager/api/delete-patient', methods=['DELETE'])
@admin_required
def manager_delete_patient():
    data = request.get_json()
    patient_id = data.get('PatientId', '').strip()
    if not patient_id:
        return jsonify({"success": False, "message": "رقم الهوية مطلوب"}), 400
    conn = get_db_connection(); cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM patients WHERE PatientId=%s", (patient_id,))
        conn.commit()
        return jsonify({"success": True, "message": "تم حذف المريض بنجاح"})
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close(); conn.close()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)