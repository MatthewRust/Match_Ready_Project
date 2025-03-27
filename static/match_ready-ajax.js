$(document).ready(function(){
    $('[id^="attendance_button_"]').click(function(){
        var button = $(this);
        var matchIdVar = $(this).attr('data_match_id');
        var count_element = $('#attendance_count_' + matchIdVar);

        $.post('/Match_Ready/attending_match/',
            {'match_id' : matchIdVar, 'csrfmiddlewaretoken': '{{ csrf_token }}' },
            function(data){
                count_element.html(data.attendees);
                button.hide();
            })
    });
});