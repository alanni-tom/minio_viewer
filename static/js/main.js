function toggleView(mode) {
    const container = document.getElementById('file-browser-container');
    if (mode === 'grid') {
        container.classList.remove('view-list');
        container.classList.add('view-grid', 'grid', 'grid-cols-2', 'md:grid-cols-4', 'gap-4');
    } else {
        container.classList.remove('view-grid', 'grid', 'grid-cols-2', 'md:grid-cols-4', 'gap-4');
        container.classList.add('view-list', 'flex', 'flex-col', 'space-y-2');
    }
    localStorage.setItem('minioViewMode', mode);
}

document.querySelectorAll('.folder-item').forEach(item => {
    item.addEventListener('dblclick', function() {
        const folderPath = this.getAttribute('data-path');
        const currentBase = window.location.pathname;
        window.location.href = currentBase + (currentBase.endsWith('/') ? '' : '/') + folderPath;
    });
});