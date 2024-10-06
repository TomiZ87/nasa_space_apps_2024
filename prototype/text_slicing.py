def main():
    #filepath = read_filepath()
    with open("i_Investigation.txt", "r") as file:
        lines = file.readlines()

    desired_data = dict()

    for line in lines:
        line = line.strip().split("	")
        # The first element in each line will be a key and the value inside of it

        desired_keys = ["Study Identifier", "Study Title", "Study Description", "Study Protocol Description" ]    

        
        if len(line) >= 2:
            if line[0] in desired_keys:
                desired_data.update({line[0]: line[1]})
                
    print(desired_data["Study Title"])

    

def read_filepath():
    filepath = input("Enter the path of your file below:\n")
    return filepath


if __name__ == "__main__":
    main()