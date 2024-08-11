import os
import re
from bs4 import BeautifulSoup
import glob
import time
import datetime

def generate_battery_report():
    user_documents_path = os.path.join(os.path.expanduser("~"), "Documents")
    report_path = os.path.join(user_documents_path, "battery-report.html")
    os.system(f'powercfg /batteryreport /output "{report_path}"')

def extract_capacity(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')

    # Find the "Installed batteries" section and extract the required capacities
    full_charge_capacity = None
    design_capacity = None

    # Iterate through all the rows to find the relevant data
    for row in soup.find_all('tr'):
        columns = row.find_all('td')
        if len(columns) == 2:
            header = columns[0].get_text(strip=True)
            value = columns[1].get_text(strip=True).replace(',', '')

            if 'DESIGN CAPACITY' in header:
                design_capacity = int(re.search(r'(\d+)', value).group(1))
            elif 'FULL CHARGE CAPACITY' in header:
                full_charge_capacity = int(re.search(r'(\d+)', value).group(1))

    return full_charge_capacity, design_capacity

def calculate_capacity_ratio(full_charge_capacity, design_capacity):
    if full_charge_capacity and design_capacity:
        return (full_charge_capacity / design_capacity) * 100
    return None

def find_latest_report():
    user_documents_path = os.path.join(os.path.expanduser("~"), "Documents")
    report_pattern = "battery-report*.html"
    report_files = glob.glob(os.path.join(user_documents_path, report_pattern))
    if report_files:
        latest_report = max(report_files, key=os.path.getmtime)
        return latest_report, os.path.getmtime(latest_report)
    else:
        return None, None

def main():
    generate_battery_report()

    latest_report, report_time = find_latest_report()
    if latest_report:
        report_time_str = datetime.datetime.fromtimestamp(report_time).strftime("%Y-%m-%d %H:%M:%S")
        full_charge_capacity, design_capacity = extract_capacity(latest_report)
        capacity_ratio = calculate_capacity_ratio(full_charge_capacity, design_capacity)
        # ANSI escape code for red text
        red_color = "\033[91m"
        reset_color = "\033[0m"
        print(f"Report Generation Time: {report_time_str}")
        print(f"Full Charge Capacity: {full_charge_capacity} mWh")
        print(f"Design Capacity: {design_capacity} mWh")
        print(f"Battery Health: {red_color}{capacity_ratio:.2f}%{reset_color}")
    else:
        print("Could not find the necessary data in the battery report.")

if __name__ == "__main__":
    main()
