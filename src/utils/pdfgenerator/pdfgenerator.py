from jinja2 import Environment, FileSystemLoader
try:
    from weasyprint import HTML
except OSError:
    print('Unable to import weasyprint')
import uuid
import os

from .ipdfgenerator import IPDFGenerator

tmp_storage_dir = 'tmp'


class PDFGenerator(IPDFGenerator):
    def generate_subject_waiver(self, subject_name: str, subject_email: str, date_signed: str, signature_file):
        return self._create_pdf_waiver(
            subject_name, subject_email, date_signed, signature_file, '', '', '', None
        )

    def generate_representative_waiver(self, subject_name: str, subject_email: str, representative_name: str, relationship: str, date_signed: str, signature_file):
        return self._create_pdf_waiver(
            subject_name, subject_email, '', None, representative_name, relationship, date_signed, signature_file
        )

    def _create_pdf_waiver(self, research_subject_name, research_subject_email, research_subject_date,
                           research_subject_signature, representative_name, representative_relationship,
                           representative_date, representative_signature):
        research_subject_signature_path = ''
        representative_signature_path = ''
        if research_subject_signature is not None:
            research_subject_signature_path = self._get_signature_file()
            research_subject_signature.save(research_subject_signature_path)
        if representative_signature is not None:
            representative_signature_path = self._get_signature_file()
            representative_signature.save(representative_signature_path)
        template_file_path = 'templates/hipaa_authorization_template.html'
        template_variables = {
            'research_subject_name': research_subject_name,
            'research_subject_email': research_subject_email,
            'research_subject_date': research_subject_date,
            'research_subject_signature': research_subject_signature_path,
            'representative_name': representative_name,
            'representative_date': representative_date,
            'representative_signature': representative_signature_path,
            'representative_relationship': representative_relationship
        }
        outfile = self._get_waiver_outfile()
        self._create_pdf('utf-16', template_file_path, template_variables, outfile)
        if os.path.isfile(research_subject_signature_path):
            os.remove(research_subject_signature_path)
        if os.path.isfile(representative_signature_path):
            os.remove(representative_signature_path)
        return outfile

    def generate_report(self, evaluation, attempts, name):
        sum_wsd = 0
        for attempt in attempts:
            sum_wsd += attempt['wsd']
        avg_wsd = sum_wsd / len(attempts)
        template_file_path = 'templates/report_template.html'
        template_variables = {
            'name': name,
            'evaluation_id': evaluation['evaluationId'],
            'date': evaluation['dateCreated'],
            'attempts': attempts,
            'total_wsd': '{0:.2f}'.format(avg_wsd),
            'gender': evaluation['gender'],
            'age': evaluation['age'],
            'impression': evaluation['impression']
        }
        outfile = self._get_report_outfile()
        self._create_pdf('utf-8', template_file_path, template_variables, outfile)
        return outfile

    @staticmethod
    def _create_pdf(encoding, template_file_path, template_variables, outfile):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        env = Environment(loader=FileSystemLoader(dir_path, encoding=encoding))
        template = env.get_template(template_file_path)
        html_out = template.render(template_variables)
        HTML(string=html_out, base_url='.').write_pdf(outfile)

    @staticmethod
    def _get_waiver_outfile():
        dir_path = os.path.join(tmp_storage_dir, 'waivers')
        file_name = uuid.uuid4().hex + '.pdf'
        return os.path.join(dir_path, file_name)

    @staticmethod
    def _get_signature_file(suffix='.png'):
        dir_path = os.path.join(tmp_storage_dir, 'signature_files')
        file_name = uuid.uuid4().hex + suffix
        return os.path.join(dir_path, file_name)

    @staticmethod
    def _get_report_outfile():
        dir_path = os.path.join(tmp_storage_dir, 'reports')
        file_name = uuid.uuid4().hex + '.pdf'
        return os.path.join(dir_path, file_name)
