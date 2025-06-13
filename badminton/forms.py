from django import forms
from .models import Match, Tournament, Group, Team

GROUP_CHOICES = [(str(i), f"{i} Group{'s' if i != '1' else ''}") for i in range(1, 11)]

class TournamentForm(forms.Form):
    name = forms.CharField(label="Tournament Name", max_length=100)
    place = forms.CharField(max_length=100)
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    num_groups = forms.ChoiceField(
        choices=GROUP_CHOICES,
        label="Number of Groups"
    )

    # Define fields for up to 10 groups (A to J)
    group_a_teams = forms.CharField(
        label="Group A Teams",
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        help_text="Enter team names for Group A, one per line."
    )

    group_b_teams = forms.CharField(
        label="Group B Teams",
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        help_text="Enter team names for Group B, one per line."
    )

    group_c_teams = forms.CharField(
        label="Group C Teams",
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        help_text="Enter team names for Group C, one per line."
    )

    group_d_teams = forms.CharField(
        label="Group D Teams",
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        help_text="Enter team names for Group D, one per line."
    )

    group_e_teams = forms.CharField(
        label="Group E Teams",
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        help_text="Enter team names for Group E, one per line."
    )

    group_f_teams = forms.CharField(
        label="Group F Teams",
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        help_text="Enter team names for Group F, one per line."
    )

    group_g_teams = forms.CharField(
        label="Group G Teams",
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        help_text="Enter team names for Group G, one per line."
    )

    group_h_teams = forms.CharField(
        label="Group H Teams",
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        help_text="Enter team names for Group H, one per line."
    )

    group_i_teams = forms.CharField(
        label="Group I Teams",
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        help_text="Enter team names for Group I, one per line."
    )

    group_j_teams = forms.CharField(
        label="Group J Teams",
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        help_text="Enter team names for Group J, one per line."
    )

class TournamentModelForm(forms.ModelForm):
    class Meta:
        model = Tournament
        fields = ['name', 'place', 'date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

class MatchForm(forms.ModelForm):

    class Meta:
        model = Match
        fields = [
            'group', 'court_number',
            'team1', 'team2',
            'set1_team1', 'set1_team2',
            'set2_team1', 'set2_team2',
            'set3_team1', 'set3_team2'
        ]

    def __init__(self, *args, **kwargs):
        
        tournament = kwargs.pop('tournament', None)
        super().__init__(*args, **kwargs)

        if tournament:
            self.fields['group'].queryset = Group.objects.filter(tournament=tournament)
            self.fields['team1'].queryset = Team.objects.none()
            self.fields['team2'].queryset = Team.objects.none()

            if 'group' in self.data:
                try:
                    group_id = int(self.data.get('group'))
                    self.fields['team1'].queryset = Team.objects.filter(group_id=group_id)
                    self.fields['team2'].queryset = Team.objects.filter(group_id=group_id)
                except (ValueError, TypeError):
                    pass
            elif self.instance.pk:
                self.fields['team1'].queryset = Team.objects.filter(group=self.instance.group)
                self.fields['team2'].queryset = Team.objects.filter(group=self.instance.group)

        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

            
class TeamModelForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['name']

class AddTeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['name', 'group']
