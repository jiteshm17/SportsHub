from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_text, force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from user_auth.forms import UpdateProfile, UserProfile
from user_auth.models import Profile
from user_auth.tokens import account_activation_token
from user_auth.forms import RegisterForm
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.core.mail import EmailMessage
from django.contrib.auth.models import User
from .forms import ServicesForm, ServiceRegistrationForm
from .models import Services
from user_auth.utils.generate_token import generatetoken


@login_required
def your_apis(request):
    services = Services.objects.filter(user_name=request.user).order_by('service_type')
    return render(request, 'user_auth/your_apis.html', {'services': services})


@login_required
def choose_service(request, service_name):
    if request.user.is_authenticated:
        if not Services.objects.filter(user_name=request.user, service_type=service_name).exists():
            print(service_name)
            Services.objects.create(user_name=request.user, service_type=service_name, token=generatetoken())
        else:
            service = Services.objects.get(user_name=request.user, service_type=service_name)
            service.token = generatetoken()
            service.save()
        return redirect('user_auth:your_apis')
    else:
        return redirect('user_auth:login')


def login_page(request):
    form = AuthenticationForm()
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if 'next' in request.GET:
                return redirect(request.GET['next'])

            return redirect('sports:homepage')

    return render(request, 'user_auth/login.html', {'form': form, 'login_active': 'active'})


@login_required
def logout_user(request):
    logout(request)
    return redirect('sports:homepage')


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect('user_auth:login')
    else:
        return HttpResponse('Activation link is invalid!')


@login_required
def user_profile(request):
    user = request.user
    print(user)
    profile = Profile.objects.get(user_name__username=user)
    if request.method == 'POST':
        user_form = UpdateProfile(request.POST, instance=user)
        news_form = UserProfile(request.POST, instance=profile)
        if user_form.is_valid() and news_form.is_valid():
            user_form.save()
            news_form.save()
            msg = 'Profile Details successfully updated!'
            return render(request, 'user_auth/profile.html',
                          {'user_form': user_form, 'news_form': news_form, 'msg': msg, 'user_active': 'active'})

    else:
        user_form = UpdateProfile(instance=user)
        news_form = UserProfile(instance=profile)
        return render(request, 'user_auth/profile.html',
                      {'user_form': user_form, 'news_form': news_form, 'user_active': 'active'})


def register_user(request):
    form = RegisterForm()
    form_profile = UserProfile()
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        form_profile = UserProfile(request.POST)
        if form.is_valid() and form_profile.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            # user.is_active = False
            user.save()
            user_profile = Profile.objects.create(user_name=user, location=form_profile.cleaned_data['location'])
            user_profile.save()

            # current_site = get_current_site(request)
            # mail_subject = 'Activate your account.'
            # message = render_to_string('user_auth/activate_email.html', {
            #     'user': user,
            #     'domain': current_site.domain,
            #     'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            #     'token': account_activation_token.make_token(user),
            # })
            # to_email = form.cleaned_data.get('email')
            # email = EmailMessage(
            #     mail_subject, message, to=[to_email]
            # )
            # email.send()
            # return render(request,'registration/confirm_email.html',{})
            return redirect('user_auth:login')
    return render(request, 'user_auth/register.html',
                  {'form': form, 'form_profile': form_profile, 'signup_active': 'active'})


def get_apis(request):
    return render(request, 'user_auth/get_api.html', {'Get_API_Key': 'active'})
