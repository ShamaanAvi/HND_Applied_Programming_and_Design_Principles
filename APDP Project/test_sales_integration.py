import unittest
from unittest.mock import patch
import pandas as pd
from io import StringIO
from sales_analysis import DataLoader, SalesRepository, AnalysisFactory, clear_screen

class TestSalesIntegration(unittest.TestCase):

    @patch('sales_analysis.pd.read_csv')
    @patch('sales_analysis.os.path.exists')
    def test_integration(self, mock_exists, mock_read_csv):
        # Mock os.path.exists to always return True
        mock_exists.return_value = True

        # Mock CSV data
        csv_data = StringIO("""
        branch_id,product_id,date,price,sales_amount
        1,101,2023-01-01,100,5
        1,102,2023-01-01,150,3
        2,101,2023-01-02,100,2
        2,103,2023-01-03,200,7
        1,104,2023-01-04,300,1
        """)
        mock_df = pd.read_csv(csv_data)
        mock_read_csv.return_value = mock_df

        # Test DataLoader and SalesRepository integration
        data_loader = DataLoader('dummy_path.csv')
        repo = SalesRepository(data_loader)

        # Test Monthly Sales Analysis
        monthly_sales_analysis = AnalysisFactory.create_analysis('monthly_sales', repo, branch_id='1')
        monthly_sales_result = monthly_sales_analysis.analyze()
        self.assertEqual(len(monthly_sales_result), 3)

        # Test Price Analysis
        price_analysis = AnalysisFactory.create_analysis('price', repo)
        price_analysis_result = price_analysis.analyze()
        self.assertEqual(len(price_analysis_result), 4)

        # Test Weekly Sales Analysis
        weekly_sales_analysis = AnalysisFactory.create_analysis('weekly_sales', repo)
        weekly_sales_result = weekly_sales_analysis.analyze()
        self.assertEqual(len(weekly_sales_result), 2)

        # Test Product Preference Analysis
        product_preference_analysis = AnalysisFactory.create_analysis('product_preference', repo)
        product_preference_result = product_preference_analysis.analyze()
        self.assertEqual(len(product_preference_result), 4)

        # Test Sales Distribution Analysis
        sales_distribution_analysis = AnalysisFactory.create_analysis('sales_distribution', repo)
        sales_distribution_result = sales_distribution_analysis.analyze()
        self.assertIn('mean', sales_distribution_result.index)

if __name__ == '__main__':
    unittest.main(exit=False)
