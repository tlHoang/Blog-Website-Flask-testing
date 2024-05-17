document.getElementById('followBtn').addEventListener('click', (e) => {
    const button = e.target;

    fetch('/follow_action', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            followerId: button.dataset.followerId,
            followingId: button.dataset.followingId
        })
    })
    .then(response => {
        if (!response.ok) {
            response.json().then(data => {
                alert(data.message);
            });
        } else {
            return response.json();
        }
    })
    .then(data => {
        if (data.followStatus === 'add') {
            button.classList.add('following');
            button.textContent = 'Unfollow';
        } else {
            button.classList.remove('following');
            button.textContent = 'Follow';
        }
    })
    .catch(error => console.error('Error:', error));
});
