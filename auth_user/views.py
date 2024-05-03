from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail, BadHeaderError
from django.db.models import Q
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.template.loader import get_template
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from Movies.models import Movies, RechargeRequest, Renting, Request, Watchlist
from Movies.utils import check_rent
from ProjectDIAM.settings import EMAIL_HOST_USER
from .forms import RegisterForm, PasswordForm
from .models import Client
import datetime


# View do registo de um novo utilizador
from .token import account_activation_token, TokenGenerator


def register(request):
    # criado formulários para fazer validar os dados
    form = RegisterForm()
    password_form = PasswordForm()
    if request.method == "POST":
        form = RegisterForm(request.POST or None)
        password_form = PasswordForm(request.POST or None)
        if form.is_valid() and password_form.is_valid():
            try:
                email = request.POST['user_email']
                password = request.POST['password1']
                new_user = User.objects.create_user(first_name=request.POST['firstname'],
                                                    last_name=request.POST['lastname'],
                                                    username=email, password=password, email=email, is_active=False)

                # cria a entrada do cliente
                ut = Client(user=new_user, birthday=request.POST['birthday'], gender=request.POST['gender'])
                ut.save()

                # Enviar e-mail ao cliente de welcome
                context = {"user": new_user,
                           'domain': '127.0.0.1:8000',
                           "uid": urlsafe_base64_encode(force_bytes(new_user.pk)),
                           'token': account_activation_token.make_token(new_user),
                           'protocol': 'http',
                           }
                html = get_template('email/register_email.html').render(context)
                send_mail('Welcome to Blockbuster', 'Welcome message!', EMAIL_HOST_USER, [email], html_message=html,
                          fail_silently=True)
                messages.success(request, "Registration successful! You will received an e-mail for confirmation! ")
                return redirect("index")
            except KeyError:
                messages.error(request, "There was a problem with your register!")

    context = {"register_form": form, "password_form": password_form}
    return render(request, "main/register.html", context=context)


def login_view(request):
    if request.method == 'POST':
        try:
            user_auth = authenticate(username=request.POST['username'], password=request.POST['password'])
            login(request, user_auth)
            messages.success(request, "Welcome " + request.user.first_name)
        except (KeyError, AttributeError):
            messages.error(request, "Couldn't Login")
    return HttpResponseRedirect(reverse('index'))


@login_required()
def logout_view(request):
    logout(request)
    return redirect("index")


# Alteração da password por parte do cliente
@login_required()
def new_password(request):
    password_form = PasswordForm()
    if request.method == 'POST':
        password_form = PasswordForm(request.POST or None)
        if password_form.is_valid():
            try:
                u = User.objects.get(username=request.user.username)
                u.set_password(request.POST['password1'])
                u.save()

                # Ao alterar faz o login de novo de forma a manter o utilizador logado
                user_auth = authenticate(username=u.username, password=request.POST['password1'], email=u.email)

                if user_auth is not None:
                    login(request, user_auth)
                    context = {"user": u}

                    # Email avisar que foi alterada a password
                    html = get_template('email/change_password.html').render(context)
                    send_mail('Change Password', 'Change Password', EMAIL_HOST_USER, [u.email], html_message=html,
                              fail_silently=True)
                    messages.success(request, "Password change successful.")
                    return redirect('auth_user:user_profile')
                else:
                    messages.error(request, "There was a problem resetting your password")
            except KeyError:
                messages.error(request, "There was a problem resetting your password")
            return redirect("auth_user:user_profile")

    context = {"user": request.user, "password_form": password_form}
    return render(request, "main/changePassword.html", context=context)


def password_reset_request(request):
    if request.method == "POST":
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data['email']
            associated_users = User.objects.filter(Q(email=data))
            if associated_users.exists():
                for user in associated_users:
                    subject = "Password Reset Requested"
                    c = {
                        "email": user.email,
                        'domain': '127.0.0.1:8000',
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "user": user,
                        'token': default_token_generator.make_token(user),
                        'protocol': 'http',
                    }
                    html = get_template('email/reset_password.html').render(c)
                    try:
                        send_mail(subject, subject, EMAIL_HOST_USER, [user.email], fail_silently=True,
                                  html_message=html)
                    except BadHeaderError:
                        return HttpResponse('Invalid header found.')
                    return redirect("/password_reset/done/")
            else:
                messages.error(request, "User not found.")
    password_reset_form = PasswordResetForm()
    return render(request=request, template_name="main/password_reset.html",
                  context={"password_reset_form": password_reset_form})


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Thank you for your email confirmation. Now you can login your account.')
        return redirect('index')
    else:
        messages.error(request, 'Activation link is invalid!')
        return redirect('index')


# Pagina profile do cliente
@login_required()
def user_profile(request):
    user_client = Client.objects.get(user=request.user)

    if request.method == 'POST' and request.POST:
        uti = RechargeRequest.objects.filter(client=user_client, recharge_state="Requested")
        if uti.count() == 0:
            new_amount = int(request.POST["coinsinput"])
            RechargeRequest.objects.create(client=user_client, coin_amount=new_amount)
            messages.success(request,
                             "Your request has been submitted. Please wait for our approval before trying to rent any "
                             "movie")
        else:
            messages.error(request, "You already made a recharge request. Please wait for its approval")
        return redirect('auth_user:user_profile')

    # Watch Movies
    watch = Watchlist.objects.filter(client=user_client).values()
    # Rented Movies
    rented = Renting.objects.filter(client=user_client).values()
    check_rent()
    movie_rented = []
    his_movie_rented = []
    if rented.count() > 0:
        for i in rented:
            movie_data = Movies.objects.get(pk=int(i['movies_id']))
            if i['rent_state'] == "Available":
                movie_rented.append({'movie': movie_data, "rent": i})
            else:
                his_movie_rented.append({'movie': movie_data, "rent": i})

    # Request Movies
    re_quest = Request.objects.filter(client=user_client).values()

    user_time = user_client.birthday
    user_time_month = user_time.strftime("%B")
    bb_client = user_client.block_coin
    days_passed = datetime.date.today() - user_time
    d = days_passed.days
    if days_passed.days > 200:
        d = 0
    
    context = {
        'bb_client': bb_client,
        'days_passed': d,
        'user_time': user_time,
        'user_time_month': user_time_month,
        'watch': watch,
        'movie_rented': movie_rented,
        're_quest': re_quest,
        'his_movie_rented': his_movie_rented,
    }

    return render(request, 'main/profile.html', context)


def delete_movie_watchlist(request, movie_id):
    dele = Watchlist.objects.get(client=Client.objects.get(user=request.user), w_movie_id=movie_id)
    dele.delete()
    
    return redirect('auth_user:user_profile')