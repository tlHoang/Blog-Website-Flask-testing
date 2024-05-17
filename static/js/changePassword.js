const modal = new bootstrap.Modal(document.getElementById('changePasswordModal'));
document.querySelector('.change-password').addEventListener('click', () => {
    modal.show();
});
document.querySelector('.edit-password').addEventListener('click', changePassword);
modal._element.addEventListener('hidden.bs.modal', () => {
    document.getElementById("currentPassword").value = '';
    document.getElementById("newPassword").value = '';
    document.getElementById("confirmPassword").value = '';
    document.querySelector('.noti').value = '';
});
function changePassword() {
    const currentPassword = document.getElementById("currentPassword").value;
    const newPassword = document.getElementById("newPassword").value;
    const confirmPassword = document.getElementById("confirmPassword").value;
    const userId = document.getElementById("userId").value;
    console.log(userId)
    const noti = document.querySelector('.noti');

    if (newPassword !== confirmPassword) {
        noti.textContent = "New password and confirm password do not match.";
        return;
    }

    fetch('/update_password', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
                // userId: {{ user['id'] }},
                userId: userId,
                currentPassword: currentPassword,
                newPassword: newPassword
            })
        })
        .then(response => {
            if (!response.ok) {
                response.json().then(data => {
                    noti.textContent = data.message;
                });
            } else {
                alert("Password changed successfully.");
                modal.hide();
            }
        })
    .catch(error => {
        console.error('Error:', error);
        alert("An error occurred. Please try again later.");
    });
}