function chargerEmploiDuTemps() {
    var nom_enseignant = "{{ nom_enseignant }}";
    var semaine = $("#date_semaine").val();

    $.ajax({
        url: "/cours_enseignant_par_semaine/" + nom_enseignant + "/" + semaine,
        method: "GET",
        success: function(data) {
            afficherEmploiDuTemps(data);
        },
        error: function(error) {
            console.error("Erreur lors de la récupération des cours :", error);
        }
    });
}

function afficherEmploiDuTemps(cours_semaine) {
    var events = [];

    $.each(cours_semaine, function(semaine, coursList) {
        $.each(coursList, function(index, coursInfo) {
            var event = {
                title: coursInfo['Activite'],
                start: coursInfo['Jour'],
                description: `
                    Code Cours: ${coursInfo['Code_cours']}<br>
                    Durée: ${coursInfo['Duree']}<br>
                    Début: ${coursInfo['Debut']}<br>
                    Fin: ${coursInfo['Fin']}<br>
                    Salle: ${coursInfo['Salle']}<br>
                    Type de cours: ${coursInfo['Type_cours']}<br>
                    Groupe TD: ${coursInfo['Groupe_TD']}<br>
                    Niveau d'étude: ${coursInfo['Niveau_etude']}<br>
                ` 
            };
            events.push(event);
        });
    });

    // Initialisez le calendrier FullCalendar
    $('#calendar').fullCalendar({
        header: {
            left: 'prev,next today',
            center: 'title',
            right: 'month,agendaWeek,agendaDay'
        },
        events: events,
        eventRender: function(event, element) {
            element.qtip({
                content: event.description, // Utilisez la description comme contenu de l'info-bulle
                style: {
                    classes: 'qtip-bootstrap' // Utilisez le thème Bootstrap pour l'info-bulle
                }
            });
        }
    });
}

$(document).ready(function() {
    chargerEmploiDuTemps();
});
