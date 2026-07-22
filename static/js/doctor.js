async function loadDoctorInfo() {
    // ✅ نفس المكان والاسم اللي loginpat.html يحفظ فيه
    const token = sessionStorage.getItem('auth_token');

    if (!token) {
        window.location.href = '/loginpat.html';
        return;
    }

    try {
        const response = await fetch('/doctor-info', {
            headers: { 'Authorization': 'Bearer ' + token }
        });

        if (response.status === 401) {
            sessionStorage.clear();
            window.location.href = '/loginpat.html';
            return;
        }

        const data = await response.json();

        if (!data.success) {
            console.log("Doctor-info error:", data);
            return;
        }

        const nameEl = document.getElementById('headerDocName');
        if (nameEl) {
            nameEl.innerText = `Dr. ${data.first_name} ${data.last_name}`;
        }

        const imgEl = document.getElementById('profile_photo');
        if (imgEl) {
            imgEl.src = (data.profile_photo && data.profile_photo !== "null")
                ? `/upload/${data.profile_photo}`
                : `https://ui-avatars.com/api/?name=${data.first_name}&background=345e85&color=fff`;
        }

    } catch (err) {
        console.error("LOAD DOCTOR ERROR:", err);
    }
}

document.addEventListener('DOMContentLoaded', loadDoctorInfo);