x = "9"

# print(f"The value of x is: {x} blah blah blah")
# print("The value of x is:", x, "blah blah blah")

list1 = [1, 2, 3]

testList = [1, list1, "3", 4, {'key': list1}]

i = 0
for item in testList:
    if type(item) == str:
        testList[i] = "Hello"
    i += 1

print(testList)

testDict = {"a": 1, "boobs": "hehehheehh", "c": "3", "d": 4, "e":5}

print(testDict["boobs"])

for key in testDict:
    print(key)
    print(testDict[key])


