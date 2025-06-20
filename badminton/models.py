from django.db import models
from django.shortcuts import render, get_object_or_404
from .utils import update_points_table
from django.db import models
from django.utils.timezone import now

class Tournament(models.Model):
    name = models.CharField(max_length=100)
    place = models.CharField(max_length=100)
    date = models.DateField()

    def __str__(self):
        return self.name

class Group(models.Model):
    name = models.CharField(max_length=1)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='groups')

    def __str__(self):
        return f"Group {self.name} - {self.tournament.name}"

class Team(models.Model):
    name = models.CharField(max_length=100)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='teams')

    def __str__(self):
        return self.name

class Match(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    court_number = models.PositiveIntegerField()
    team1 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='team1_matches')
    team2 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='team2_matches')

    set1_team1 = models.PositiveIntegerField()
    set1_team2 = models.PositiveIntegerField()
    set2_team1 = models.PositiveIntegerField(null=True, blank=True)
    set2_team2 = models.PositiveIntegerField(null=True, blank=True)
    set3_team1 = models.PositiveIntegerField(null=True, blank=True)
    set3_team2 = models.PositiveIntegerField(null=True, blank=True)

    winner = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name='matches_won')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True)  # Manual updates only

    def get_winner(self):
        sets_team1 = 0
        sets_team2 = 0

        # Set 1
        if self.set1_team1 is not None and self.set1_team2 is not None:
            if self.set1_team1 > self.set1_team2:
                sets_team1 += 1
            elif self.set1_team2 > self.set1_team1:
                sets_team2 += 1

        # Set 2
        if self.set2_team1 is not None and self.set2_team2 is not None:
            if self.set2_team1 > self.set2_team2:
                sets_team1 += 1
            elif self.set2_team2 > self.set2_team1:
                sets_team2 += 1

        # Set 3
        if self.set3_team1 is not None and self.set3_team2 is not None:
            if self.set3_team1 > self.set3_team2:
                sets_team1 += 1
            elif self.set3_team2 > self.set3_team1:
                sets_team2 += 1

        if sets_team1 == 2:
            return self.team1
        elif sets_team2 == 2:
            return self.team2
        else:
            return None

    def save(self, *args, **kwargs):
        is_update = self.pk is not None
        new_winner = self.get_winner()

        if self.winner != new_winner:
            self.winner = new_winner

        if is_update:
            self.updated_at = now()  # update only if it's not a new object

        super().save(*args, **kwargs)
        update_points_table(self.group)

    @property
    def match_score(self):
        t1 = 0
        t2 = 0

        if self.set1_team1 > self.set1_team2:
            t1 += 1
        else:
            t2 += 1

        if self.set2_team1 is not None and self.set2_team2 is not None:
            if self.set2_team1 > self.set2_team2:
                t1 += 1
            else:
                t2 += 1

        if self.set3_team1 is not None and self.set3_team2 is not None:
            if self.set3_team1 > self.set3_team2:
                t1 += 1
            else:
                t2 += 1

        return f"{t1}-{t2}"

    @property
    def was_updated(self):
        return self.updated_at and self.updated_at != self.created_at

    def __str__(self):
        return f"{self.team1.name} vs {self.team2.name} (Group {self.group.name})"

class SetScore(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='set_scores')
    set_number = models.IntegerField()  # 1, 2, or 3
    team1_score = models.PositiveIntegerField()
    team2_score = models.PositiveIntegerField()

    def __str__(self):
        return f"Set {self.set_number}: {self.match}"

class PointsTable(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    matches_played = models.IntegerField(default=0)
    matches_won = models.IntegerField(default=0)
    matches_lost = models.IntegerField(default=0)
    sets_won = models.IntegerField(default=0)
    sets_lost = models.IntegerField(default=0)
    points_scored = models.IntegerField(default=0)
    points_conceded = models.IntegerField(default=0)
    points = models.IntegerField(default=0) 
    class Meta:
        unique_together = ('group', 'team')

    def __str__(self):
        return f"{self.team.name} - {self.points} pts"



