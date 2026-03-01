from django import forms
from .models import Expense, Category

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['title', 'amount', 'category', 'note', 'date', 'receipt']

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']

class FilterForm(forms.Form):
    start_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=False)
    search = forms.CharField(required=False, label='Search by title/note')
