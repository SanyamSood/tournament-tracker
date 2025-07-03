from django.shortcuts import render, redirect, get_object_or_404
from .models import Tournament, Group, Team, Match
from .forms import TournamentForm, MatchForm, TournamentModelForm, TeamModelForm
from django.http import JsonResponse, HttpResponseForbidden, HttpResponse
from django.forms import modelformset_factory
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .utils import update_points_table
from datetime import timedelta
import string
from django.db.models import Q

# ==== GROUP CHECKERS ====
def is_organiser(user):
    return user.is_superuser or user.groups.filter(name='Tournament Organisers').exists()

def is_manager(user):
    return user.is_superuser or user.groups.filter(name='Tournament Managers').exists()

def is_organiser_or_manager(user):
    return is_organiser(user) or is_manager(user)

# ==== PUBLIC VIEWS ====
def tournament_list(request):
    tournaments = Tournament.objects.all().order_by('-date')
    return render(request, 'tournament_list.html', {'tournaments': tournaments})

def tournament_detail(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)
    groups = Group.objects.filter(tournament=tournament)

    group_data = []
    for group in groups:
        teams = Team.objects.filter(group=group)
        matches = Match.objects.filter(group=group)

        stats = {team.id: {
            'name': team.name,
            'played': 0,
            'won': 0,
            'lost': 0,
            'sets_won': 0,
            'sets_lost': 0,
            'set_diff': 0,
            'points_scored': 0,
            'points_conceded': 0,
            'point_diff': 0,
        } for team in teams}

        for match in matches:
            if match.winner is None:
                continue

            t1, t2 = match.team1, match.team2
            stats[t1.id]['played'] += 1
            stats[t2.id]['played'] += 1

            sets = [(match.set1_team1, match.set1_team2), (match.set2_team1, match.set2_team2)]
            if match.set3_team1 is not None and match.set3_team2 is not None:
                sets.append((match.set3_team1, match.set3_team2))

            t1_sets_won = sum(1 for a, b in sets if a > b)
            t2_sets_won = sum(1 for a, b in sets if b > a)

            stats[t1.id]['sets_won'] += t1_sets_won
            stats[t1.id]['sets_lost'] += t2_sets_won
            stats[t1.id]['set_diff'] += t1_sets_won - t2_sets_won

            stats[t2.id]['sets_won'] += t2_sets_won
            stats[t2.id]['sets_lost'] += t1_sets_won
            stats[t2.id]['set_diff'] += t2_sets_won - t1_sets_won

            for a, b in sets:
                stats[t1.id]['points_scored'] += a
                stats[t1.id]['points_conceded'] += b
                stats[t2.id]['points_scored'] += b
                stats[t2.id]['points_conceded'] += a

            if t1_sets_won > t2_sets_won:
                stats[t1.id]['won'] += 1
                stats[t2.id]['lost'] += 1
            else:
                stats[t2.id]['won'] += 1
                stats[t1.id]['lost'] += 1

        for team_id in stats:
            stats[team_id]['point_diff'] = stats[team_id]['points_scored'] - stats[team_id]['points_conceded']

        sorted_table = sorted(stats.values(), key=lambda x: (-x['won'], -x['set_diff'], -x['point_diff']))
        group_data.append({'group': group.name, 'table': sorted_table})

    return render(request, 'tournament_detail.html', {
        'tournament': tournament,
        'groups': group_data,
        'current_tournament': tournament
    })


def view_matches(request, tournament_id):
    tournament = get_object_or_404(Tournament, pk=tournament_id)

    search_query = request.GET.get('search', '').strip()

    matches = Match.objects.filter(group__tournament=tournament)

    if search_query:
        matches = matches.filter(
            Q(team1__name__icontains=search_query) |
            Q(team2__name__icontains=search_query)
        )

    matches = matches.order_by('created_at')

    for match in matches:
        match.local_time = match.created_at
        match.local_updated_time = match.updated_at if match.was_updated else None

    return render(request, 'view_matches.html', {
        'tournament': tournament,
        'matches': matches,
        'current_tournament': tournament,
        'search_query': search_query,
    })

def load_teams(request):
    group_id = request.GET.get('group_id')
    teams = Team.objects.filter(group_id=group_id).values('id', 'name')
    return JsonResponse(list(teams), safe=False)

# ==== PROTECTED VIEWS ====
@login_required
@user_passes_test(is_organiser)
def test_permission_view(request):
    return render(request, 'test.html', {'message': 'You have access!'})

@login_required
@user_passes_test(is_organiser)
def create_badminton_tournament(request):
    print("Inside create_badminton_tournament view")

    # ✅ Updated to support 20 groups
    GROUP_CHOICES = [(i, f"{i} Group{'s' if i > 1 else ''}") for i in range(1, 21)]

    if request.method == 'POST':
        form = TournamentForm(request.POST)
        num_groups = int(request.POST.get('num_groups', 1))
        group_letters = list(string.ascii_uppercase[:num_groups])  # Supports A–T

        if form.is_valid():
            tournament = Tournament.objects.create(
                name=form.cleaned_data['name'],
                place=form.cleaned_data['place'],
                date=form.cleaned_data['date']
            )

            for letter in group_letters:
                group = Group.objects.create(name=letter, tournament=tournament)
                team_names = form.cleaned_data.get(f'group_{letter.lower()}_teams', '').strip().split('\n')
                for team_name in team_names:
                    if team_name.strip():
                        Team.objects.create(name=team_name.strip(), group=group)

            return redirect('tournament_detail', tournament.id)
    else:
        form = TournamentForm()
        num_groups = int(request.GET.get('num_groups', 1))
        group_letters = list(string.ascii_uppercase[:20])  # A to T for display

    return render(request, 'create_badminton_tournament.html', {
        'form': form,
        'group_choices': GROUP_CHOICES,
        'group_letters': group_letters
    })

