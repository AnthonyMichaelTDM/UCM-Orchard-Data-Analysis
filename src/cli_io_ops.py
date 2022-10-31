def get_int(prompt:str, min:int, max:int) -> int:
    while True:
        value:int = int(input(prompt))
        if value >= min and value <= max: 
            return value
        else:
            print("invalid input, try again")
def get_int_nomax(prompt:str, min:int) -> int:
    while True:
        value:int = int(input(prompt))
        if value >= min: 
            return value
        else:
            print("invalid input, try again")

def get_char(prompt) -> str:
    while True:
        value = input(prompt)
        if len(value) >= 1:
            return value[0]
        else:
            print("invalid input, try again")