function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie('csrftoken');

$(document).ready(function() {
    // Use event delegation on the list for potetialy dynamic cotent (good practice)
    $('.match-list').on('click', '.attend-button', function() {
        const button = $(this);
        const matchId = button.data('match-id');
        // Find status/count spans relative to the buton's list item parent
        const listItem = button.closest('li'); // Find the parent <li>
        const statusSpan = listItem.find(`.attend-status[data-match-id=${matchId}]`);
        const countSpan = listItem.find(`.attendee-count[data-match-id=${matchId}]`);

        // Prevent multiple clicks while processing
        if (button.prop('disabled')) {
            return; // Already disabled (either procesing or already attemding)
        }
        button.prop('disabled', true); // Disanle immediately
        statusSpan.text('Processing...').css('color', 'grey').show(); // Provide feedback

        $.ajax({
            url: "{% url 'Match_Ready:attend_match_ajax' %}", // The URL for our AJAX view
            type: "POST",
            data: {
                'match_id': matchId,
                'csrfmiddlewaretoken': csrftoken // Include CSRD token
            },
            dataType: 'json', // Expect JSON response
            success: function(data) {
                if (data.status === 'success') {
                    statusSpan.text(data.message).css('color', 'green').fadeOut(4000); // Fade out success message after 4 seconds
                    button.text('Attending'); // Keep button disabled abd text updated
                    countSpan.text(data.new_count); // Update count
                } else {
                    // Handle specific errors reported by the server (e.g., already attending)
                    statusSpan.text('Error: ' + data.message).css('color', 'red');
                    if (data.already_attending) {
                         button.text('Attending'); // Ensure text is correct, keepdisabled
                    } else {
                         button.prop('disabled', false); // Re-enable button on other logical errors
                    }
                }
            },
            error: function(xhr, errmsg, err) {
                console.error("AJAX Error:", xhr.status, xhr.responseText); // Log dstailed error to console
                let errorMsg = 'An error occurred. Please try again.';
                if (xhr.status === 403) { // Forbidden (likely not logged in)
                     errorMsg = 'Please login to attend.';
                     // Optional: Redirect to login
                     // window.location.href = "{% url 'Match_Ready:login' %}?next=" + window.location.pathname;
                } else if (xhr.status === 404) { // Not Found
                    errorMsg = 'Match not found.';
                } else if (xhr.status === 400 && xhr.responseJSON && xhr.responseJSON.message) { // Bqd Request with JSON message
                    errorMsg = 'Error: ' + xhr.responseJSON.message;
                     if (xhr.responseJSON.already_attending) {
                         button.text('Attending'); // Keep disabled
                     }
                } else if (xhr.status === 405) { // Method Not Allowed
                     errorMsg = 'Invalid request method.';
                } else if (xhr.status >= 500) { // Server error
                     errorMsg = 'Server error. Please try again later.';
                }

                statusSpan.text(errorMsg).css('color', 'red');

                // Only re-enable the button if the error wasn't "already attending"
                if (!button.text().includes('Attending')) {
                    button.prop('disabled', false);
                }
            }
        });
    });
});