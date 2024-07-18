import unittest
import pandas as pd
from io import StringIO
from sales_analysis import DataLoader, SalesRepository, MonthlySalesAnalysis, PriceAnalysis, AnalysisFactory

class TestSalesRepository(unittest.TestCase):

    def setUp(self):
        # Sample data to be used for tests
        data = StringIO("""branch_id,date,product_id,sales_amount,price
        1,2023-01-01,101,100,10.0
        1,2023-01-08,101,150,10.0
        1,2023-01-15,102,200,20.0
        2,2023-01-01,101,120,10.0
        2,2023-01-08,103,130,15.0
        2,2023-01-15,104,140,20.0""")
        
        self.data_loader = DataLoader.__new__(DataLoader)  # Bypass the Singleton restriction for testing
        self.data_loader.file_path = None
        self.data_loader.data = pd.read_csv(data)
        self.repo = SalesRepository(self.data_loader)

    def test_get_monthly_sales(self):
        result = self.repo.get_monthly_sales('1')
        self.assertEqual(len(result), 3)
        self.assertTrue('sales_amount' in result.columns)

    def test_get_product_price_analysis(self):
        result = self.repo.get_product_price_analysis()
        expected_columns = ['count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max']
        self.assertTrue(all(col in result.columns for col in expected_columns))

    def test_get_weekly_sales(self):
        result = self.repo.get_weekly_sales()
        self.assertTrue('week' in result.index.names)
        self.assertTrue('sales_amount' in result.columns)

    def test_get_product_preference(self):
        result = self.repo.get_product_preference()
        self.assertTrue(isinstance(result, pd.Series))
        self.assertTrue(result.index.name == 'product_id')

    def test_get_sales_distribution(self):
        result = self.repo.get_sales_distribution()
        expected_columns = ['count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max']
        self.assertTrue(all(col in result.index for col in expected_columns))

class TestAnalysisFactory(unittest.TestCase):

    def setUp(self):
        data = StringIO("""branch_id,date,product_id,sales_amount,price
        1,2023-01-01,101,100,10.0
        1,2023-01-08,101,150,10.0
        1,2023-01-15,102,200,20.0
        2,2023-01-01,101,120,10.0
        2,2023-01-08,103,130,15.0
        2,2023-01-15,104,140,20.0""")
        
        self.data_loader = DataLoader.__new__(DataLoader)  # Bypass the Singleton restriction for testing
        self.data_loader.file_path = None
        self.data_loader.data = pd.read_csv(data)
        self.repo = SalesRepository(self.data_loader)

    def test_monthly_sales_analysis(self):
        analysis = MonthlySalesAnalysis(self.repo, '1')
        result = analysis.analyze()
        self.assertEqual(len(result), 3)
        self.assertTrue('sales_amount' in result.columns)

    def test_price_analysis(self):
        analysis = PriceAnalysis(self.repo)
        result = analysis.analyze()
        expected_columns = ['count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max']
        self.assertTrue(all(col in result.columns for col in expected_columns))

    def test_analysis_factory(self):
        analysis = AnalysisFactory.create_analysis('monthly_sales', self.repo, branch_id='1')
        self.assertIsInstance(analysis, MonthlySalesAnalysis)
        analysis = AnalysisFactory.create_analysis('price', self.repo)
        self.assertIsInstance(analysis, PriceAnalysis)

if __name__ == '__main__':
    unittest.main(exit=False)
