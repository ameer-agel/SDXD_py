/* ================================================================
   manager.js — جميع وظائف JavaScript لواجهة المدير (مرتبطة بـ web.py)
   ================================================================ */

// ======= AUTH GUARD =======
(function authGuard() {
    const token = sessionStorage.getItem('auth_token');
    const role = sessionStorage.getItem('role');
    if (!token || role !== 'admin') {
        window.location.href = '/loginpat.html';
    }
})();

function managerLogout() {
    sessionStorage.clear();
    localStorage.removeItem('token');
    localStorage.removeItem('role');
    window.location.href = '/loginpat.html';
}

// ======= DARK MODE =======
function initDarkMode() {
    const isDark = localStorage.getItem('theme') === 'dark';
    if (isDark) document.body.classList.add('dark-mode');
}

function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
    localStorage.setItem('theme', document.body.classList.contains('dark-mode') ? 'dark' : 'light');
}

// ======= TOAST =======
function showToast(message, type = 'success') {
    let toast = document.getElementById('toast');
    if (!toast) {
        toast = document.createElement('div');
        toast.id = 'toast';
        toast.className = 'toast';
        document.body.appendChild(toast);
    }
    toast.textContent = message;
    toast.className = `toast ${type}`;
    setTimeout(() => toast.classList.add('show'), 10);
    setTimeout(() => toast.classList.remove('show'), 3500);
}

// ======= VALIDATION =======
function validateField(inputId, errorId, rules = {}) {
    const input = document.getElementById(inputId);
    const error = document.getElementById(errorId);
    const value = input ? input.value.trim() : '';

    if (error) error.classList.remove('show');

    if (rules.required && value === '') {
        if (error) { error.textContent = 'لا يمكن أن يكون هذا الحقل فارغاً'; error.classList.add('show'); }
        return false;
    }
    if (rules.maxLength && value.length > rules.maxLength) {
        if (error) { error.textContent = `يجب أن يكون أقل من ${rules.maxLength} حرفاً`; error.classList.add('show'); }
        return false;
    }
    if (rules.minLength && value.length < rules.minLength) {
        if (error) { error.textContent = `يجب أن يكون أكثر من ${rules.minLength} أحرف`; error.classList.add('show'); }
        return false;
    }
    return true;
}

// ======= MODAL =======
function openModal(id) {
    const m = document.getElementById(id);
    if (m) m.classList.add('active');
}
function closeModal(id) {
    const m = document.getElementById(id);
    if (m) m.classList.remove('active');
}

// ======= TABS =======
function switchTab(tabId, btn) {
    document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.getElementById(tabId).classList.add('active');
    btn.classList.add('active');
}

// ======= API HELPER (JWT) =======
async function apiRequest(url, method = 'GET', body = null) {
    const token = sessionStorage.getItem('auth_token');
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + (token || '')
        }
    };
    if (body) options.body = JSON.stringify(body);

    const res = await fetch(url, options);

    if (res.status === 401) {
        sessionStorage.clear();
        window.location.href = '/loginpat.html';
        return { success: false };
    }
    return res.json();
}

