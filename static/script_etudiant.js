function updateGroupesTD() {
    var niveauSelect = document.getElementById("niveau_etude");
    var groupeSelect = document.getElementById("groupe_td");
    groupeSelect.innerHTML = "";

    var selectedNiveau = niveauSelect.options[niveauSelect.selectedIndex].value;
    var groupes = {
        'L1': ['TD06 - MIASHS + Bessières Maths', 'TD07 - MIASHS', 'TD08 - MIASHS (et Oui, si)', 'TD09 - DL Economie-Maths', 'TD10 - DL Gestion-Info', 'TD11 - Economie-Gestion CMI'],
        'L2': ['TD06 - MIASHS (Maths Appliquées) + Bessières', 'TD07 - DL Économie-Maths', 'TD08 - MIASHS parcours MIAGE', 'TD09 - MIASHS parcours MIAGE', 'TD10 - DL Gestion-Informatique', 'TD11 - Économie-Gestion CMI'],
        'L3': ['TD1 - L3 MIAGE CLA', 'TD2 - L3 MIAGE CLA', 'TD3 - DL Info-Gestion', 'TD03 - CMI']
    }
    if (groupes && groupes[selectedNiveau]) {
        groupes[selectedNiveau].forEach(function (groupe) {
            var option = document.createElement("option");
            option.value = groupe;
            option.text = groupe;
            groupeSelect.add(option);
        });
    }
}
