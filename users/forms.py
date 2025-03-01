from django import forms
from django.contrib.auth.forms import AuthenticationForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit
from .models import Profile


class LoginUserForm(AuthenticationForm):
    username = forms.CharField(
        label='Логин',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )
    remember_me = forms.BooleanField(
        label="Запомнить меня",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        initial=True  # Можно включить по умолчанию
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('username'),
            Field('password'),
            Field('remember_me'),  # Добавить поле в разметку
        )
        self.helper.add_input(Submit('submit', 'Войти'))


class EditPasswordForm(forms.ModelForm):
    new_password = forms.CharField(
        label='Новый пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-input'}),
        min_length=8,
    )
    confirm_password = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput(attrs={'class': 'form-input'}),
        min_length=8,
    )

    class Meta:
        model = Profile
        fields = []  # Если вам не нужны поля модели, оставьте пустым

    def __init__(self, *args, **kwargs):
        super(EditPasswordForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Изменить пароль'))  # Кнопка отправки
        self.helper.layout = Layout(
            Field('new_password'),  # Поле нового пароля
            Field('confirm_password'),  # Поле подтверждения пароля
        )
    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if new_password and confirm_password and new_password != confirm_password:
            raise forms.ValidationError("Пароли не совпадают!")
        
        return cleaned_data

