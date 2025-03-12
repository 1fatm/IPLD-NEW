document.addEventListener("DOMContentLoaded", function () {
    // Cacher toutes les sections au chargement de la page
    const sections = document.querySelectorAll(".main-content section");
    sections.forEach(section => section.style.display = "none");

    // Afficher la section "Accueil" par défaut
    const defaultSection = document.querySelector("#home");
    if (defaultSection) {
        defaultSection.style.display = "block";
    }

    // Gérer les clics sur les liens du menu
    const navLinks = document.querySelectorAll(".sidebar a");
    navLinks.forEach(link => {
        link.addEventListener("click", function (e) {
            e.preventDefault(); // Empêcher le comportement par défaut du lien

            // Cacher toutes les sections
            sections.forEach(section => section.style.display = "none");

            // Afficher la section correspondante
            const target = this.getAttribute("data-target");
            const targetSection = document.querySelector(`#${target}`);
            if (targetSection) {
                targetSection.style.display = "block";
            }
        });
    });

    // Gestion du chatbot
    const chatbotWindow = document.getElementById("chatbotWindow");
    const openChatbotButton = document.getElementById("openChatbot");
    const closeChatbotButton = document.getElementById("closeChatbot");
    const sendMessageButton = document.getElementById("sendMessage");
    const chatbotInput = document.getElementById("chatbotInput");
    const chatbotMessages = document.getElementById("chatbotMessages");

    if (chatbotWindow && openChatbotButton && closeChatbotButton && sendMessageButton && chatbotInput && chatbotMessages) {
        // Ouvrir le chatbot
        openChatbotButton.addEventListener("click", function () {
            chatbotWindow.style.display = "flex";
            openChatbotButton.style.display = "none";
        });

        // Fermer le chatbot
        closeChatbotButton.addEventListener("click", function () {
            chatbotWindow.style.display = "none";
            openChatbotButton.style.display = "block";
        });

        // Envoyer un message
        sendMessageButton.addEventListener("click", function () {
            const messageText = chatbotInput.value.trim();
            if (messageText !== "") {
                // Ajouter le message de l'utilisateur
                const userMessage = document.createElement("div");
                userMessage.classList.add("message", "user-message");
                userMessage.textContent = messageText;
                chatbotMessages.appendChild(userMessage);

                // Réponse du bot (simulée)
                setTimeout(function () {
                    const botMessage = document.createElement("div");
                    botMessage.classList.add("message", "bot-message");
                    botMessage.textContent = "Merci pour votre message !";
                    chatbotMessages.appendChild(botMessage);

                    // Faire défiler vers le bas
                    chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
                }, 1000);

                // Effacer le champ de saisie
                chatbotInput.value = "";
            }
        });

        // Envoyer un message avec la touche Entrée
        chatbotInput.addEventListener("keypress", function (e) {
            if (e.key === "Enter") {
                sendMessageButton.click();
            }
        });
    }
});
