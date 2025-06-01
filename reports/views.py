from django.shortcuts import render, redirect, get_object_or_404
from .forms import AdminUserRegistrationForm
from django.contrib import messages
from accounts.decorators import role_required

@role_required('admin')
def register_user_by_admin(request):
    if request.method == 'POST':
        form = AdminUserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])  # hash password
            user.is_active = True
            user.save()
            messages.success(request, f"{user.role.capitalize()} {user.full_name} registered successfully.")
            return redirect('accounts/admin_dashboard')
    else:
        form = AdminUserRegistrationForm()
    return render(request, 'reports/register_user.html', {'form': form})
