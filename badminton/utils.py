# badminton/utils.py

def update_points_table(group):
    from .models import PointsTable, Match  # ✅ delayed import to avoid circular imports

    # Delete old points
    PointsTable.objects.filter(group=group).delete()

    teams = group.teams.all()

    # Initialize table
    for team in teams:
        PointsTable.objects.create(group=group, team=team)

    # Recalculate all stats
    matches = Match.objects.filter(group=group)

    for match in matches:
        if match.winner is None:
            continue

        team1_stats = PointsTable.objects.get(group=group, team=match.team1)
        team2_stats = PointsTable.objects.get(group=group, team=match.team2)

        team1_stats.matches_played += 1
        team2_stats.matches_played += 1

        set_scores = [
            (match.set1_team1, match.set1_team2),
            (match.set2_team1, match.set2_team2)
        ]
        if match.set3_team1 is not None and match.set3_team2 is not None:
            set_scores.append((match.set3_team1, match.set3_team2))

        for s1, s2 in set_scores:
            if s1 > s2:
                team1_stats.sets_won += 1
                team2_stats.sets_lost += 1
            else:
                team2_stats.sets_won += 1
                team1_stats.sets_lost += 1

            team1_stats.points_scored += s1
            team1_stats.points_conceded += s2
            team2_stats.points_scored += s2
            team2_stats.points_conceded += s1

        if match.winner == match.team1:
            team1_stats.matches_won += 1
            team2_stats.matches_lost += 1
        else:
            team2_stats.matches_won += 1
            team1_stats.matches_lost += 1

        team1_stats.points = team1_stats.matches_won * 2
        team2_stats.points = team2_stats.matches_won * 2

        team1_stats.save()
        team2_stats.save()