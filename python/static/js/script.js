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




// JavaScript pour pageprof.html
document.addEventListener('DOMContentLoaded', function() {
    // Variables globales
    let currentBrouillonId = null;
    let itemCounter = 0;

    // Gestion de la navigation
    const sidebarItems = document.querySelectorAll('.sidebar-item');
    const sections = document.querySelectorAll('.feature-section');
    const accueilCards = document.querySelectorAll('.accueil-card');

    // Navigation via sidebar
    sidebarItems.forEach(item => {
        item.addEventListener('click', function() {
            const targetSection = this.dataset.section;
            if (targetSection && targetSection !== 'logout') {
                showSection(targetSection);
                updateActiveMenuItem(this);
            }
        });
    });

    // Navigation via cartes d'accueil
    accueilCards.forEach(card => {
        card.addEventListener('click', function() {
            const targetSection = this.dataset.section;
            if (targetSection) {
                showSection(targetSection);
                updateActiveMenuItem(document.querySelector(`.sidebar-item[data-section="${targetSection}"]`));
            }
        });
    });

    function showSection(sectionName) {
        sections.forEach(section => {
            section.classList.add('hidden');
        });
        
        const targetSection = document.getElementById(sectionName + '-section');
        if (targetSection) {
            targetSection.classList.remove('hidden');
            
            // Charger les données spécifiques à la section
            if (sectionName === 'view-status') {
                chargerDemandes();
            } else if (sectionName === 'synthese') {
                chargerStatistiques();
            }
        }
    }

    function updateActiveMenuItem(activeItem) {
        sidebarItems.forEach(item => {
            item.classList.remove('active');
        });
        if (activeItem) {
            activeItem.classList.add('active');
        }
    }

    // Gestion du formulaire de demande
    const form = document.getElementById('budget-request-form');
    const addItemBtn = document.getElementById('add-item-btn');
    const itemsContainer = document.getElementById('items-container');
    const saveDraftBtn = document.getElementById('save-draft-btn');
    const submitBtn = document.getElementById('submit-request-btn');

    // Ajouter un article
    addItemBtn.addEventListener('click', function() {
        ajouterArticle();
    });

    function ajouterArticle() {
        itemCounter++;
        const itemHtml = `
            <div class="item-row" data-item-id="${itemCounter}">
                <div class="item-inputs">
                    <input type="text" name="itemName[]" placeholder="Nom de l'article" required>
                    <input type="number" name="itemQuantity[]" placeholder="Quantité" min="1" required>
                    <input type="number" name="itemPrice[]" placeholder="Prix unitaire" min="0" step="0.01" required>
                    <span class="item-total">Total: 0 XOF</span>
                </div>
                <button type="button" class="btn btn-danger small-btn remove-item-btn">Supprimer</button>
            </div>
        `;
        itemsContainer.insertAdjacentHTML('beforeend', itemHtml);
        
        // Ajouter les event listeners pour le nouvel article
        const newItem = itemsContainer.lastElementChild;
        const removeBtn = newItem.querySelector('.remove-item-btn');
        const quantityInput = newItem.querySelector('input[name="itemQuantity[]"]');
        const priceInput = newItem.querySelector('input[name="itemPrice[]"]');
        const totalSpan = newItem.querySelector('.item-total');

        removeBtn.addEventListener('click', function() {
            newItem.remove();
            calculerMontantTotal();
        });

        // Calculer le total de l'article
        function updateItemTotal() {
            const quantity = parseFloat(quantityInput.value) || 0;
            const price = parseFloat(priceInput.value) || 0;
            const total = quantity * price;
            totalSpan.textContent = `Total: ${total.toLocaleString('fr-FR')} XOF`;
            calculerMontantTotal();
        }

        quantityInput.addEventListener('input', updateItemTotal);
        priceInput.addEventListener('input', updateItemTotal);
    }

    function calculerMontantTotal() {
        const quantities = document.querySelectorAll('input[name="itemQuantity[]"]');
        const prices = document.querySelectorAll('input[name="itemPrice[]"]');
        let total = 0;

        for (let i = 0; i < quantities.length; i++) {
            const quantity = parseFloat(quantities[i].value) || 0;
            const price = parseFloat(prices[i].value) || 0;
            total += quantity * price;
        }

        const amountInput = document.getElementById('requested-amount');
        if (total > 0) {
            amountInput.value = total;
        }
    }

    // Sauvegarder en brouillon
    saveDraftBtn.addEventListener('click', function() {
        sauvegarderBrouillon();
    });

    function sauvegarderBrouillon() {
        const formData = new FormData(form);
        const data = {
            teacherName: formData.get('teacherName'),
            title: formData.get('title'),
            category: formData.get('category'),
            description: formData.get('description'),
            amount: formData.get('amount'),
            articles: getArticlesData(),
            brouillon_id: currentBrouillonId
        };

        fetch('/sauvegarder_brouillon', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                currentBrouillonId = data.brouillon_id;
                showNotification('Brouillon sauvegardé avec succès', 'success');
            } else {
                showNotification(data.message || 'Erreur lors de la sauvegarde', 'error');
            }
        })
        .catch(error => {
            console.error('Erreur:', error);
            showNotification('Erreur de connexion', 'error');
        });
    }

    // Soumettre la demande
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        soumettredemande();
    });

    function soumettredemande() {
        const formData = new FormData(form);
        
        fetch('/creer_demande', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification('Demande créée avec succès', 'success');
                form.reset();
                itemsContainer.innerHTML = '';
                currentBrouillonId = null;
                itemCounter = 0;
            } else {
                showNotification(data.message || 'Erreur lors de la création', 'error');
            }
        })
        .catch(error => {
            console.error('Erreur:', error);
            showNotification('Erreur de connexion', 'error');
        });
    }

    function getArticlesData() {
        const articles = [];
        const itemRows = document.querySelectorAll('.item-row');
        
        itemRows.forEach(row => {
            const name = row.querySelector('input[name="itemName[]"]').value;
            const quantity = row.querySelector('input[name="itemQuantity[]"]').value;
            const price = row.querySelector('input[name="itemPrice[]"]').value;
            
            if (name && quantity && price) {
                articles.push({
                    nom: name,
                    quantite: parseInt(quantity),
                    prix_unitaire: parseFloat(price),
                    prix_total: parseInt(quantity) * parseFloat(price)
                });
            }
        });
        
        return articles;
    }

    // Charger les demandes
    function chargerDemandes() {
        fetch('/consulter_demandes')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                afficherDemandes(data.demandes);
            } else {
                showNotification(data.message || 'Erreur lors du chargement', 'error');
            }
        })
        .catch(error => {
            console.error('Erreur:', error);
            showNotification('Erreur de connexion', 'error');
        });
    }

    function afficherDemandes(demandes) {
        const tbody = document.querySelector('#requests-table tbody');
        tbody.innerHTML = '';

        demandes.forEach(demande => {
            const row = document.createElement('tr');
            
            const statutClass = getStatutClass(demande.statut);
            const dateCreation = new Date(demande.date_creation).toLocaleDateString('fr-FR');
            
            row.innerHTML = `
                <td>${demande.id}</td>
                <td>${demande.titre_demande}</td>
                <td>${demande.montant_total.toLocaleString('fr-FR')} XOF</td>
                <td><span class="status ${statutClass}">${getStatutText(demande.statut)}</span></td>
                <td>${dateCreation}</td>
                <td>
                    <button class="btn btn-sm btn-info" onclick="voirDetails(${demande.id})">Voir</button>
                    ${demande.statut === 'brouillon' ? `<button class="btn btn-sm btn-warning" onclick="modifierBrouillon(${demande.id})">Modifier</button>` : ''}
                    ${demande.statut === 'brouillon' ? `<button class="btn btn-sm btn-danger" onclick="supprimerBrouillon(${demande.id})">Supprimer</button>` : ''}
                </td>
            `;
            
            tbody.appendChild(row);
        });
    }

    function getStatutClass(statut) {
        switch(statut) {
            case 'en_attente': return 'pending';
            case 'approuve_chef': return 'approved';
            case 'rejete_chef': return 'rejected';
            case 'approuve_final': return 'approved';
            case 'rejete_final': return 'rejected';
            case 'brouillon': return 'draft';
            default: return 'pending';
        }
    }

    function getStatutText(statut) {
        switch(statut) {
            case 'en_attente': return 'En attente';
            case 'approuve_chef': return 'Approuvé par le chef';
            case 'rejete_chef': return 'Rejeté par le chef';
            case 'approuve_final': return 'Approuvé final';
            case 'rejete_final': return 'Rejeté final';
            case 'brouillon': return 'Brouillon';
            default: return 'Statut inconnu';
        }
    }

    // Charger les statistiques
    function chargerStatistiques() {
        fetch('/obtenir_statistiques')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                afficherStatistiques(data.statistiques);
            } else {
                showNotification(data.message || 'Erreur lors du chargement des statistiques', 'error');
            }
        })
        .catch(error => {
            console.error('Erreur:', error);
            showNotification('Erreur de connexion', 'error');
        });
    }

    function afficherStatistiques(stats) {
        const syntheseSection = document.getElementById('synthese-section');
        const placeholderContent = syntheseSection.querySelector('.placeholder-content');
        
        placeholderContent.innerHTML = `
            <div class="stats-grid">
                <div class="stat-card">
                    <h3>Total des demandes</h3>
                    <p class="stat-number">${stats.total_demandes}</p>
                </div>
                <div class="stat-card">
                    <h3>Montant total</h3>
                    <p class="stat-number">${stats.total_montant.toLocaleString('fr-FR')} XOF</p>
                </div>
            </div>
            <div class="stats-details">
                <h3>Répartition par statut</h3>
                <div class="stats-list">
                    ${Object.entries(stats.stats_statut).map(([statut, data]) => `
                        <div class="stat-item">
                            <span>${getStatutText(statut)}</span>
                            <span>${data.count} demandes (${data.montant.toLocaleString('fr-FR')} XOF)</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    // Notification system
    function showNotification(message, type) {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            border-radius: 5px;
            color: white;
            font-weight: bold;
            z-index: 1000;
            ${type === 'success' ? 'background-color: #4CAF50;' : 'background-color: #f44336;'}
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }

    // Fonctions globales pour les boutons
    window.voirDetails = function(id) {
        // Implémenter la modal pour voir les détails
        console.log('Voir détails de la demande:', id);
    };

    window.modifierBrouillon = function(id) {
        // Charger le brouillon dans le formulaire
        fetch(`/charger_brouillon?id=${id}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const brouillon = data.brouillon;
                
                // Remplir le formulaire
                document.getElementById('teacher-name').value = brouillon.nom_demandeur || '';
                document.getElementById('request-title').value = brouillon.titre_demande || '';
                document.getElementById('request-category').value = brouillon.categorie || '';
                document.getElementById('request-description').value = brouillon.description || '';
                document.getElementById('requested-amount').value = brouillon.montant_total || '';
                
                // Charger les articles
                itemsContainer.innerHTML = '';
                if (brouillon.articles && brouillon.articles.length > 0) {
                    brouillon.articles.forEach(article => {
                        ajouterArticle();
                        const lastItem = itemsContainer.lastElementChild;
                        lastItem.querySelector('input[name="itemName[]"]').value = article.nom;
                        lastItem.querySelector('input[name="itemQuantity[]"]').value = article.quantite;
                        lastItem.querySelector('input[name="itemPrice[]"]').value = article.prix_unitaire;
                    });
                }
                
                currentBrouillonId = id;
                showSection('create-request');
                updateActiveMenuItem(document.querySelector('.sidebar-item[data-section="create-request"]'));
                
                showNotification('Brouillon chargé avec succès', 'success');
            } else {
                showNotification(data.message || 'Erreur lors du chargement', 'error');
            }
        })
        .catch(error => {
            console.error('Erreur:', error);
            showNotification('Erreur de connexion', 'error');
        });
    };

    window.supprimerBrouillon = function(id) {
        if (confirm('Êtes-vous sûr de vouloir supprimer ce brouillon ?')) {
            fetch('/supprimer_brouillon', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({id: id})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showNotification('Brouillon supprimé avec succès', 'success');
                    chargerDemandes();
                } else {
                    showNotification(data.message || 'Erreur lors de la suppression', 'error');
                }
            })
            .catch(error => {
                console.error('Erreur:', error);
                showNotification('Erreur de connexion', 'error');
            });
        }
    };

    // Initialisation
    showSection('accueil');
});