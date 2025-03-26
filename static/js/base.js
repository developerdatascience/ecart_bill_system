document.addEventListener('DOMContentLoaded', function() {
    const sidebar_btn = document.getElementById('toggle-btn');
    const sidebar = document.getElementById('sidebar');

    sidebar_btn.addEventListener('click', function() {
        sidebar.classList.toggle('collapsed');

    });
});


document.addEventListener('DOMContentLoaded', () => {
    // Handle AJAX navigation
    document.querySelectorAll('.ajax-link').forEach(link => {
        link.addEventListener('click', async (e) => {
            e.preventDefault();
            const url = link.getAttribute('href');
            
            try {
                // Fetch new page
                const response = await fetch(url);
                const text = await response.text();
                
                // Extract content from response
                const parser = new DOMParser();
                const doc = parser.parseFromString(text, 'text/html');
                const newContent = doc.getElementById('main-content').innerHTML;
                const newTitle = doc.querySelector('title').innerText;

                // Update DOM
                document.getElementById('main-content').innerHTML = newContent;
                document.title = newTitle;
                history.pushState({}, '', url);
            } catch (error) {
                window.location.href = url;
            }
        });
    });

    // Handle back/forward navigation
    window.addEventListener('popstate', async () => {
        const url = window.location.pathname;
        const response = await fetch(url);
        const text = await response.text();
        const parser = new DOMParser();
        const doc = parser.parseFromString(text, 'text/html');
        document.getElementById('main-content').innerHTML = doc.getElementById('main-content').innerHTML;
    });
});