// ======= UTILITY =======
function escHtml(str) {
    return String(str ?? '')
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

// ================================================================
// DOCTORS
// ================================================================
async function loadDoctors() {
    const tbody = document.getElementById('doctors-tbody');
    if (!tbody) return;
    tbody.innerHTML = '<tr><td colspan="8" class="empty-state">جاري التحميل...</td></tr>';

    const data = await apiRequest('/manager/api/doctors');
    if (!data.success) {
        tbody.innerHTML = `<tr><td colspan="8" class="empty-state">${data.message || 'حدث خطأ'}</td></tr>`;
        return;
    }
    if (!data.doctors || data.doctors.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" class="empty-state">لا يوجد أطباء بقاعدة البيانات</td></tr>';
        return;
    }
    document.getElementById('stat-doctors').textContent = data.doctors.length;

    tbody.innerHTML = data.doctors.map(doc => `
        <tr>
            <td>${escHtml(doc.idDoctor)}</td>
            <td>${escHtml(doc.first_name)} ${escHtml(doc.last_name)}</td>
            <td>${escHtml(doc.password_hash)}</td>
            <td>${escHtml(doc.email)}</td>
            <td>${escHtml(doc.phone)}</td>
            <td>${escHtml(doc.specialty)}</td>
            <td>${escHtml(doc.clinic_name)}</td>
            <td>
                <div class="btn-group">
                    <button class="btn btn-primary btn-sm" onclick='openEditDoctorModal(${JSON.stringify(doc)})'>تعديل</button>
                    <button class="btn btn-danger btn-sm" onclick="confirmDelete('doctor','${escHtml(doc.idDoctor)}','${escHtml(doc.first_name)} ${escHtml(doc.last_name)}')">حذف</button>
                </div>
            </td>
        </tr>
    `).join('');
}

async function submitAddDoctor(e) {
    e.preventDefault();
    const ok1 = validateField('add-doc-idDoctor', 'add-doc-idDoctor-error', { required: true, maxLength: 50 });
    const ok2 = validateField('add-doc-password', 'add-doc-password-error', { required: true, minLength: 4 });
    const ok3 = validateField('add-doc-first', 'add-doc-first-error', { required: true });
    const ok4 = validateField('add-doc-last', 'add-doc-last-error', { required: true });
    if (!ok1 || !ok2 || !ok3 || !ok4) return;

    const payload = {
        idDoctor: document.getElementById('add-doc-idDoctor').value.trim(),
        password: document.getElementById('add-doc-password').value.trim(),
        first_name: document.getElementById('add-doc-first').value.trim(),
        last_name: document.getElementById('add-doc-last').value.trim(),
        email: document.getElementById('add-doc-email').value.trim(),
        phone: document.getElementById('add-doc-phone').value.trim(),
        specialty: document.getElementById('add-doc-specialty').value.trim(),
        clinic_name: document.getElementById('add-doc-clinic').value.trim()
    };

    const data = await apiRequest('/manager/api/add-doctor', 'POST', payload);
    if (data.success) {
        showToast(data.message, 'success');
        closeModal('add-doctor-modal');
        document.getElementById('add-doctor-form').reset();
        loadDoctors();
    } else {
        showToast(data.message || 'حدث خطأ', 'error');
    }
}

function openEditDoctorModal(doc) {
    document.getElementById('edit-doc-idDoctor').value = doc.idDoctor;
    document.getElementById('edit-doc-first').value = doc.first_name || '';
    document.getElementById('edit-doc-last').value = doc.last_name || '';
    document.getElementById('edit-doc-password').value = doc.password_hash || '';
    document.getElementById('edit-doc-email').value = doc.email || '';
    document.getElementById('edit-doc-phone').value = doc.phone || '';
    document.getElementById('edit-doc-specialty').value = doc.specialty || '';
    document.getElementById('edit-doc-clinic').value = doc.clinic_name || '';
    openModal('edit-doctor-modal');
}

async function submitEditDoctor(e) {
    e.preventDefault();
    const ok1 = validateField('edit-doc-first', 'edit-doc-first-error', { required: true });
    const ok2 = validateField('edit-doc-last', 'edit-doc-last-error', { required: true });
    const ok3 = validateField('edit-doc-password', 'edit-doc-password-error', { required: true, minLength: 4 });
    if (!ok1 || !ok2 || !ok3) return;

    const payload = {
        idDoctor: document.getElementById('edit-doc-idDoctor').value,
        first_name: document.getElementById('edit-doc-first').value.trim(),
        last_name: document.getElementById('edit-doc-last').value.trim(),
        password: document.getElementById('edit-doc-password').value.trim(),
        email: document.getElementById('edit-doc-email').value.trim(),
        phone: document.getElementById('edit-doc-phone').value.trim(),
        specialty: document.getElementById('edit-doc-specialty').value.trim(),
        clinic_name: document.getElementById('edit-doc-clinic').value.trim()
    };

    const data = await apiRequest('/manager/api/update-doctor', 'PUT', payload);
    if (data.success) {
        showToast(data.message, 'success');
        closeModal('edit-doctor-modal');
        loadDoctors();
    } else {
        showToast(data.message || 'حدث خطأ', 'error');
    }
}

async function searchDoctor() {
    const search = document.getElementById('doctor-search-input')?.value.trim();
    if (!search) { loadDoctors(); return; }

    const data = await apiRequest('/manager/api/doctors');
    const tbody = document.getElementById('doctors-tbody');
    if (!data.success || !data.doctors) return;

    const filtered = data.doctors.filter(d => d.idDoctor.toLowerCase().includes(search.toLowerCase()));
    if (filtered.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" class="empty-state">لا توجد نتائج</td></tr>';
        return;
    }
    tbody.innerHTML = filtered.map(doc => `
        <tr>
            <td>${escHtml(doc.idDoctor)}</td>
            <td>${escHtml(doc.first_name)} ${escHtml(doc.last_name)}</td>
            <td>${escHtml(doc.password_hash)}</td>
            <td>${escHtml(doc.email)}</td>
            <td>${escHtml(doc.phone)}</td>
            <td>${escHtml(doc.specialty)}</td>
            <td>${escHtml(doc.clinic_name)}</td>
            <td>
                <div class="btn-group">
                    <button class="btn btn-primary btn-sm" onclick='openEditDoctorModal(${JSON.stringify(doc)})'>تعديل</button>
                    <button class="btn btn-danger btn-sm" onclick="confirmDelete('doctor','${escHtml(doc.idDoctor)}','${escHtml(doc.first_name)} ${escHtml(doc.last_name)}')">حذف</button>
                </div>
            </td>
        </tr>
    `).join('');
}

// ================================================================
// PATIENTS
// ================================================================
async function loadPatients() {
    const tbody = document.getElementById('patients-tbody');
    if (!tbody) return;
    tbody.innerHTML = '<tr><td colspan="6" class="empty-state">جاري التحميل...</td></tr>';

    const data = await apiRequest('/manager/api/patients');
    if (!data.success) {
        tbody.innerHTML = `<tr><td colspan="6" class="empty-state">${data.message || 'حدث خطأ'}</td></tr>`;
        return;
    }
    if (!data.patients || data.patients.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="empty-state">لا يوجد مرضى بقاعدة البيانات</td></tr>';
        return;
    }
    document.getElementById('stat-patients').textContent = data.patients.length;

    tbody.innerHTML = data.patients.map(p => `
        <tr>
            <td>${escHtml(p.PatientId)}</td>
            <td>${escHtml(p.full_name)}</td>
            <td>${escHtml(p.phone)}</td>
            <td>${escHtml(p.emailP)}</td>
            <td>${escHtml(p.date_of_birth)}</td>
            <td>
                <div class="btn-group">
                    <button class="btn btn-primary btn-sm" onclick='openEditPatientModal(${JSON.stringify(p)})'>تعديل</button>
                    <button class="btn btn-danger btn-sm" onclick="confirmDelete('patient','${escHtml(p.PatientId)}','${escHtml(p.full_name)}')">حذف</button>
                </div>
            </td>
        </tr>
    `).join('');
}

async function submitAddPatient(e) {
    e.preventDefault();
    const ok1 = validateField('add-pat-id', 'add-pat-id-error', { required: true });
    const ok2 = validateField('add-pat-name', 'add-pat-name-error', { required: true });
    if (!ok1 || !ok2) return;

    const payload = {
        PatientId: document.getElementById('add-pat-id').value.trim(),
        full_name: document.getElementById('add-pat-name').value.trim(),
        phone: document.getElementById('add-pat-phone').value.trim(),
        emailP: document.getElementById('add-pat-email').value.trim(),
        date_of_birth: document.getElementById('add-pat-dob').value,
        password: document.getElementById('add-pat-password').value.trim()
    };

    const data = await apiRequest('/manager/api/add-patient', 'POST', payload);
    if (data.success) {
        showToast(data.message, 'success');
        closeModal('add-patient-modal');
        document.getElementById('add-patient-form').reset();
        loadPatients();
    } else {
        showToast(data.message || 'حدث خطأ', 'error');
    }
}

function openEditPatientModal(p) {
    document.getElementById('edit-pat-id').value = p.PatientId;
    document.getElementById('edit-pat-name').value = p.full_name || '';
    document.getElementById('edit-pat-phone').value = p.phone || '';
    document.getElementById('edit-pat-email').value = p.emailP || '';
    document.getElementById('edit-pat-dob').value = p.date_of_birth || '';
    document.getElementById('edit-pat-password').value = '';
    openModal('edit-patient-modal');
}

async function submitEditPatient(e) {
    e.preventDefault();
    const ok1 = validateField('edit-pat-name', 'edit-pat-name-error', { required: true });
    if (!ok1) return;

    const payload = {
        PatientId: document.getElementById('edit-pat-id').value,
        full_name: document.getElementById('edit-pat-name').value.trim(),
        phone: document.getElementById('edit-pat-phone').value.trim(),
        emailP: document.getElementById('edit-pat-email').value.trim(),
        date_of_birth: document.getElementById('edit-pat-dob').value,
        password: document.getElementById('edit-pat-password').value.trim()
    };

    const data = await apiRequest('/manager/api/update-patient', 'PUT', payload);
    if (data.success) {
        showToast(data.message, 'success');
        closeModal('edit-patient-modal');
        loadPatients();
    } else {
        showToast(data.message || 'حدث خطأ', 'error');
    }
}

async function searchPatient() {
    const search = document.getElementById('patient-search-input')?.value.trim();
    if (!search) { loadPatients(); return; }

    const data = await apiRequest('/manager/api/patients');
    const tbody = document.getElementById('patients-tbody');
    if (!data.success || !data.patients) return;

    const filtered = data.patients.filter(p => p.PatientId.toLowerCase().includes(search.toLowerCase()));
    if (filtered.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="empty-state">لا توجد نتائج</td></tr>';
        return;
    }
    tbody.innerHTML = filtered.map(p => `
        <tr>
            <td>${escHtml(p.PatientId)}</td>
            <td>${escHtml(p.full_name)}</td>
            <td>${escHtml(p.phone)}</td>
            <td>${escHtml(p.emailP)}</td>
            <td>${escHtml(p.date_of_birth)}</td>
            <td>
                <div class="btn-group">
                    <button class="btn btn-primary btn-sm" onclick='openEditPatientModal(${JSON.stringify(p)})'>تعديل</button>
                    <button class="btn btn-danger btn-sm" onclick="confirmDelete('patient','${escHtml(p.PatientId)}','${escHtml(p.full_name)}')">حذف</button>
                </div>
            </td>
        </tr>
    `).join('');
}

// ================================================================
// DELETE (مشترك بين الطبيب والمريض)
// ================================================================
function confirmDelete(type, id, name) {
    document.getElementById('delete-target-type').value = type;
    document.getElementById('delete-target-id').value = id;
    document.getElementById('delete-target-name').textContent = name;
    openModal('delete-modal');
}

async function submitDelete() {
    const type = document.getElementById('delete-target-type').value;
    const id = document.getElementById('delete-target-id').value;

    let data;
    if (type === 'doctor') {
        data = await apiRequest('/manager/api/delete-doctor', 'DELETE', { idDoctor: id });
    } else {
        data = await apiRequest('/manager/api/delete-patient', 'DELETE', { PatientId: id });
    }

    if (data.success) {
        showToast(data.message, 'success');
        closeModal('delete-modal');
        if (type === 'doctor') loadDoctors(); else loadPatients();
    } else {
        showToast(data.message || 'حدث خطأ', 'error');
    }
}

// ================================================================
// MANAGER ACCOUNT (manager_page.html)
// ================================================================
async function loadAdminInfo() {
    const nameEl = document.getElementById('admin-username');
    if (!nameEl) return;

    const data = await apiRequest('/manager/api/admin-info');
    if (data.success && data.admin) {
        document.getElementById('admin-fullname').textContent = data.admin.full_name || '—';
        document.getElementById('admin-idnumber').textContent = data.admin.id_number || '—';
        document.getElementById('admin-username').textContent = data.admin.username || '—';
    }
}

async function submitUpdateAdmin(e) {
    e.preventDefault();
    const ok1 = validateField('admin-edit-username', 'admin-username-error', { required: true, maxLength: 50 });
    if (!ok1) return;

    const username = document.getElementById('admin-edit-username').value.trim();
    const password = document.getElementById('admin-edit-password').value.trim();

    if (password) {
        const okPass = validateField('admin-edit-password', 'admin-password-error', { minLength: 6 });
        if (!okPass) return;
    }

    const payload = { username, password };
    const data = await apiRequest('/manager/api/update-admin', 'PUT', payload);
    if (data.success) {
        showToast(data.message, 'success');
        if (data.token) {
            sessionStorage.setItem('auth_token', data.token);
            sessionStorage.setItem('token', data.token);
            localStorage.setItem('token', data.token);
        }
        closeModal('edit-admin-modal');
        loadAdminInfo();
    } else {
        showToast(data.message || 'حدث خطأ', 'error');
    }
}

// ======= INIT =======
document.addEventListener('DOMContentLoaded', () => {
    initDarkMode();

    if (document.getElementById('doctors-tbody')) loadDoctors();
    if (document.getElementById('patients-tbody')) loadPatients();
    if (document.getElementById('admin-username')) loadAdminInfo();

    const addDoctorForm = document.getElementById('add-doctor-form');
    if (addDoctorForm) addDoctorForm.addEventListener('submit', submitAddDoctor);

    const editDoctorForm = document.getElementById('edit-doctor-form');
    if (editDoctorForm) editDoctorForm.addEventListener('submit', submitEditDoctor);

    const addPatientForm = document.getElementById('add-patient-form');
    if (addPatientForm) addPatientForm.addEventListener('submit', submitAddPatient);

    const editPatientForm = document.getElementById('edit-patient-form');
    if (editPatientForm) editPatientForm.addEventListener('submit', submitEditPatient);

    const adminEditForm = document.getElementById('admin-edit-form');
    if (adminEditForm) adminEditForm.addEventListener('submit', submitUpdateAdmin);

    const docSearch = document.getElementById('doctor-search-input');
    if (docSearch) docSearch.addEventListener('input', () => searchDoctor());

    const patSearch = document.getElementById('patient-search-input');
    if (patSearch) patSearch.addEventListener('input', () => searchPatient());
});