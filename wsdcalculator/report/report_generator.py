from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import uuid
import os


class ReportGenerator:
    def create_pdf_report(self, eval_id, date, name, attempts, total_wsd, gender, age, impression):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        env = Environment(loader=FileSystemLoader(dir_path, encoding='utf-8'))
        template = env.get_template('report_template.html', )
        template_variables = {
            'name': name,
            'eval_id': eval_id,
            'date': date,
            'attempts': attempts,
            'total_wsd': total_wsd,
            'gender': gender,
            'age': age,
            'impression': impression
        }
        html_out = template.render(template_variables)
        outfile = self.get_outfile()
        HTML(string=html_out, base_url='.').write_pdf(outfile)
        return outfile

    @staticmethod
    def get_outfile():
        dir_path = os.path.dirname(os.path.realpath(__file__)) + '/tmp_reports/'
        file_name = uuid.uuid4().hex + '.pdf'
        return os.path.join(dir_path, file_name)
