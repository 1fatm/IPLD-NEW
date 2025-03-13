document.addEventListener('DOMContentLoaded', () => {
    // ==================================================
    // Gestion des sections et du sidebar
    // ==================================================

    // Cacher toutes les sections au chargement de la page
    const sections = document.querySelectorAll('.main-content section');
    sections.forEach(section => section.style.display = 'none');

    // Afficher la section "Accueil" par défaut
    const defaultSection = document.querySelector('#home');
    if (defaultSection) {
        defaultSection.style.display = 'block';
    }

    // Gérer les clics sur les liens du menu
    const navLinks = document.querySelectorAll('.sidebar a');
    navLinks.forEach(link => {
        link.addEventListener('click', function (e) {
            e.preventDefault(); // Empêcher le comportement par défaut du lien

            // Cacher toutes les sections
            sections.forEach(section => section.style.display = 'none');

            // Afficher la section correspondante
            const target = this.getAttribute('data-target');
            const targetSection = document.querySelector(`#${target}`);
            if (targetSection) {
                targetSection.style.display = 'block';
            }
        });
    });

    // Gestion du sidebar
    const sidebar = document.querySelector('.sidebar');
    const sidebarToggle = document.getElementById('sidebarToggle');

    if (sidebar && sidebarToggle) {
        // Fonction pour ouvrir/fermer le sidebar
        sidebarToggle.addEventListener('click', function () {
            sidebar.classList.toggle('translate-x-0');
sidebar.classList.toggle('-translate-x-full');
sidebar.classList.toggle('shadow-lg'); // Optionnel : Ajoute une ombre au sidebar quand il est ouvert

        });
    }

    // ==================================================
    // Récupération des données dynamiques depuis le backend
    // ==================================================

    // Récupérer les données de la page d'accueil (statistiques et rappels)
    fetch('/api/home-data')
        .then(response => response.json())
        .then(data => {
            const statsContainer = document.getElementById('stats-container');
            const remindersList = document.getElementById('reminders-list');

            // Injecter les statistiques
            statsContainer.innerHTML = data.stats.map(stat => `
                <div class="stat-box">
                    <h3><i class="${stat.icon}" style="color: ${stat.color};"></i> ${stat.title}</h3>
                    <p>${stat.value}</p>
                </div>
            `).join('');

            // Injecter les rappels
            remindersList.innerHTML = data.reminders.map(reminder => `
                <li>${reminder}</li>
            `).join('');
        })
        .catch(error => console.error('Erreur lors de la récupération des données :', error));

    // Récupérer les notifications
    fetch('/api/notifications')
        .then(response => response.json())
        .then(data => {
            const notificationsList = document.getElementById('notifications-list');
            notificationsList.innerHTML = data.map(notification => `
                <div class="notification-item">
                    <div>
                        <p class="text-gray-700 font-medium">📌 ${notification.message}</p>
                        <small class="text-gray-500">⏳ ${new Date(notification.date).toLocaleString()}</small>
                    </div>
                    <i class="fas fa-bell text-blue-500 text-xl"></i>
                </div>
            `).join('');
        });

    // Récupérer les devoirs
    fetch('/api/exam-topics')
        .then(response => response.json())
        .then(data => {
            const examTopicsList = document.getElementById('exam-topics-list');
            examTopicsList.innerHTML = data.map(topic => `
                <div class="exam-topic-item">
                    <h3 class="text-2xl font-semibold text-gray-700 mb-3 flex items-center">
                        📖 <span class="ml-2 text-blue-600">${topic.subject}</span>
                    </h3>
                    <p class="text-gray-500 mb-6">📅 Publié le : <span class="font-medium text-gray-700">${new Date(topic.date).toLocaleDateString()}</span></p>
                    <div class="flex justify-end space-x-4 mt-6">
                        <a href="${topic.fileUrl}" class="download-link">
                            <i class="fas fa-download mr-2"></i> Télécharger
                        </a>
                    </div>
                </div>
            `).join('');
        });

    // Récupérer les notes
    fetch('/api/grades')
        .then(response => response.json())
        .then(data => {
            const gradesList = document.getElementById('grades-list');
            gradesList.innerHTML = data.map(grade => `
                <div class="grade-item">
                    <h3 class="text-2xl font-semibold text-gray-700 mb-2 flex items-center">
                        📖 <span class="ml-2 text-blue-600">${grade.subject}</span>
                    </h3>
                    <p class="text-gray-600 text-lg mb-2">
                        <span class="font-bold text-green-600 text-xl">⭐ ${grade.score}</span>
                    </p>
                    <p class="text-gray-500 italic">📝 ${grade.comment}</p>
                </div>
            `).join('');
        });
});