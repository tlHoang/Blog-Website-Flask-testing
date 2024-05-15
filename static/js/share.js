const shareButtons = document.querySelectorAll('.share-button');
shareButtons.forEach((btn) => {
    btn.addEventListener('click', (event) => shareButtonClicked(event))
})
function shareButtonClicked(event) {
    // event.preventDefault();
    const postId = event.target.dataset.postId;
    const shareForm = document.getElementById('share-form');
    shareForm.dataset.postId = postId;
    shareForm.style.display = 'block';
}
