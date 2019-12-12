from django.urls import path
from sports import views
from .views import Sport_InfoListView, Sport_InfoDetailView

app_name = 'sports'

urlpatterns = [
    path('', views.homepage, name="homepage"),
    # path('choose_favorites/', views.choose_favorite_sports, name='choose_favorites'),
    path('tournament_list/', views.tournament_list, name='tournament_list'),
    path('participants_list/<int:t_id>/', views.participants_list, name='participants_list'),
    path('join_tournament/<int:t_id>', views.join_Tournament, name='join_tournament'),
    path('leave_tournament/<int:t_id>', views.leave_Tournament, name='leave_tournament'),
    path('delete_tournament/<int:t_id>', views.delete_tournament, name='delete_tournament'),
    path('coaching_centers_list/', views.coaching_centers_list, name='coaching_centers_list'),
    path('delete_coaching_centers/<int:c_id>', views.delete_coaching_centers, name='delete_coaching_centers'),
    path('create_coaching_centers/', views.create_coaching_center, name='create_coaching_centers'),
    path('sports_store/', views.sports_store, name='sports_store'),

    path('tournaments/', views.tournamentsList),
    path('tournaments_join/', views.tournamentsJoin, name='tournaments_join'),
    path('sports_list/', Sport_InfoListView.as_view(), name='sports-list'),
    path('sport/<int:pk>/', views.Sport_InfoDetailView.as_view(), name='sport-detail'),
    path('edit_tournament/<int:t_id>', views.edit_tournament, name='edit_tournament'),
    path('create_tournament/', views.create_tournament, name='create_tournament'),
    path('edit_coaching_center/<int:c_id>', views.edit_coaching_center, name='edit_coaching_center'),
    path('tournament_leave/', views.tournament_leave, name='tournament_leave'),
    path('snippets/<int:pk>/<str:name>/', views.TournamentDeregister.as_view()),

]
