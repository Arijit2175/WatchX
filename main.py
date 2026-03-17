from src.stats import get_system_stats

def main():
    stats = get_system_stats()
    print("System Stats:")
    for key, value in stats.items():
        print(f"{key.capitalize()}: {value}")

if __name__ == "__main__":
    main()