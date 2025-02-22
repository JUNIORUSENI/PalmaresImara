from django.contrib import admin, messages
from django.shortcuts import redirect, render, HttpResponse
from django.urls import path
import pandas as pd
import decimal
from .models import RESULTAT, ELEVE, CLASSE, SECTION, ANNEE_SCOLAIRE
from .forms import CSVUploadForm
import io
import csv


admin.site.site_header = "Palmarès Administration"
admin.site.site_title = "Palmarès Administration"
admin.site.index_title = "Bienvenue dans l'administration des résultats"

admin.site.register (ANNEE_SCOLAIRE)
admin.site.register (SECTION)
admin.site.register (CLASSE)


@admin.register(ELEVE)
class EleveAdmin(admin.ModelAdmin):
    """Admin pour le modèle ELEVE."""
    list_display = ("nom", "post_nom", "prenom")
    search_fields = ("nom", "post_nom", "prenom")
    ordering = ("nom", "post_nom", "prenom")


EXPECTED_COLUMNS = [
    "Nom",
    "Postnom",
    "Prénom",
    "Pourcentage",
    "Section",
    "Classe",
    "Année scolaire",
]

REQUIRED_COLUMNS = [
    "Nom",
    "Classe",
    "Section",
    "Année scolaire",
]

@admin.register(RESULTAT)
class ResultatAdmin(admin.ModelAdmin):
    change_list_template = "admin/csv_upload.html"
    list_display = (
        "eleve_nom",
        "eleve_post_nom",
        "eleve_prenom",
        "pourcentage",
        "classe",
        "section",
        "annee_scolaire",
    )
    search_fields = (
        "eleve__nom",
        "eleve__post_nom",
        "eleve__prenom",
        "classe__nom_classe",
        "section__nom_section",
        "annee_scolaire__annee_scolaire",
    )
    list_filter = (
        "classe__nom_classe",
        "section__nom_section",
        "annee_scolaire__annee_scolaire",
    )
    ordering = ("eleve__nom", "classe")
    list_per_page = 5

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("import-csv/", self.import_csv, name="import_csv"),
            path("download-errors/", self.download_errors, name="download_errors"),
        ]
        return custom_urls + urls

    def import_csv(self, request):
        if request.method == "POST":
            form = CSVUploadForm(request.POST, request.FILES)
            if form.is_valid():
                uploaded_file = request.FILES["file"]
                try:
                    data = self.read_csv_file(uploaded_file)
                    actual_columns = set(data.columns)
                    expected_columns = set(EXPECTED_COLUMNS)

                    if actual_columns != expected_columns:
                        missing_in_file = expected_columns - actual_columns
                        extra_in_file = actual_columns - expected_columns
                        error_messages = []
                        if missing_in_file:
                            error_messages.append("Colonnes manquantes : " + ", ".join(missing_in_file))
                        if extra_in_file:
                            error_messages.append("Colonnes supplémentaires non attendues : " + ", ".join(extra_in_file))
                        raise ValueError(" ; ".join(error_messages))

                    for col in REQUIRED_COLUMNS:
                        if col not in data.columns:
                            raise ValueError(f"Colonne obligatoire manquante : {col}")

                    errors = []
                    for i, row in enumerate(data.to_dict(orient="records"), start=1):
                        try:
                            self.validate_row(row, i)
                            self.create_or_update_result(row)
                        except Exception as e:
                            errors.append(f"Ligne {i}: {e}")

                    # S'il n'y a aucune erreur, on renvoie l'utilisateur vers la liste
                    if not errors:
                        self.message_user(request, "Fichier importé avec succès.")
                        return redirect("..")

                    # S'il y a des erreurs, on les stocke en session, puis on rend une page spéciale
                    request.session["import_errors"] = errors
                    return render(request, "admin/import_errors.html", {
                        "title": "Erreurs d'import",
                        "errors": errors,
                    })

                except Exception as e:
                    messages.error(request, f"Erreur générale : {e}")
                    return redirect("..")
        else:
            form = CSVUploadForm()

        return render(
            request,
            "admin/csv_form.html",
            {"form": form, "title": "Importer un fichier CSV/Excel"},
        )

    def download_errors(self, request):
        errors = request.session.get("import_errors", [])
        output = io.StringIO()
        writer = csv.writer(output, delimiter=";")
        writer.writerow(["Erreur"])
        if errors:
            for err in errors:
                writer.writerow([err])
        else:
            writer.writerow(["Aucune erreur à signaler"])
        output.seek(0)
        response = HttpResponse(output, content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="erreurs_import.csv"'
        return response

    def read_csv_file(self, uploaded_file):
        if uploaded_file.name.lower().endswith(".xlsx"):
            return pd.read_excel(uploaded_file)
        elif uploaded_file.name.lower().endswith(".csv"):
            return pd.read_csv(uploaded_file, sep=";", encoding="utf-8-sig")
        else:
            raise ValueError("Format de fichier non pris en charge.")

    def validate_row(self, row, line_number):
        for col in REQUIRED_COLUMNS:
            raw_value = row.get(col)
            if pd.isnull(raw_value) or not str(raw_value).strip():
                raise ValueError(f"Le champ '{col}' est obligatoire.")

    def create_or_update_result(self, row):
        nom = row.get("Nom")
        post_nom = row.get("Postnom", "")
        prenom = row.get("Prénom", "")
        raw_pourcentage = row.get("Pourcentage", None)
        nom_classe = row.get("Classe")
        nom_section = row.get("Section")
        annee_raw = row.get("Année scolaire")

        nom = "" if pd.isnull(nom) else str(nom).strip()
        post_nom = "" if pd.isnull(post_nom) else str(post_nom).strip()
        prenom = "" if pd.isnull(prenom) else str(prenom).strip()
        nom_classe = "" if pd.isnull(nom_classe) else str(nom_classe).strip().upper()
        nom_section = "" if pd.isnull(nom_section) else str(nom_section).strip().upper()
        annee_raw = "" if pd.isnull(annee_raw) else str(annee_raw).strip().replace(" ", "")

        pourcentage = None
        if not pd.isnull(raw_pourcentage) and str(raw_pourcentage).strip():
            tmp_str = str(raw_pourcentage).strip()
            if "%" in tmp_str:
                try:
                    pourcentage = decimal.Decimal(tmp_str.replace("%", "").strip())
                except decimal.InvalidOperation:
                    pourcentage = None
            else:
                try:
                    pourcentage = decimal.Decimal(tmp_str)
                except decimal.InvalidOperation:
                    pourcentage = None

        annee, _ = ANNEE_SCOLAIRE.objects.get_or_create(annee_scolaire=annee_raw)
        section, _ = SECTION.objects.get_or_create(nom_section=nom_section)
        classe, _ = CLASSE.objects.get_or_create(nom_classe=nom_classe)
        eleve, _ = ELEVE.objects.get_or_create(nom=nom, post_nom=post_nom, prenom=prenom)
        RESULTAT.objects.update_or_create(
            eleve=eleve, classe=classe, section=section, annee_scolaire=annee,
            defaults={"pourcentage": pourcentage},
        )

    def eleve_nom(self, obj):
        return obj.eleve.nom

    def eleve_post_nom(self, obj):
        return obj.eleve.post_nom

    def eleve_prenom(self, obj):
        return obj.eleve.prenom