from django.db import models


class ELEVE(models.Model):
    """Modèle regroupant toutes les informations d'élèves."""
    nom = models.CharField(max_length=30, verbose_name="Nom", blank=False, null=False, db_index=True)
    post_nom = models.CharField(max_length=30, verbose_name="Post-nom", blank=True, null=True)
    prenom = models.CharField(max_length=30, verbose_name="Prénom", blank=True, null=True)

    class Meta:
        db_table = "table_eleve"
        verbose_name = "Élève"
        verbose_name_plural = "Élèves"

    def __str__(self):
        return f"{self.nom} {self.post_nom} {self.prenom}"


class ANNEE_SCOLAIRE(models.Model):
    """Modèle regroupant les années scolaires."""
    annee_scolaire = models.CharField(max_length=9, unique=True, verbose_name="Année scolaire", blank=False, null=False)

    class Meta:
        db_table = "table_annee_scolaire"
        verbose_name = "Année scolaire"
        verbose_name_plural = "Années scolaires"

    def __str__(self):
        return self.annee_scolaire


class SECTION(models.Model):
    """Modèle regroupant les sections (ex : secondaire, primaire, etc.)."""
    nom_section = models.CharField(max_length=50, verbose_name="Nom de la section", blank=False, null=False)

    class Meta:
        db_table = "table_section"
        verbose_name = "Section"
        verbose_name_plural = "Sections"
        constraints = [
            models.UniqueConstraint(fields=['nom_section'], name="unique_section")
        ]

    def __str__(self):
        return f"{self.nom_section}"


class CLASSE(models.Model):
    """Modèle regroupant les classes avec sections et années scolaires."""
    nom_classe = models.CharField(max_length=50, verbose_name="Nom de la classe", blank=False, null=False)

    class Meta:
        db_table = "table_classe"
        verbose_name = "Classe"
        verbose_name_plural = "Classes"
        constraints = [
            models.UniqueConstraint(fields=['nom_classe'], name="unique_classe")
        ]

    def __str__(self):
        return f"{self.nom_classe}"


class RESULTAT(models.Model):
    """Modèle regroupant les résultats des élèves."""
    eleve = models.ForeignKey(
        ELEVE, on_delete=models.CASCADE, related_name="resultats", verbose_name="Élève"
    )
    pourcentage = models.DecimalField(
        max_digits=4, decimal_places=2, verbose_name="Pourcentage", blank=True, null=True
    )
    classe = models.ForeignKey(
        CLASSE, on_delete=models.CASCADE, related_name="resultats_classe", verbose_name="Classe", blank=False, null=False
    )
    section = models.ForeignKey(
        SECTION, on_delete=models.CASCADE, related_name="resultats_section", verbose_name="Section", blank=False, null=False
    )
    annee_scolaire = models.ForeignKey(
        ANNEE_SCOLAIRE, on_delete=models.CASCADE, related_name="resultats_annee", verbose_name="Année scolaire", blank=False, null=False
    )

    class Meta:
        db_table = "table_resultat"
        verbose_name = "Résultat"
        verbose_name_plural = "Résultats"
        constraints = [
            models.UniqueConstraint(
                fields=['eleve', 'classe', 'section', 'annee_scolaire'],
                name="unique_resultat"
            )
        ]

    def __str__(self):
        return f"{self.eleve.nom} {self.eleve.post_nom} {self.eleve.prenom} - {self.classe.nom_classe} ({self.section.nom_section}, {self.annee_scolaire})"
