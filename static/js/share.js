var currentModal;

// Get the <span> element that closes the modal
var spans = document.getElementsByClassName("close");
spans = Array.from(spans);

var submitButton = document.getElementById('share-submit');

const shareButtons = document.querySelectorAll('.share-button');
shareButtons.forEach((btn) => {
    btn.addEventListener('click', (event) => shareButtonClicked(event))
})
function shareButtonClicked(event) {
    const postId = event.currentTarget.dataset.postId;
    console.log(postId);
    var modal = document.querySelector('.modal[data-post-id="' + postId + '"]');
    if (modal !== null) {
        modal.style.display = 'block';
    } else {
        console.error(postId + ' not found ' + event.currentTarget);
    }
    currentModal = modal;
    modal.style.display = 'block';
}

// When the user clicks on <span> (x), close the modal
spans.forEach((span) => {
    span.onclick = function() {
        currentModal.style.display = "none";
    }
});

submitButton.onclick = function() {
    currentModal.style.display = "none";
}

// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
    if (event.target == currentModal) {
        currentModal.style.display = "none";
    }
}