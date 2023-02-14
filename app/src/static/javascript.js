// Executes after page loads
document.addEventListener("DOMContentLoaded", function(){
    // Any javascript code you put here executes when any layout page opens

});

// Show or hide the section that asks for delete confimation
function show_confirm(show) {
    document.getElementById('confirm-delete').style.display = show ? "block" : "none";
}



function delete_movie(id){
    // Mark a video for deletion by browsing to delete_form_movie endpoint
    base_url=location.origin;
    target_url = base_url + '/delete_form_movie/' + id;
    location.href = target_url;
}

function makeTableScroll() {
    // Constant retrieved from server-side via JSP
    var maxRows = 4;

    var table = document.getElementById('myTable');
    var wrapper = table.parentNode;
    var rowsInTable = table.rows.length;
    var height = 0;
    if (rowsInTable > maxRows) {
        for (var i = 0; i < maxRows; i++) {
            height += table.rows[i].clientHeight;
        }
        wrapper.style.height = height + "px";
    }