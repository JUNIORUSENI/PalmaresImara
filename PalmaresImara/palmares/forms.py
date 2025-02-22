from django import forms

class LoginForm(forms.Form):
    username = forms.CharField(
        label="Nom d'utilisateur",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': "Nom d'utilisateur"
        })
    )
    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mot de passe'
        })
    )


class CSVUploadForm(forms.Form):
    file = forms.FileField(
        label="Fichier CSV",
        help_text="Téléchargez un fichier CSV contenant les colonnes : Nom, Postnom, Prénom, Pourcentage, Classe, Section, Année scolaire."
    )
