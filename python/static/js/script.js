// script.js

document.addEventListener('DOMContentLoaded', () => {
    // --- Éléments de la Sidebar ---
    const sidebarItems = document.querySelectorAll('.sidebar-item');
    const accueilCards = document.querySelectorAll('.accueil-card'); // Cartes sur la page d'accueil

    // --- Sections de Contenu ---
    const accueilSection = document.getElementById('accueil-section');
    const createRequestSection = document.getElementById('create-request-section');
    const viewStatusSection = document.getElementById('view-status-section');
    const syntheseSection = document.getElementById('synthese-section'); // Nouvelle section
    const logoutSection = document.getElementById('logout-section');

    // --- Éléments spécifiques au formulaire de demande ---
    const budgetRequestForm = document.getElementById('budget-request-form');
    const saveDraftBtn = document.getElementById('save-draft-btn');
    const submitRequestBtn = document.getElementById('submit-request-btn');
    const addItemBtn = document.getElementById('add-item-btn');
    const itemsContainer = document.getElementById('items-container');

    // --- Éléments spécifiques au statut des demandes ---
    const requestsTableBody = document.querySelector('#requests-table tbody');

    // --- Éléments spécifiques à la déconnexion ---
    const confirmLogoutBtn = document.getElementById('confirm-logout-btn');
    const cancelLogoutBtn = document.querySelector('.cancel-logout-btn'); // Bouton Annuler la déconnexion

    let itemCounter = 0; // Pour donner des IDs uniques aux articles

    // --- Fonctions utilitaires ---

    // Fonction pour masquer toutes les sections de fonctionnalité
    const hideAllFeatureSections = () => {
        const sections = document.querySelectorAll('.feature-section');
        sections.forEach(section => {
            section.classList.add('hidden');
        });
    };

    // Fonction pour désactiver l'état "actif" de tous les éléments de la sidebar
    const deactivateAllSidebarItems = () => {
        sidebarItems.forEach(item => {
            item.classList.remove('active');
        });
    };

    // Fonction pour afficher une section spécifique
    const showSection = (sectionId) => {
        hideAllFeatureSections();
        const targetSection = document.getElementById(`${sectionId}-section`);
        if (targetSection) {
            targetSection.classList.remove('hidden');
        }
    };

    // --- Gestion des clics sur les éléments de la sidebar ---
    sidebarItems.forEach(item => {
        item.addEventListener('click', () => {
            deactivateAllSidebarItems(); // Désactive tous les éléments
            item.classList.add('active'); // Active l'élément cliqué

            const sectionToShow = item.dataset.section;
            showSection(sectionToShow);

            // Actions spécifiques au chargement de la section
            if (sectionToShow === 'view-status') {
                loadRequestsStatus();
            } else if (sectionToShow === 'create-request') {
                // S'assurer que le formulaire est propre ou chargé si brouillon
                budgetRequestForm.reset();
                itemsContainer.innerHTML = '';
                itemCounter = 0;
            }
        });
    });

    // --- Gestion des clics sur les cartes d'accueil ---
    accueilCards.forEach(card => {
        card.addEventListener('click', () => {
            const sectionToShow = card.dataset.section;
            // Trouver l'élément de la sidebar correspondant et simuler un clic dessus
            const correspondingSidebarItem = document.querySelector(`.sidebar-item[data-section="${sectionToShow}"]`);
            if (correspondingSidebarItem) {
                correspondingSidebarItem.click(); // Simule un clic sur l'élément de la sidebar
            }
        });
    });

    // --- Logique du formulaire de création de demande (identique à précédemment) ---

    // Fonction pour ajouter une nouvelle ligne d'article
    const addItemEntry = () => {
        itemCounter++;
        const itemEntryDiv = document.createElement('div');
        itemEntryDiv.classList.add('item-entry');
        itemEntryDiv.dataset.itemId = itemCounter;

        itemEntryDiv.innerHTML = `
            <div class="form-group">
                <label for="item-name-${itemCounter}">Nom de l'article :</label>
                <input type="text" id="item-name-${itemCounter}" name="itemName-${itemCounter}" placeholder="Ex: Ordinateur portable" required>
            </div>
            <div class="form-group">
                <label for="item-quantity-${itemCounter}">Quantité :</label>
                <input type="number" id="item-quantity-${itemCounter}" name="itemQuantity-${itemCounter}" min="1" value="1" required>
            </div>
            <div class="form-group">
                <label for="item-unit-price-${itemCounter}">Prix unitaire (XOF) :</label>
                <input type="number" id="item-unit-price-${itemCounter}" name="itemUnitPrice-${itemCounter}" min="0" step="1" placeholder="Ex: 250000" required>
            </div>
            <button type="button" class="remove-item-btn" data-item-id="${itemCounter}">X</button>
        `;
        itemsContainer.appendChild(itemEntryDiv);
    };

    if (addItemBtn) {
        addItemBtn.addEventListener('click', addItemEntry);
    }

    if (itemsContainer) {
        itemsContainer.addEventListener('click', (event) => {
            if (event.target.classList.contains('remove-item-btn')) {
                const itemIdToRemove = event.target.dataset.itemId;
                const itemEntryToRemove = document.querySelector(`.item-entry[data-item-id="${itemIdToRemove}"]`);
                if (itemEntryToRemove) {
                    itemEntryToRemove.remove();
                }
            }
        });
    }

    // Simulation du processus d'enregistrement et de soumission (avec localStorage pour l'exemple)
    let requests = JSON.parse(localStorage.getItem('budgetRequests')) || [];
    // Assurez-vous que nextRequestId est basé sur les IDs existants après le chargement
    let nextRequestId = requests.length > 0 ? Math.max(...requests.map(r => r.id)) + 1 : 1;

    const saveRequest = async (status) => {
        const teacherName = document.getElementById('teacher-name').value; // Nouveau champ
        const title = document.getElementById('request-title').value;
        const category = document.getElementById('request-category').value;
        const description = document.getElementById('request-description').value;
        const amount = document.getElementById('requested-amount').value;

        if (!teacherName || !title || !category || !description || !amount) {
            alert("Veuillez remplir tous les champs obligatoires (Nom de l'enseignant, Intitulé, Catégorie, Description, Montant total estimé).");
            return null;
        }

        const items = [];
        let allItemsValid = true;
        document.querySelectorAll('.item-entry').forEach(itemDiv => {
            const itemId = itemDiv.dataset.itemId;
            const itemName = document.getElementById(`item-name-${itemId}`).value;
            const itemQuantity = document.getElementById(`item-quantity-${itemId}`).value;
            const itemUnitPrice = document.getElementById(`item-unit-price-${itemId}`).value;

            if (!itemName || !itemQuantity || !itemUnitPrice) {
                alert("Veuillez remplir tous les champs pour chaque article ajouté.");
                allItemsValid = false;
                return;
            }

            items.push({
                name: itemName,
                quantity: parseInt(itemQuantity),
                unitPrice: parseFloat(itemUnitPrice)
            });
        });

        if (!allItemsValid) {
            return null;
        }

        const requestData = {
            id: nextRequestId++,
            teacherName: teacherName, // Ajout du nom de l'enseignant
            title,
            category,
            description,
            amount: parseFloat(amount),
            items: items,
            status: status,
            submissionDate: new Date().toLocaleDateString('fr-FR', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit'
            }),
        };

        // --- Appel au backend (à décommenter en production) ---
        /*
        try {
            const response = await fetch('/api/requests', { // Assurez-vous que l'URL est correcte
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                },
                body: JSON.stringify(requestData),
            });
            const data = await response.json();
            if (response.ok) {
                alert(`Demande "${title}" ${status === 'Brouillon' ? 'sauvegardée en brouillon' : 'soumise'} avec succès !`);
                budgetRequestForm.reset();
                itemsContainer.innerHTML = '';
                itemCounter = 0;
                // Optionnel: Recharger la liste des demandes si on vient de soumettre
                // loadRequestsStatus();
            } else {
                alert(data.message || `Erreur lors de la ${status === 'Brouillon' ? 'sauvegarde en brouillon' : 'soumission'}.`);
            }
        } catch (error) {
            console.error("Erreur lors de l'envoi au backend:", error);
            alert("Une erreur de communication est survenue.");
        }
        */

        // Simulation avec localStorage:
        requests.push(requestData);
        localStorage.setItem('budgetRequests', JSON.stringify(requests));
        alert(`Demande "${title}" ${status === 'Brouillon' ? 'sauvegardée en brouillon' : 'soumise'} avec succès !`);
        budgetRequestForm.reset();
        itemsContainer.innerHTML = '';
        itemCounter = 0;
        return requestData;
    };

    if (saveDraftBtn) {
        saveDraftBtn.addEventListener('click', () => {
            saveRequest('Brouillon');
        });
    }

    if (budgetRequestForm) {
        budgetRequestForm.addEventListener('submit', (event) => {
            event.preventDefault();
            saveRequest('Soumise');
        });
    }

    // --- Logique de consultation du statut (identique à précédemment, avec simulation) ---
    const loadRequestsStatus = async () => {
        requestsTableBody.innerHTML = '<tr><td colspan="6">Chargement des demandes...</td></tr>';

        // --- Appel au backend (à décommenter en production) ---
        /*
        try {
            const response = await fetch('/api/my-requests', { // Assurez-vous que l'URL est correcte
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                }
            });
            const requests = await response.json();
            // ... Mettre à jour le tableau avec ces données ...
        } catch (error) {
            console.error("Erreur lors du chargement des demandes:", error);
            requestsTableBody.innerHTML = '<tr><td colspan="6">Erreur lors du chargement des demandes.</td></tr>';
        }
        */

        // Simulation avec localStorage:
        const currentRequests = JSON.parse(localStorage.getItem('budgetRequests')) || [];
        requestsTableBody.innerHTML = '';
        if (currentRequests.length === 0) {
            requestsTableBody.innerHTML = '<tr><td colspan="6">Aucune demande trouvée.</td></tr>';
            return;
        }

        currentRequests.forEach(request => {
            const row = requestsTableBody.insertRow();
            row.insertCell().textContent = request.id;
            row.insertCell().textContent = request.title;
            row.insertCell().textContent = request.amount.toLocaleString('fr-FR', { style: 'currency', currency: 'XOF' });
            row.insertCell().textContent = request.status;
            row.insertCell().textContent = request.submissionDate;

            const actionsCell = row.insertCell();
            if (request.status === 'Brouillon') {
                const editButton = document.createElement('button');
                editButton.textContent = 'Modifier';
                editButton.classList.add('btn', 'btn-secondary', 'small-btn'); // Ajoutez small-btn pour un style plus petit
                editButton.style.marginRight = '5px';
                editButton.addEventListener('click', () => {
                    alert(`Charger le brouillon ${request.id} pour modification (à implémenter: pré-remplir le formulaire).`);
                    // Implémentation réelle : charger les données du brouillon dans le formulaire
                    // puis basculer vers la section 'create-request'
                    // showSection('create-request');
                    // fillFormWithDraftData(request); // Fonction à créer pour pré-remplir
                });
                actionsCell.appendChild(editButton);
            }
            const viewDetailsButton = document.createElement('button');
            viewDetailsButton.textContent = 'Voir Détails';
            viewDetailsButton.classList.add('btn', 'btn-primary', 'small-btn'); // Ajoutez small-btn
            viewDetailsButton.addEventListener('click', () => {
                let details = `Détails de la demande ${request.id}:\n\nNom Enseignant: ${request.teacherName}\nTitre: ${request.title}\nDescription: ${request.description}\nMontant: ${request.amount.toLocaleString('fr-FR', { style: 'currency', currency: 'XOF'})}\nStatut: ${request.status}\nDate: ${request.submissionDate}\nCatégorie: ${request.category}\n\nArticles:\n`;
                if (request.items && request.items.length > 0) {
                    request.items.forEach(item => {
                        details += ` - ${item.name} (x${item.quantity}) @ ${item.unitPrice.toLocaleString('fr-FR', { style: 'currency', currency: 'XOF'})} = ${(item.quantity * item.unitPrice).toLocaleString('fr-FR', { style: 'currency', currency: 'XOF'})}\n`;
                    });
                } else {
                    details += "Aucun article détaillé.\n";
                }
                alert(details);
            });
            actionsCell.appendChild(viewDetailsButton);
        });
    };

    // --- Logique de déconnexion ---
    if (confirmLogoutBtn) {
        confirmLogoutBtn.addEventListener('click', () => {
            // Supprimer le token d'authentification ou les informations de session
            localStorage.removeItem('authToken');
            // Rediriger vers la page de connexion ou la page d'accueil
            window.location.href = 'index.html'; // Supposons que l'écran de sélection est index.html
            alert("Vous avez été déconnecté avec succès.");
        });
    }

    if (cancelLogoutBtn) {
        cancelLogoutBtn.addEventListener('click', () => {
            // Revenir à l'accueil
            document.querySelector('.sidebar-item[data-section="accueil"]').click();
        });
    }


    // --- Initialisation : afficher la section "Accueil" par défaut ---
    // Simule un clic sur l'élément "Accueil" de la sidebar au chargement de la page
    const initialSidebarItem = document.querySelector('.sidebar-item.active');
    if (initialSidebarItem) {
        initialSidebarItem.click();
    } else {
        // Fallback si aucun item n'est 'active' par défaut, afficher l'accueil
        showSection('accueil');
    }
});