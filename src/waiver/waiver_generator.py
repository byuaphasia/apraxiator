from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import uuid
import os


class WaiverGenerator:
    def create_pdf_report(self, research_subject_name, research_subject_email, research_subject_date,
                          research_subject_signature, representative_name, representative_relationship,
                          representative_date, representative_signature):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        research_subject_signature_path = ''
        representative_signature_path = ''
        if research_subject_signature is not None:
            research_subject_signature_path = self.get_tmpfile()
            research_subject_signature.save(research_subject_signature_path)
        if representative_signature is not None:
            representative_signature_path = self.get_tmpfile()
            representative_signature.save(representative_signature_path)

        env = Environment(loader=FileSystemLoader(dir_path, encoding='utf-16'))
        template = env.get_template('waiver_template.html', )
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
        html_out = template.render(template_variables)
        outfile = self.get_outfile()

        HTML(string=html_out, base_url='.').write_pdf(outfile)
        if os.path.isfile(research_subject_signature_path):
            os.remove(research_subject_signature_path)
        if os.path.isfile(representative_signature_path):
            os.remove(representative_signature_path)

        return outfile

    @staticmethod
    def get_outfile():
        dir_path = os.path.dirname(os.path.realpath(__file__)) + '/signed_waivers/'
        file_name = uuid.uuid4().hex + '.pdf'
        return os.path.join(dir_path, file_name)

    @staticmethod
    def get_tmpfile(suffix='.png'):
        dir_path = os.path.dirname(os.path.realpath(__file__)) + '/tmp/'
        file_name = uuid.uuid4().hex + suffix
        return os.path.join(dir_path, file_name)
