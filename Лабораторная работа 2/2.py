salary = 50000
spend = 55000
months = 10
increase = 0.03
total_deficit = 0

for month in range(months):
    monthly_deficit = spend - salary
    total_deficit += monthly_deficit
    spend *= (1 + increase)

print(f"Необходима подушка в размере {round(total_deficit, 2)} руб")