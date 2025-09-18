from data_loader import load_data


def main():
    data = load_data()
    for point in data:
        print(point)

if __name__ == "__main__":
    main()