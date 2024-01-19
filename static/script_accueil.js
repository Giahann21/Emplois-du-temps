document.addEventListener("DOMContentLoaded", function () {
    const citations = document.querySelectorAll('.citation');
    let index = 0;
    function afficherCitation() {
        citations[index].style.display = 'inline';
        setTimeout(cacherCitation, 3000); // Contrôle le temps d'affichage de chaque citation
    }
    function cacherCitation() {
        citations[index].style.display = 'none';
        index = (index + 1) % citations.length;
        afficherCitation();
    }
    afficherCitation();
});