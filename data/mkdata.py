# this script generates the files A.csv, B.csv, C.csv, D.csv, and E.csv from
# the games.csv downloaded from https://www.kaggle.com/datasnaek/chess

if __name__ == "__main__":

    files = {}
    with open("games.csv", "r") as f:
        for i, line in enumerate(f.readlines()):
            if i == 0:
                header = line
                continue
            data = line.split(",")
            eco = data[13]
            code = eco[0]  # A, B, C, D, or E
            if code not in files:
                print(f"making {code}.csv")
                fh = open(f"{code}.csv", "w")
                fh.write(header)
                files[code] = fh
            files[code].write(line)
            if i % 100 == 0:
                print(f"processed {i} records")
