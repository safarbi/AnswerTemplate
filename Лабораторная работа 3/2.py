def find_common_participants(group1, group2, delimiter=','):
    participants_group1 = group1.split(delimiter)
    participants_group2 = group2.split(delimiter)
    common_participants = list(set(participants_group1) & set(participants_group2))
    common_participants.sort()
    return common_participants

group1 = "Иванов,Петров,Сидоров"
group2 = "Петров,Смирнов,Кузнецов"

common_participants = find_common_participants(group1, group2)
print(common_participants)
