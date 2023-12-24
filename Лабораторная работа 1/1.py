numbers = [1, 2, 3, None, 5]

sum = 0
pos = -1

if None not in numbers:
    print(numbers)

for i in range(len(numbers)):
    if numbers[i] is not None:
        sum += numbers[i]
    else:
        pos = i

numbers[pos] = sum/len(numbers)

print(numbers)

