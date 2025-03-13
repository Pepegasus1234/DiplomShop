from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from .models import User, Product, Review, Shop

class BuyerRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Логин'
        self.fields['first_name'].label = 'Имя'
        self.fields['last_name'].label = 'Фамилия'
        self.fields['email'].label = 'E-mail'
        self.fields['password1'].label = 'Пароль'
        self.fields['password2'].label = 'Подтвердите пароль'

class SellerRegistrationForm(UserCreationForm):
    inn = forms.CharField(max_length=12, label="ИНН")

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'inn', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Логин'
        self.fields['first_name'].label = 'Имя'
        self.fields['last_name'].label = 'Фамилия'
        self.fields['email'].label = 'E-mail'
        self.fields['password1'].label = 'Пароль'
        self.fields['password2'].label = 'Подтвердите пароль'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'seller'
        if commit:
            user.save()
        return user

class LoginForm(forms.Form):
    username = forms.CharField(label="Логин")
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")
    inn = forms.CharField(max_length=12, required=False, label="ИНН (для продавцов)")


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'size', 'color', 'price', 'quantity', 'description', 'image1', 'image2']


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'gender', 'phone']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].label = 'Имя'
        self.fields['last_name'].label = 'Фамилия'
        self.fields['email'].label = 'E-mail'
        self.fields['gender'].label = 'Пол'
        self.fields['phone'].label = 'Номер телефона'


class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].label = 'Текущий пароль'
        self.fields['new_password1'].label = 'Новый пароль'
        self.fields['new_password2'].label = 'Подтвердите новый пароль'


class ShopInfoForm(forms.ModelForm):
    class Meta:
        model = Shop
        fields = ['name', 'email']
        labels = {
            'name': 'Название магазина',
            'email': 'Email'
        }

class AddManagerForm(forms.ModelForm):
    username = forms.ModelChoiceField(
        queryset=User.objects.filter(role='buyer'),
        empty_label="Выберите пользователя",
        label="Логин пользователя"
    )

    class Meta:
        model = User
        fields = ['username']