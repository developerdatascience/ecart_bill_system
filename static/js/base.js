document.addEventListener('DOMContentLoaded', function() {
    const sidebar_btn = document.getElementById('toggle-btn');
    const sidebar = document.getElementById('sidebar');

    sidebar_btn.addEventListener('click', function() {
        sidebar.classList.toggle('collapsed');

    });


});