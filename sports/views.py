from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from sports.models import Tournaments, CoachingCenters, TournamentJoin
from news.models import LastNewsUpdate, HeadLine
from sports.forms import TournamentRegistration, CoachingCenterRegistration, TournamentJoinForm
from django.urls import reverse
from news.views import scrape_all_sports
from datetime import datetime
import time

from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework.parsers import JSONParser
from sports.serializers import TournamentSerializer, JoinTournamentSerializer
from django.views.generic import ListView, DetailView

from user_auth.models import Services
from .models import Sport_Info

from django.views.generic import ListView, DetailView
from .models import Sport_Info


def homepage(request):
    now = datetime.now()
    last_update = LastNewsUpdate.objects.all()
    if len(last_update) == 0:
        scrape_all_sports()
        LastNewsUpdate.objects.create(last_update=datetime.now())
    else:
        d1_ts = time.mktime(last_update[0].last_update.timetuple())
        d2_ts = time.mktime(now.timetuple())

        if (int(d2_ts - d1_ts) / 60) > 1000000:
            scrape_all_sports()
            LastNewsUpdate.objects.all().delete()
            LastNewsUpdate.objects.create(last_update=datetime.now())
    news = HeadLine.objects.filter(category="sports")
    slider_1 = news[:4]
    slider_2 = news[4:8]
    blog_1 = news[8:12]
    blog_2 = news[12:16]
    n = 4
    slider_3 = [news[i * n:(i + 1) * n] for i in range((len(news[16:]) + n - 1) // n)]

    return render(request, 'sports/homepage.html',
                  {'slider_1': slider_1, 'slider_2': slider_2, 'slider_3': slider_3, 'blog_1': blog_1,
                   'blog_2': blog_2, 'Home': 'active'})


def sports_store(request):
    return render(request, "sports/maps.html", {'Sports_Stores': 'active'})


def Sports_List(request):
    context = {'sportss': Sport_Info.objects.all()}
    return render(request, "sports/sports_list.html", context)


class Sport_InfoListView(ListView):
    model = Sport_Info
    template_name = 'sports/sports_list.html'
    context_object_name = 'sports'


class Sport_InfoDetailView(DetailView):
    model = Sport_Info
    template_name = 'sports/sport_info.html'


def tournament_list(request):
    tournaments = Tournaments.objects.all()
    if request.user.is_authenticated:
        user = User.objects.get(pk=request.user.pk)
        user_tournaments = Tournaments.objects.filter(user=user)
        join = TournamentJoin.objects.filter(user=user)
        joined_pk = []
        for i in join:
            joined_pk.append(i.tournament.pk)
        tournaments = Tournaments.objects.exclude(pk__in=joined_pk)
        join_tornamnets = Tournaments.objects.filter(pk__in=joined_pk)
        return render(request, 'sports/tournament_list.html',
                      {'Tournaments': tournaments,
                       'User_Tournaments': user_tournaments, 'joined_tournaments': join_tornamnets,
                       'Tournaments_active': 'active'})
    return render(request, 'sports/tournament_list.html',
                  {'Tournaments': tournaments, 'Tournaments_active': 'active'})


@login_required
def create_tournament(request):
    tournamentForm = TournamentRegistration()
    if request.method == 'POST':
        tournamentForm = TournamentRegistration(request.POST, request.FILES)
        if tournamentForm.is_valid():
            user = User.objects.get(pk=request.user.pk)
            name = tournamentForm.cleaned_data['name']
            des = tournamentForm.cleaned_data['description']
            s_date = tournamentForm.cleaned_data['start_date']
            e_date = tournamentForm.cleaned_data['end_date']
            location = tournamentForm.cleaned_data['location']
            img = tournamentForm.cleaned_data['image']
            if s_date < datetime.date(datetime.now()):
                return render(request, 'sports/create.html',
                              {'form': tournamentForm, 'name': 'Tournament', 'error': 'Enter a  valid Start date'})
            if s_date > e_date:
                return render(request, 'sports/create.html',
                              {'form': tournamentForm, 'name': 'Tournament',
                               'error': 'End date should be greater that Start date'})
            Tournaments.objects.create(name=name, description=des, start_date=s_date, end_date=e_date,
                                       location=location, user=user, image=img)
            return HttpResponseRedirect(reverse('sports:tournament_list'))

    return render(request, 'sports/create.html',
                  {'form': tournamentForm, 'name': 'Tournament', 'Tournaments_active': 'active'})


@login_required
def delete_tournament(request, t_id):
    if t_id:
        user = User.objects.get(pk=request.user.pk)
        try:
            instance = Tournaments.objects.get(pk=t_id, user=user)
            instance.delete()
        except:
            pass
    return HttpResponseRedirect(reverse('sports:tournament_list'))


@login_required
def edit_tournament(request, t_id):
    if t_id:
        user = User.objects.get(pk=request.user.pk)
        instance = Tournaments.objects.get(pk=t_id, user=user)
        if request.method == 'POST':
            form = TournamentRegistration(request.POST, request.FILES, instance=instance)
            if form.is_valid():
                if form.cleaned_data['start_date'] < datetime.date(datetime.now()):
                    return render(request, 'sports/edit.html', {'edit_form': form, 'name': 'Edit Tournament',
                                                                'error': 'Enter a  valid Start date',
                                                                'Tournaments_active': 'active'})
                if form.cleaned_data['start_date'] > form.cleaned_data['end_date']:
                    return render(request, 'sports/edit.html', {'edit_form': form, 'name': 'Edit Tournament',
                                                                'error': 'End date should be greater that Start date',
                                                                'Tournaments_active': 'active'})
                form.save()
                return HttpResponseRedirect(reverse('sports:tournament_list'))
        form = TournamentRegistration(instance=instance)
        return render(request, 'sports/edit.html', {'edit_form': form, 'name': 'Edit Tournament'})


@login_required
def edit_coaching_center(request, c_id):
    if c_id:
        user = User.objects.get(pk=request.user.pk)
        t = CoachingCenters.objects.get(pk=c_id, user=user)
        form = CoachingCenterRegistration(instance=t)
        if request.method == 'POST':
            form = CoachingCenterRegistration(request.POST, request.FILES, instance=t)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(reverse('sports:coaching_centers_list'))
        return render(request, 'sports/edit.html',
                      {'edit_form': form, 'name': 'Edit Coaching center', 'Coaching_Centers': 'active'})


def coaching_centers_list(request):
    coaching_centers = CoachingCenters.objects.all()
    if request.user.is_authenticated:
        user = User.objects.get(pk=request.user.pk)
        user_coaching_centers = CoachingCenters.objects.filter(user=user)
        return render(request, 'sports/coaching_centers_list.html',
                      {'user_coaching_centers': user_coaching_centers, 'coaching_centers': coaching_centers,
                       'Coaching_Centers': 'active'})
    return render(request, 'sports/coaching_centers_list.html',
                  {'coaching_centers': coaching_centers, 'Coaching_Centers': 'active'})


@login_required
def create_coaching_center(request):
    coaching_centersForm = CoachingCenterRegistration()
    if request.method == 'POST':
        coaching_centersForm = CoachingCenterRegistration(request.POST, request.FILES)
        if coaching_centersForm.is_valid():
            user = User.objects.get(pk=request.user.pk)
            name = coaching_centersForm.cleaned_data['name']
            des = coaching_centersForm.cleaned_data['description']
            street = coaching_centersForm.cleaned_data['street_name']
            state = coaching_centersForm.cleaned_data['state']
            pincode = coaching_centersForm.cleaned_data['pincode']
            contact = coaching_centersForm.cleaned_data['phone_num']
            area = coaching_centersForm.cleaned_data['area']
            email = coaching_centersForm.cleaned_data['mail']
            img = coaching_centersForm.cleaned_data['image']
            CoachingCenters.objects.create(name=name, description=des,
                                           user=user, mail=email, phone_num=contact, pincode=pincode, state=state,
                                           street_name=street, area=area, image=img)
            return HttpResponseRedirect(reverse('sports:coaching_centers_list'))
    return render(request, 'sports/create.html',
                  {'form': coaching_centersForm, 'name': 'Coaching Center', 'Coaching_Centers': 'active'})


@login_required
def delete_coaching_centers(request, c_id):
    if c_id:
        user = User.objects.get(pk=request.user.pk)
        try:
            instance = CoachingCenters.objects.get(pk=c_id, user=user)
            instance.delete()
        except:
            pass
    return HttpResponseRedirect(reverse('sports:coaching_centers_list'))


@api_view(['GET'])
def tournamentsList(request):
    if request.method == 'GET':
        if Services.objects.filter(token=request.GET.get('api_key'), service_type='Tournaments').exists():
            snippets = Tournaments.objects.all()
            serializer = TournamentSerializer(snippets, many=True)
            return JsonResponse(serializer.data, safe=False)
        else:
            return Response('Invalid API Key', status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def tournamentsJoin(request):
    if Services.objects.filter(token=request.GET.get('api_key'), service_type='Tournaments').exists():
        if request.method == 'POST':
            data = JSONParser().parse(request)
            serializer = JoinTournamentSerializer(data=data)
            print(data)
            if serializer.is_valid():
                tournament = Tournaments.objects.get(pk=data['tournament'])
                tournament.no_of_joined += 1
                tournament.save()
                print('User Joined')
                print(data['tournament'])
                # t = Tournaments.objects.get(pk=data['tournament'])
                # t.no_of_joined += 1
                # t.save()
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response('Invalid API Key', status=status.HTTP_400_BAD_REQUEST)


class TournamentDeregister(APIView):

    def get_object(self, pk, u_name):
        try:
            return TournamentJoin.objects.get(pk=pk, name=u_name)
        except TournamentJoin.DoesNotExist:
            raise Http404

    def delete(self, request, pk, name):
        snippet = self.get_object(pk, name)
        snippet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


def join_Tournament(request, t_id):
    initial = {'name': request.user.username, 'mail': request.user.email}

    joinForm = TournamentJoinForm(initial=initial)
    if t_id:
        tourna = Tournaments.objects.get(pk=t_id)
        if request.method == 'POST':
            joinForm = TournamentJoinForm(request.POST)
            if joinForm.is_valid():
                name = joinForm.cleaned_data['name']
                phone_num = joinForm.cleaned_data['phoneNumber']
                mail = joinForm.cleaned_data['mail']

                if request.user.is_authenticated:
                    user = User.objects.get(pk=request.user.pk)
                    TournamentJoin.objects.create(user=user, tournament=tourna, name=name, mail=mail,
                                                  phoneNumber=phone_num)
                    tourna.no_of_joined += 1
                    tourna.save()
                else:
                    TournamentJoin.objects.create(tournament=tourna, name=name, mail=mail, phoneNumber=phone_num)
                    tourna.no_of_joined += 1
                    tourna.save()
                return HttpResponseRedirect(reverse('sports:tournament_list'))
        return render(request, 'sports/join_tournament.html',
                      {'joinform': joinForm, 'tournament': tourna, 'Tournaments_active': 'active'})


def leave_Tournament(request, t_id):
    if t_id:
        if request.user.is_authenticated:
            user = User.objects.get(pk=request.user.pk)
            joined_tournament = TournamentJoin.objects.get(user=user, tournament_id=t_id)
            joined_tournament.delete()
            tournament = Tournaments.objects.get(pk=t_id)
            tournament.no_of_joined -= 1
            tournament.save()
    return HttpResponseRedirect(reverse('sports:tournament_list'))


def participants_list(request, t_id):
    t = Tournaments.objects.get(pk=t_id)
    participants = TournamentJoin.objects.filter(tournament=t)
    return render(request, 'sports/participants_list.html',
                  {'participants': participants, 'Tournaments_active': 'active'})


@api_view(['POST'])
def tournament_leave(request):
    if Services.objects.filter(token=request.GET.get('api_key'), service_type='Tournaments').exists():
        if request.method == 'POST':
            data = JSONParser().parse(request)
            # t = Tournaments.objects.get(name=data['tournament'])
            # data['tournament'] = t.pk

            # tournament = get_object_or_404(Tournaments, title=request.data.get('tournament'))

            pk = data['tournament']
            name = data['name']
            print(pk, name)
            try:
                instances = TournamentJoin.objects.filter(tournament_id=pk, name=name)
                for instance in instances:
                    if instance.user is None:
                        instance.delete()
                        tournament = Tournaments.objects.get(pk=pk)
                        tournament.no_of_joined -= 1
                        tournament.save()
                        print('deleted')
                        return Response('deleted the instance', status=status.HTTP_200_OK)
                print('not found')
                return Response('deleted the instance', status=status.HTTP_404_NOT_FOUND)
            except:
                pass
            print('error occured')
            return Response('invalid data', status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response('invalid API Key', status=status.HTTP_400_BAD_REQUEST)
