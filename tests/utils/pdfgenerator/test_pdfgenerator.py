import unittest
import os
import pytest

from ...context import src
from src.utils.pdfgenerator import PDFGenerator
from ...testutils.modelutils import make_attempt, make_evaluation


@pytest.mark.skipif(os.environ.get('APX_TEST_MODE', 'isolated') == 'isolated',
                    reason='Must not be running in "isolated" generate pdfs')
class TestPDFGenerator(unittest.TestCase):
    def test_generate_report(self):
        generator = PDFGenerator(os.path.join(os.path.dirname(__file__), '../../../src/utils/pdfgenerator/templates'))
        e = make_evaluation('generate report')
        a = make_attempt(e.id)
        result = generator.generate_report(e.to_report(), [a.to_report()], 'name')
        self.assertTrue(os.path.isfile(result))
        self.assertEqual(result[-3:], 'pdf')
        os.remove(result)
