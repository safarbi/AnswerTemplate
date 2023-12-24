money_capital = 131000
salary = 50000
spend = 55000
increase = 0.03

months = 0
current_budget = money_capital

while current_budget >= spend:
    current_budget -= spend
    months += 1
    current_budget += salary
    spend *= (1 + increase)
    print(f"spend: {spend}")
    print(f"current_budget: {current_budget}")

print(f"Можно прожить {months} месяцев")
