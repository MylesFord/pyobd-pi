import time
def calc_square(numbers):
    for n in numbers:
        print(f'\n{n} ^ 2 = {n*n}')
        time.sleep(0.1)

def calc_cube(numbers):
    for n in numbers:
        print(f'\n{n} ^ 3 = {n*n*n}')
        time.sleep(0.1)
         
numbers = [2, 3, 5, 8]
start = time.time()
calc_square(numbers)
calc_cube(numbers)
end = time.time()

print('Execution Time: {}'.format(end-start))
