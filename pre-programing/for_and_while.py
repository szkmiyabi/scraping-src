for x in [1, 2, 3]:
  print(x)
  print("---")

for i in range(10):
  print(i)
  print("---")

d = {'a': 1, 'b': 2}

for key in d:
  value = d[key]
  print(key, value)
  print("---")

for key, value in d.items():
  print(key, value)
  print("---")

s = 1
while s < 1000:
  print(s)
  s = s * 2


