from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import redirect, render
from django.utils.safestring import mark_safe

from .forms import LoginForm, RegisterForm, UserUpdateForm


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("dashboard")

        errors_msg = []
        for field, errors in form.errors.items():
            field_name = form.fields[field].label if field in form.fields else field
            for error in errors:
                errors_msg.append(f"{field_name}: {error}")

        messages.error(request, mark_safe(f"Erro ao criar conta:<br>{'<br>'.join(errors_msg)}"))
    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("dashboard")

        for errors in form.errors.values():
            for error in errors:
                messages.error(request, str(error))
    else:
        form = LoginForm()

    return render(request, "accounts/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
def account_view(request):
    # TODO: Improve form error message
    if request.method == "POST":
        print(request.POST)
        if "update_user" in request.POST:
            user_update_form: UserUpdateForm = UserUpdateForm(request.POST, instance=request.user)
            password_change_form = PasswordChangeForm(request.user)
            if user_update_form.is_valid():
                user_update_form.save()
                messages.success(request, "As suas informações foram atualizadas com sucesso")
                return redirect("account")
            messages.error(request, "Não foi possível atualizar as informações.")

        elif "change_password" in request.POST:
            user_update_form = UserUpdateForm(instance=request.user)
            password_change_form = PasswordChangeForm(request.user, request.POST)
            if password_change_form.is_valid():
                user = password_change_form.save()
                update_session_auth_hash(request, user)  # not logout
                messages.success(request, "A sua senha foi atualizada com sucesso")
                return redirect("account")
            messages.error(request, "Não foi possível atualizar a senha.")

        return redirect("account")
    else:
        user_update_form = UserUpdateForm(instance=request.user)
        password_change_form = PasswordChangeForm(request.user)

    return render(
        request,
        "accounts/account.html",
        {
            "user_update_form": user_update_form,
            "password_change_form": password_change_form,
        },
    )
