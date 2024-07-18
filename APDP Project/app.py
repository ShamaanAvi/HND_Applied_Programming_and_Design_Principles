from flask import Flask, request, render_template_string
import pandas as pd
from abc import ABC, abstractmethod
import os

app = Flask(__name__)

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
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"The file {self.file_path} does not exist.")
        try:
            self.data = pd.read_csv(self.file_path)
            self.data['branch_id'] = self.data['branch_id'].astype(str)
        except Exception as e:
            raise IOError(f"An error occurred while reading the file {self.file_path}: {e}")

    def get_data(self):
        if self.data is None:
            self._load_data()
        return self.data

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

data_loader = DataLoader('sales_data.csv')
repo = SalesRepository(data_loader)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        analysis_type = request.form['analysis_type']
        branch_id = request.form.get('branch_id', None)
        
        try:
            if analysis_type == 'monthly_sales':
                analysis = AnalysisFactory.create_analysis(analysis_type, repo, branch_id=branch_id)
            else:
                analysis = AnalysisFactory.create_analysis(analysis_type, repo)
                
            result = analysis.analyze()
            return render_template_string(TEMPLATE, result=result.to_html(), analysis_type=analysis_type)
        except Exception as e:
            return render_template_string(TEMPLATE, error=str(e), analysis_type=analysis_type)

    return render_template_string(TEMPLATE)

TEMPLATE = '''
<!doctype html>
<html lang="en">
  <head>
    <title>Sales Analysis</title>
  </head>
  <body>
    <h1>Sales Analysis</h1>
    <form method="post">
      <label for="analysis_type">Select Analysis Type:</label>
      <select id="analysis_type" name="analysis_type" onchange="toggleBranchID()">
        <option value="monthly_sales">Monthly Sales Analysis</option>
        <option value="price">Price Analysis</option>
        <option value="weekly_sales">Weekly Sales Analysis</option>
        <option value="product_preference">Product Preference Analysis</option>
        <option value="sales_distribution">Sales Distribution Analysis</option>
      </select>
      <br>
      <div id="branch_id_div">
        <label for="branch_id">Enter Branch ID:</label>
        <input type="text" id="branch_id" name="branch_id">
      </div>
      <br>
      <button type="submit">Submit</button>
    </form>
    {% if error %}
    <div style="color: red;">{{ error }}</div>
    {% endif %}
    {% if result %}
    <h2>{{ analysis_type.replace('_', ' ').title() }} Result</h2>
    <div>{{ result | safe }}</div>
    {% endif %}
    <script>
      function toggleBranchID() {
        var analysisType = document.getElementById("analysis_type").value;
        var branchIDDiv = document.getElementById("branch_id_div");
        if (analysisType === "monthly_sales") {
          branchIDDiv.style.display = "block";
        } else {
          branchIDDiv.style.display = "none";
        }
      }
      document.addEventListener("DOMContentLoaded", function() {
        toggleBranchID();
      });
    </script>
  </body>
</html>
'''

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
