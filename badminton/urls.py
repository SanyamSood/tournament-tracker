from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

#app_name = 'badminton'
urlpatterns = [
    path('', views.tournament_list, name='tournament_list'),  # Updated function name
    # path('', views.home, name='home'),
    path('ajax/load-teams/', views.load_teams, name='ajax_load_teams'),
    path('tournament/create/', views.create_badminton_tournament, name='create_badminton_tournament'),  # Updated path
    path('tournament/<int:tournament_id>/', views.tournament_detail, name='tournament_detail'),  # Updated name
    path('tournament/<int:tournament_id>/edit/', views.edit_tournament, name='edit_tournament'),
    path('tournament/<int:tournament_id>/delete/', views.delete_tournament, name='delete_tournament'),
    path('tournament/<int:tournament_id>/match/add/', views.add_match, name='add_match'),
    path('tournament/<int:tournament_id>/matches/', views.view_matches, name='view_matches'),
    path('tournament/<int:tournament_id>/match/<int:match_id>/edit/', views.edit_match, name='edit_match'),
    path('test/', views.test_permission_view, name='test_permission'),

    path('tournament/<int:tournament_id>/edit-groups-teams/', views.edit_groups_teams, name='edit_groups_teams'),
    path('tournament/<int:tournament_id>/delete/', views.delete_tournament, name='confirm_delete_tournament'),
    path('tournament/<int:tournament_id>/add-team/', views.add_teams, name='add_team'),
    path('tournament/<int:tournament_id>/match/<int:match_id>/delete/', views.delete_match, name='delete_match'),
    path('check-permissions/', views.check_permissions),

    #path('signup/', views.signup_view, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    #path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/login/'), name='logout'),
    path('tournament/<int:tournament_id>/download-points/', views.download_points_table_csv, name='download_points_table_csv'),
]