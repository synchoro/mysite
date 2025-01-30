document.addEventListener("DOMContentLoaded", () => {
    const currentPath = window.location.pathname; // 获取当前页面路径
    document.querySelectorAll('.content li a').forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.parentElement.classList.add('active'); // 高亮当前页面对应的导航项
        }
    });
});
