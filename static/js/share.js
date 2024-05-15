// Get the modal
var modal = document.getElementById("share-modal");

// Get the <span> element that closes the modal
var span = document.getElementsByClassName("close")[0];

var submitButton = document.getElementById('share-submit');

const shareButtons = document.querySelectorAll('.share-button');
shareButtons.forEach((btn) => {
    btn.addEventListener('click', (event) => shareButtonClicked(event))
})
function shareButtonClicked(event) {
    // event.preventDefault();
    const postId = event.target.dataset.postId;
    const shareForm = document.getElementById('share-form');
    modal.dataset.postId = postId;
    modal.style.display = 'block';
}

// When the user clicks on <span> (x), close the modal
span.onclick = function() {
    modal.style.display = "none";
}

submitButton.onclick = function() {
    modal.style.display = "none";
}

// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
}