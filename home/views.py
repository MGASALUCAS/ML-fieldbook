from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User


def home_view(request):
    return render(request, "home/index.html")


# signup view
def signup_view(request):
    context = {}
    if request.POST:
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]

        if User.objects.filter(username=username).exists():
            context["form_errors"] = "username already exists"
        elif User.objects.filter(email=email).exists():
            context["form_errors"] = "email already exists"
        else:
            user = User.objects.create_user(username, email, password)
            user.save()
            return redirect("/login")

    return render(request, "home/signup.html", context)


def logout_view(request):
    logout(request)
    return redirect("/")


def process_login(request, redirect_path="/"):
    from django.db.models import Q

    identifier = request.POST.get("email")
    password = request.POST.get("password")

    user = None

    if identifier and password:
        try:
            user_obj = User.objects.get(Q(username=identifier) | Q(email=identifier))
            user = authenticate(username=user_obj.username, password=password)
        except User.DoesNotExist:
            return False

    if user is not None:
        login(request, user)
        return redirect(redirect_path)
    else:
        return False


def login_view(request):
    context = {}
    if request.POST:
        success = process_login(request, "/")
        if success is False:
            context["form_errors"] = "invalid username or password"
        else:
            return redirect("/logbook")

    return render(request, "home/login.html", context)


def password_reset_view(request):
    from django.db.models import Q

    context = {}

    if request.method == "POST":
        identifier = request.POST.get("identifier")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if not identifier or not password1 or not password2:
            context["form_errors"] = "All fields are required"
        elif password1 != password2:
            context["form_errors"] = "Passwords do not match"
        else:
            try:
                user = User.objects.get(Q(email=identifier) | Q(username=identifier))
                user.password = make_password(password1)
                user.save()
                context["success_message"] = "Password has been reset successfully"
                return redirect("/login")
            except User.DoesNotExist:
                context["form_errors"] = "No user with that username or email found"

    return render(request, "home/reset.html", context)
