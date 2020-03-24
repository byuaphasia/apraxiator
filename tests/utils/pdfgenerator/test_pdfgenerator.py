import unittest
import os

from ...context import src
from src.utils.pdfgenerator import PDFGenerator
from ...testutils.modelutils import make_attempt, make_evaluation


class TestPDFGenerator(unittest.TestCase):
    def test_generate_report(self):
        generator = PDFGenerator()
        e = make_evaluation('generate report')
        a = make_attempt(e.id)
        result = generator.generate_report(e.to_report(), [a.to_report()], 'name')
        self.assertTrue(os.path.isfile(result))
        self.assertEqual(result[-3:], 'pdf')
        os.remove(result)
