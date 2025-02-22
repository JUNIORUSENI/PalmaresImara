from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.template.loader import render_to_string
from .forms import LoginForm
from .models import RESULTAT, ANNEE_SCOLAIRE, SECTION, CLASSE, ELEVE


def login_view(request):
    """Gérer l'authentification de l'utilisateur."""
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('recherche')
            else:
                form.add_error(None, "Nom d'utilisateur ou mot de passe incorrect.")
    else:
        form = LoginForm()

    return render(request, 'palmares/login.html', {'form': form})


@login_required
def recherche(request):
    """Vue pour rechercher des résultats d'élèves."""
    query_params = request.GET
    nom = query_params.get('nom', '').strip()
    post_nom = query_params.get('post_nom', '').strip()
    prenom = query_params.get('prenom', '').strip()
    annee_scolaire = query_params.get('annee_scolaire', '').strip()
    section = query_params.get('section', '').strip()
    classe = query_params.get('classe', '').strip()

    # -> Détecter si au moins un champ est rempli
    search_done = any([
        nom, post_nom, prenom,
        annee_scolaire, section, classe
    ])

    # Si aucun critère => on peut renvoyer la page SANS faire de requête,
    # et SANS afficher "Aucun résultat trouvé"
    if not search_done:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # Pour l'AJAX, on peut renvoyer un HTML partiel vide ou un msg d'erreur
            return JsonResponse({'html': ''})
        return render(request, 'palmares/recherche.html', {
            # On ne passe pas de resultats => pas de table
            # Mais on passe search_done=False pour masquer "Aucun résultat trouvé"
            'search_done': False,
            'annees': ANNEE_SCOLAIRE.objects.all(),
            'sections': SECTION.objects.all(),
            'classes': CLASSE.objects.all(),
        })

    # Sinon => on fait le filtrage des résultats
    resultats = RESULTAT.objects.select_related('eleve', 'classe', 'section', 'annee_scolaire')
    if nom:
        resultats = resultats.filter(eleve__nom__icontains=nom)
    if post_nom:
        resultats = resultats.filter(eleve__post_nom__icontains=post_nom)
    if prenom:
        resultats = resultats.filter(eleve__prenom__icontains=prenom)
    if annee_scolaire:
        resultats = resultats.filter(annee_scolaire__annee_scolaire=annee_scolaire)
    if section:
        resultats = resultats.filter(section__nom_section__icontains=section)
    if classe:
        resultats = resultats.filter(classe__nom_classe__icontains=classe)

    # Pagination
    paginator = Paginator(resultats, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Requête AJAX => on renvoie du JSON (HTML partiel inclus)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('palmares/resultats_partial.html', {
            'resultats': page_obj,
            'search_done': True,   # puisqu'on est en train de filtrer
        })
        return JsonResponse({'html': html})

    # Sinon, rendu normal (chargement de la page)
    return render(request, 'palmares/recherche.html', {
        'resultats': page_obj,
        'search_done': True,
        'annees': ANNEE_SCOLAIRE.objects.all(),
        'sections': SECTION.objects.all(),
        'classes': CLASSE.objects.all(),
    })


@login_required
def charger_sections_classes(request):
    """Charger dynamiquement les sections et les classes en fonction de l'année scolaire, via RESULTAT."""
    annee_scolaire = request.GET.get('annee_scolaire', None)
    section = request.GET.get('section', None)

    if not annee_scolaire:
        return JsonResponse({'error': "Année scolaire non spécifiée."}, status=400)

    # 1) Sélectionner toutes les sections qui ont au moins un résultat pour cette année scolaire
    sections = SECTION.objects.filter(
        resultats_section__annee_scolaire__annee_scolaire=annee_scolaire
    ).distinct()

    # 2) Sélectionner toutes les classes si une section est spécifiée
    if section:
        # On filtre sur la même année + la section
        classes = CLASSE.objects.filter(
            resultats_classe__annee_scolaire__annee_scolaire=annee_scolaire,
            resultats_classe__section__nom_section=section
        ).distinct()
    else:
        # Pas de section spécifiée => on renvoie un tableau vide ou rien du tout
        classes = []

    return JsonResponse({
        'sections': [
            {'id': sec.id, 'nom_section': sec.nom_section} 
            for sec in sections
        ],
        'classes': [
            {'id': cls.id, 'nom_classe': cls.nom_classe} 
            for cls in classes
        ],
    })
