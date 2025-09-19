from data_loader import load_data
from engine import ExecutionEngine

def main():
    # 1. load data
    data_points = load_data() # tick data points

    # 2. intilialize engine
    engine = ExecutionEngine(data_points)
    
    # 3. run engine
    engine.run()


if __name__ == "__main__":
    main()