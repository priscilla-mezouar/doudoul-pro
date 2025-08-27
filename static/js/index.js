window.addEventListener("DOMContentLoaded", () => {
    const flashMessages = document.getElementById("flash-messages");
    if (flashMessages) {
        setTimeout(() => {
            flashMessages.style.transition = "opacity 0.5s ease";
            flashMessages.style.opacity = "0";
            // Après la transition, supprimer complètement l'élément
            setTimeout(() => {
                flashMessages.remove();
            }, 500); // durée = durée de la transition
        }, 3000); // délai avant disparition
    }
});