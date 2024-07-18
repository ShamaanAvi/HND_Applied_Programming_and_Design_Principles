import pandas as pd
from abc import ABC, abstractmethod
import os
import platform

# Function to clear the terminal screen
def clear_screen():
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")

# Singleton Pattern for Data Loading
class DataLoader:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(DataLoader, cls).__new__(cls)
        return cls._instance

    def __init__(self, file_path):
        self.file_path = file_path
        self.data = None
        self._load_data()

    def _load_data(self):
        # File Handling: Check if the file exists
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"The file {self.file_path} does not exist.")
        try:
            # File Handling: Reading CSV file into a Pandas DataFrame
            self.data = pd.read_csv(self.file_path)
            # Ensure branch_id is treated as a string
            self.data['branch_id'] = self.data['branch_id'].astype(str)
        except FileNotFoundError as fnf_error:
            raise FileNotFoundError(f"File not found: {fnf_error}")
        except pd.errors.EmptyDataError:
            raise ValueError("The file is empty.")
        except pd.errors.ParserError:
            raise ValueError("Error parsing the file.")
        except Exception as e:
            raise IOError(f"An unexpected error occurred while reading the file {self.file_path}: {e}")

    def get_data(self):
        if self.data is None:
            self._load_data()
        return self.data

# Repository Pattern for Data Access
class SalesRepository:
    def __init__(self, data_loader):
        self.data_loader = data_loader

    def get_monthly_sales(self, branch_id):
        try:
            data = self.data_loader.get_data()
            branch_data = data[data['branch_id'] == branch_id]
            if branch_data.empty:
                raise ValueError(f"No data found for branch ID: {branch_id}")
            return branch_data
        except Exception as e:
            raise ValueError(f"Error fetching monthly sales data: {e}")

    def get_product_price_analysis(self):
        try:
            data = self.data_loader.get_data()
            return data.groupby('product_id')['price'].describe()
        except Exception as e:
            raise ValueError(f"Error fetching product price analysis: {e}")

    def get_weekly_sales(self):
        try:
            data = self.data_loader.get_data()
            data['week'] = pd.to_datetime(data['date']).dt.isocalendar().week
            return data.groupby('week')['sales_amount'].sum()
        except Exception as e:
            raise ValueError(f"Error fetching weekly sales data: {e}")

    def get_product_preference(self):
        try:
            data = self.data_loader.get_data()
            return data.groupby('product_id')['sales_amount'].sum().sort_values(ascending=False)
        except Exception as e:
            raise ValueError(f"Error fetching product preference data: {e}")

    def get_sales_distribution(self):
        try:
            data = self.data_loader.get_data()
            return data['sales_amount'].describe()
        except Exception as e:
            raise ValueError(f"Error fetching sales distribution data: {e}")

# Strategy Pattern for Analysis
class AnalysisStrategy(ABC):
    @abstractmethod
    def analyze(self):
        pass

class MonthlySalesAnalysis(AnalysisStrategy):
    def __init__(self, repo, branch_id):
        self.repo = repo
        self.branch_id = branch_id

    def analyze(self):
        return self.repo.get_monthly_sales(self.branch_id)

class PriceAnalysis(AnalysisStrategy):
    def __init__(self, repo):
        self.repo = repo

    def analyze(self):
        return self.repo.get_product_price_analysis()

class WeeklySalesAnalysis(AnalysisStrategy):
    def __init__(self, repo):
        self.repo = repo

    def analyze(self):
        return self.repo.get_weekly_sales()

class ProductPreferenceAnalysis(AnalysisStrategy):
    def __init__(self, repo):
        self.repo = repo

    def analyze(self):
        return self.repo.get_product_preference()

class SalesDistributionAnalysis(AnalysisStrategy):
    def __init__(self, repo):
        self.repo = repo

    def analyze(self):
        return self.repo.get_sales_distribution()

# Factory Pattern for Analysis Creation
class AnalysisFactory:
    @staticmethod
    def create_analysis(analysis_type, repo, **kwargs):
        if analysis_type == 'monthly_sales':
            return MonthlySalesAnalysis(repo, kwargs['branch_id'])
        elif analysis_type == 'price':
            return PriceAnalysis(repo)
        elif analysis_type == 'weekly_sales':
            return WeeklySalesAnalysis(repo)
        elif analysis_type == 'product_preference':
            return ProductPreferenceAnalysis(repo)
        elif analysis_type == 'sales_distribution':
            return SalesDistributionAnalysis(repo)
        else:
            raise ValueError("Unknown analysis type")

# CLI Interface
def main():
    try:
        data_loader = DataLoader('sales_data.csv')
        repo = SalesRepository(data_loader)
    except (FileNotFoundError, ValueError, IOError) as e:
        print(f"Initialization error: {e}")
        return

    while True:
        clear_screen()
        print("Select Analysis Type:")
        print("1. Monthly Sales Analysis")
        print("2. Price Analysis")
        print("3. Weekly Sales Analysis")
        print("4. Product Preference Analysis")
        print("5. Sales Distribution Analysis")
        print("0. Exit")

        choice = input("Enter choice: ")

        if choice == '0':
            break

        if choice == '1':
            branch_id = input("Enter branch ID: ")
            analysis = AnalysisFactory.create_analysis('monthly_sales', repo, branch_id=branch_id)
        elif choice == '2':
            analysis = AnalysisFactory.create_analysis('price', repo)
        elif choice == '3':
            analysis = AnalysisFactory.create_analysis('weekly_sales', repo)
        elif choice == '4':
            analysis = AnalysisFactory.create_analysis('product_preference', repo)
        elif choice == '5':
            analysis = AnalysisFactory.create_analysis('sales_distribution', repo)
        else:
            print("Invalid choice")
            input("Press Enter to continue...")
            continue

        try:
            result = analysis.analyze()
            print("Result:")
            print(result)
        except ValueError as ve:
            print(f"Value error: {ve}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        
        input("Press Enter to continue...")
        clear_screen()

if __name__ == "__main__":
    main()
