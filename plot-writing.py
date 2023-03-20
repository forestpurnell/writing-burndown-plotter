import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import os

def main():
    data_file = 'word_count_data.csv'
    project_id = project_menu(data_file)

    if project_id is None:
        print("Goodbye!")
        return

    start_time, goal_date, word_goal, timestamps, words_remaining = load_or_create_project(project_id, data_file)

    while True:
        print("\nSelect an option:")
        print("1. Update word count")
        print("2. Show progress")
        print("3. Exit")

        choice = int(input("Enter the option number: "))

        if choice == 1:
            current_total = int(input("Enter the most current total word count: "))
            words_written = word_goal - words_remaining[-1] - current_total
            words_remaining[-1] -= words_written
            words_remaining.append(words_remaining[-1])
            timestamps.append(datetime.datetime.now())
            save_to_csv(project_id, timestamps, words_remaining, start_time, goal_date, word_goal, data_file)
        elif choice == 2:
            plot_progress(start_time, goal_date, timestamps, words_remaining, word_goal)
        elif choice == 3:
            print("Goodbye!")
            break
        else:
            print("Invalid option")

def project_menu(data_file):
    if os.path.exists(data_file):
        df = pd.read_csv(data_file)
        project_ids = sorted(df['Project ID'].unique())
    else:
        project_ids = []

    print("\nSelect an option:")
    print("1. Create a new project")
    if project_ids:
        print("2. Select an existing project")
        print("3. Remove a project")

    choice = int(input("Enter the option number: "))

    if choice == 1:
        project_id = input("Enter a unique project ID: ")
        while project_id in project_ids:
            print("Project ID already exists, please choose a different one.")
            project_id = input("Enter a unique project ID: ")
    elif choice == 2:
        print("\nExisting projects:")
        for project_id in project_ids:
            print(f"  {project_id}")
        project_id = input("Enter the project ID you want to select: ")
    elif choice == 3:
        print("\nExisting projects:")
        for project_id in project_ids:
            print(f"  {project_id}")
        project_id = input("Enter the project ID you want to remove: ")
        remove_project(project_id, data_file)
        return None
    else:
        print("Invalid option")
        return None

    return project_id

def load_or_create_project(project_id, data_file):
    if os.path.exists(data_file):
        df = pd.read_csv(data_file)

        project_data = df[df['Project ID'] == project_id]
        if not project_data.empty:
            start_time = pd.to_datetime(project_data.iloc[0]['Start Date'])
            goal_date = pd.to_datetime(project_data.iloc[0]['Goal Date'])
            word_goal = project_data.iloc[0]['Word Goal']
            timestamps = pd.to_datetime(project_data['Timestamp']).tolist()
            words_remaining = project_data['Words Remaining'].tolist()
        else:
            start_time, goal_date, word_goal = get_project_details()
            timestamps = [start_time]
            words_remaining = [word_goal]
            save_to_csv(project_id, timestamps, words_remaining, start_time, goal_date, word_goal, data_file)
    else:
        start_time, goal_date, word_goal = get_project_details()
        timestamps = [start_time]
        words_remaining = [word_goal]
        save_to_csv(project_id, timestamps, words_remaining, start_time, goal_date, word_goal, data_file)

    return start_time, goal_date, word_goal, timestamps, words_remaining

def get_project_details():
    start_time_str = input("Enter the start date (YYYY-MM-DD) or press Enter for today: ")
    
    if start_time_str.strip() == "":
        start_time = datetime.datetime.now()
    else:
        start_time = datetime.datetime.strptime(start_time_str, "%Y-%m-%d")
    
    goal_date_str = input("Enter the goal date (YYYY-MM-DD): ")
    goal_date = datetime.datetime.strptime(goal_date_str, "%Y-%m-%d")
    
    word_goal = int(input("Enter the total word goal: "))
    
    return start_time, goal_date, word_goal


def save_to_csv(project_id, timestamps, words_remaining, start_time, goal_date, word_goal, data_file):
    data = {
        'Project ID': [project_id] * len(timestamps),
        'Timestamp': timestamps,
        'Words Remaining': words_remaining,
        'Start Date': [start_time] * len(timestamps),
        'Goal Date': [goal_date] * len(timestamps),
        'Word Goal': [word_goal] * len(timestamps),
    }
    df = pd.DataFrame(data)

    if os.path.exists(data_file):
        df_existing = pd.read_csv(data_file)
        df = pd.concat([df_existing, df])

    df.to_csv(data_file, index=False)

def remove_project(project_id, data_file):
    df = pd.read_csv(data_file)
    df = df[df['Project ID'] != project_id]
    df.to_csv(data_file, index=False)
    print(f"Project {project_id} removed.")

def plot_progress(start_time, goal_date, timestamps, words_remaining, word_goal):
    plt.figure(figsize=(10, 5), facecolor='white')
    
    # Calculate actual line color
    line_color = 'r' if words_remaining[-1] > (word_goal - word_goal / ((goal_date - start_time).days) * (datetime.datetime.now() - start_time).days) else 'g'

    # Plot actual words remaining
    plt.plot(timestamps, words_remaining, marker='_', markersize=4, linestyle='-', color=line_color, label='ACTUAL WORDS REMAINING')
    plt.plot(timestamps[-1], words_remaining[-1], marker='o', markersize=4, color=line_color)
    
    # Plot ideal burndown line
    ideal_times = [start_time, goal_date]
    ideal_words_remaining = [word_goal, 0]
    plt.plot(ideal_times, ideal_words_remaining, linestyle='dotted', color='grey', label='IDEAL BURNDOWN LINE')

    plt.title("WORD GOAL BURNDOWN CHART")
    plt.xlabel("TIME")
    plt.ylabel("WORDS REMAINING")
    plt.grid(color='grey', linestyle='-', linewidth=0.25, alpha=0.5)
    plt.xticks(rotation=45, fontname="Arial", fontsize=8, fontweight='bold')
    plt.yticks(fontname="Arial", fontsize=8, fontweight='bold')

    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d%b'))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=1))

    plt.legend(frameon=False, loc='upper right', prop={'size': 8, 'family': 'Arial'})
    plt.show()

if __name__ == "__main__":
    main()
