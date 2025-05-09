document.addEventListener("DOMContentLoaded", function () {
    const niveauxTd = {
        "L1": ["TD06", "TD07", "TD08", "TD09", "TD10", "TD11"],
        "L2": ["TD06", "TD07", "TD08", "TD09", "TD10", "TD11", "OG3"],
        "L3": ["TD1", "TD2", "TD03A", "TD03B"]
    };

    const selectNiveau = document.getElementById("niveau_etude");
    const selectGroupe = document.getElementById("groupe_td");

    function updateGroupesTD() {
        const niveau = selectNiveau.value;
        const groupes = niveauxTd[niveau] || [];

        // Sauvegarder la sélection précédente
        const previous = selectGroupe.value;

        // Réinitialiser les options
        selectGroupe.innerHTML = "";

        groupes.forEach(code => {
            const option = document.createElement("option");
            option.value = code;
            option.textContent = code;
            if (code === previous) {
                option.selected = true;
            }
            selectGroupe.appendChild(option);
        });
    }

    // Déclenche au chargement de la page
    if (selectNiveau && selectGroupe) {
        updateGroupesTD();
        selectNiveau.addEventListener("change", updateGroupesTD);
    }
});