@login_required
@user_passes_test(is_organiser_or_manager)
def add_match(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)
    if request.method == 'POST':
        form = MatchForm(request.POST, tournament=tournament)
        if form.is_valid():
            match = form.save()
            update_points_table(match.group)
            return redirect('tournament_detail', tournament_id=tournament.id)
    else:
        form = MatchForm(tournament=tournament)

    return render(request, 'add_match.html', {'form': form, 'tournament': tournament})

@login_required
@user_passes_test(is_organiser_or_manager)
def edit_match(request, tournament_id, match_id):
    match = get_object_or_404(Match, id=match_id, group__tournament__id=tournament_id)
    tournament = get_object_or_404(Tournament, id=tournament_id)

    if request.method == 'POST':
        form = MatchForm(request.POST, instance=match, tournament=tournament)
        if form.is_valid():
            if form.has_changed():
                form.save()
            return redirect('view_matches', tournament_id=tournament.id)
    else:
        form = MatchForm(instance=match, tournament=tournament)

    return render(request, 'edit_match.html', {
        'form': form,
        'match': match,
        'tournament': tournament,
    })

@login_required
@user_passes_test(is_organiser_or_manager)
def delete_match(request, tournament_id, match_id):
    match = get_object_or_404(Match, id=match_id, group__tournament__id=tournament_id)
    if request.method == 'POST':
        match.delete()
        messages.success(request, "Match deleted successfully.")
        return redirect('view_matches', tournament_id=tournament_id)
    return render(request, 'confirm_delete_match.html', {'match': match, 'tournament_id': tournament_id})

@login_required
@user_passes_test(is_organiser)
def delete_tournament(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)
    if request.method == 'POST':
        tournament.delete()
        return redirect('tournament_list')
    return render(request, 'confirm_delete_tournament.html', {'tournament': tournament})

@login_required
@user_passes_test(is_organiser)
def edit_tournament(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)
    if request.method == 'POST':
        form = TournamentModelForm(request.POST, instance=tournament)
        if form.is_valid():
            form.save()
            return redirect('tournament_detail', tournament_id=tournament.id)
    else:
        form = TournamentModelForm(instance=tournament)
    return render(request, 'edit_tournament.html', {'form': form, 'tournament': tournament})

@login_required
@user_passes_test(is_organiser)
def edit_groups_teams(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)
    groups = Group.objects.filter(tournament=tournament).order_by('name')
    group_forms = []
    all_valid = True

    for group in groups:
        TeamFormSet = modelformset_factory(Team, form=TeamModelForm, extra=0, can_delete=True)
        queryset = Team.objects.filter(group=group)

        if request.method == 'POST':
            formset = TeamFormSet(request.POST, prefix=f"group_{group.id}", queryset=queryset)
            if formset.is_valid():
                instances = formset.save(commit=False)
                for instance in instances:
                    if not instance.group_id:
                        instance.group = group
                    instance.save()
                for obj in formset.deleted_objects:
                    obj.delete()
            else:
                all_valid = False
        else:
            formset = TeamFormSet(prefix=f"group_{group.id}", queryset=queryset)
        group_forms.append((group, formset))

    if request.method == 'POST' and all_valid:
        return redirect('tournament_detail', tournament_id=tournament.id)

    return render(request, 'edit_groups_teams.html', {
        'tournament': tournament,
        'group_forms': group_forms
    })

@login_required
@user_passes_test(is_organiser)
def add_teams(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)
    groups = Group.objects.filter(tournament=tournament)
    TeamFormSet = modelformset_factory(Team, form=TeamModelForm, extra=1, can_delete=False)

    if request.method == 'POST':
        formset = TeamFormSet(request.POST, queryset=Team.objects.none())
        if formset.is_valid():
            for idx, form in enumerate(formset.forms):
                if form.cleaned_data:
                    team = form.save(commit=False)
                    group_id = request.POST.get(f"group_{idx}")
                    if group_id:
                        try:
                            team.group = groups.get(id=group_id)
                            team.save()
                        except Group.DoesNotExist:
                            continue
            messages.success(request, "Teams added successfully!")
            return redirect('tournament_detail', tournament_id=tournament.id)
        else:
            messages.error(request, "Please correct the errors in the form.")
    else:
        formset = TeamFormSet(queryset=Team.objects.none())

    return render(request, 'add_team.html', {
        'formset': formset,
        'tournament': tournament,
        'groups': groups
    })

def permission_denied(request, exception):
    return render(request, '403.html', status=403)

@login_required
def check_permissions(request):
    return HttpResponse(f"""
        Superuser: {request.user.is_superuser}<br>
        Groups: {[g.name for g in request.user.groups.all()]}<br>
        Is Organiser: {is_organiser(request.user)}<br>
        Is Manager: {is_manager(request.user)}<br>
    """)
