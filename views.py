from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from .models import Expense, Category
from .forms import ExpenseForm, CategoryForm, FilterForm
from django.db.models import Sum, Q
import datetime

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created! Please log in.")
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'expenses/signup.html', {'form': form})

@login_required
def dashboard(request):
    today = datetime.date.today()
    current_month = today.month
    current_year = today.year
    expenses = Expense.objects.filter(user=request.user, date__month=current_month, date__year=current_year)
    total = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    # Category-wise chart data
    chart_data = expenses.values('category__name').annotate(total=Sum('amount'))
    return render(request, 'expenses/dashboard.html', {
        'total': total,
        'chart_data': chart_data,
        'month': today.strftime("%B"),
        'year': current_year
    })

@login_required
def expense_list(request):
    expenses = Expense.objects.filter(user=request.user).order_by('-date')
    filter_form = FilterForm(request.GET or None)
    if filter_form.is_valid():
        start = filter_form.cleaned_data.get('start_date')
        end = filter_form.cleaned_data.get('end_date')
        cat = filter_form.cleaned_data.get('category')
        search = filter_form.cleaned_data.get('search')
        if start:
            expenses = expenses.filter(date__gte=start)
        if end:
            expenses = expenses.filter(date__lte=end)
        if cat:
            expenses = expenses.filter(category=cat)
        if search:
            expenses = expenses.filter(Q(title__icontains=search) | Q(note__icontains=search))
    return render(request, 'expenses/expense_list.html', {'expenses': expenses, 'filter_form': filter_form})

@login_required
def expense_detail(request, pk):
    exp = get_object_or_404(Expense, pk=pk, user=request.user)
    return render(request, 'expenses/expense_detail.html', {'expense': exp})

@login_required
def add_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES)
        if form.is_valid():
            exp = form.save(commit=False)
            exp.user = request.user
            exp.save()
            messages.success(request, "Expense added!")
            return redirect('expense_list')
    else:
        form = ExpenseForm()
    return render(request, 'expenses/expense_form.html', {'form': form, 'action': 'Add Expense'})

@login_required
def edit_expense(request, pk):
    exp = get_object_or_404(Expense, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES, instance=exp)
        if form.is_valid():
            form.save()
            messages.success(request, "Expense updated!")
            return redirect('expense_list')
    else:
        form = ExpenseForm(instance=exp)
    return render(request, 'expenses/expense_form.html', {'form': form, 'action': 'Edit Expense'})

@login_required
def delete_expense(request, pk):
    exp = get_object_or_404(Expense, pk=pk, user=request.user)
    if request.method == 'POST':
        exp.delete()
        messages.success(request, "Expense deleted!")
        return redirect('expense_list')
    return render(request, 'expenses/expense_confirm_delete.html', {'expense': exp})

@login_required
def add_category(request):
    form = CategoryForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Category added!")
        return redirect('expense_list')
    return render(request, 'expenses/category_form.html', {'form': form})
