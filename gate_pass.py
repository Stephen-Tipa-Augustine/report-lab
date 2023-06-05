import io

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from PIL import Image as PilImage
from reportlab.platypus import Table, Paragraph, Frame, ListFlowable, ListItem, Image

VERTICAL_MARGIN = 32
HORIZONTAL_MARGIN = 32


class GatePassTemplate:

    def __init__(self, response_type='file', filename='print-review.pdf'):
        if response_type == 'file':
            self.canvas = canvas.Canvas(filename)
        else:
            buffer = io.BytesIO()
            self.canvas = canvas.Canvas(buffer)
        self.page_width, self.page_height = self.canvas._pagesize
        self.table_frame = Frame(HORIZONTAL_MARGIN, VERTICAL_MARGIN, self.page_width - 2 * HORIZONTAL_MARGIN,
                                 self.page_height - 2 * VERTICAL_MARGIN - 135, showBoundary=0)
        self.styleSheet = getSampleStyleSheet()
        self.table_frame_content = []
        self.response_type = response_type
        self.types = ('official', 'personal', 'lunchtime')

    def draw_title(self, title):
        self.canvas.setFont("Helvetica", 16)
        self.canvas.drawCentredString(self.page_width / 2, self.page_height - VERTICAL_MARGIN - 135, title)

    def draw_logo(self):
        # Load the image
        image_path = "kmc-doc-logo.jpg"
        image = PilImage.open(image_path)
        aspect_ratio = image.width / image.height

        # Set the desired width and height of the image
        image_width = self.page_width - 160
        image_height = image_width / aspect_ratio

        # Calculate the x-coordinate to center the image horizontally
        x = (self.page_width - image_width) / 2

        # Set the y-coordinate at the top of the page
        y = self.page_height - 150

        # Draw the image on the canvas
        self.canvas.drawImage(image_path, x, y, width=image_width, height=image_height)

    def title_paragraph(self, title):
        return Paragraph('''
                   <para align=left fontSize=9 spaceb=3><b>{:}<font color=black></font></b></para>'''.format(title),
                         self.styleSheet["BodyText"])

    def list_item(self, text):
        return Paragraph('''
                       <para align=left fontSize=9 spaceb=3><bullet>{:}</bullet></para>'''.format(text),
                         self.styleSheet["BodyText"])

    def content_paragraph(self, text):
        return Paragraph('''
                   <para align=left fontSize=9 spaceb=3>{:}</para>'''.format(text),
                         self.styleSheet["BodyText"])

    def signature_label(self, text):
        return Paragraph('''
                   <para align=center fontSize=10 spaceBefore=0>{:}</para>'''.format(text),
                         self.styleSheet["BodyText"])

    @staticmethod
    def draw_signature(url):
        image = Image(url)
        image.drawHeight = .5 * inch * image.drawHeight / image.drawWidth
        image.drawWidth = .5 * inch
        return image

    @staticmethod
    def chosen_type():
        image = Image('tick.png')
        image.drawHeight = .4 * inch * image.drawHeight / image.drawWidth
        image.drawWidth = .4 * inch
        return image

    def draw_table(self, payload):
        reason_title = [self.title_paragraph('Reasons for leaving duty station during working hours:')]
        feedback_title = [self.title_paragraph('Feedback to the responsible supervising officer (For official duty '
                                               'only)')]
        reason_text = payload['reasons']
        feedback_text = payload['feedbacks']

        # Create a ListStyle with desired bullet style
        list_style = getSampleStyleSheet()["Bullet"]
        list_style.leftIndent = 12  # Indentation of the bullet list
        list_style.spaceAfter = 8  # Space after the bullet list
        list_style.textColor = colors.black  # Color of the bullet list text
        list_style.fontSize = 10  # Font size of the bullet list text

        # Create a ListFlowable with the data and style
        reason_list = ListFlowable(
            [ListItem(Paragraph(item, list_style), leftIndent=20, value="\u2022") for item in reason_text],
            bulletType="bullet",
            bulletColor=colors.black,  # Color of the bullet
            start=None,
            end=None,
            bulletFontSize=12,  # Font size of the bullet
            bulletOffsetY=-2,  # Offset of the bullet from the text baseline
            bulletDedent="auto",  # Dedentation of the bullet from the left
            bulletDir="ltr",  # Bullet direction (left-to-right)
        )
        feedback_list = ListFlowable(
            [ListItem(Paragraph(item, list_style), leftIndent=20, value="\u2022") for item in feedback_text],
            bulletType="bullet",
            bulletColor=colors.black,  # Color of the bullet
            start=None,
            end=None,
            bulletFontSize=12,  # Font size of the bullet
            bulletOffsetY=-2,  # Offset of the bullet from the text baseline
            bulletDedent="auto",  # Dedentation of the bullet from the left
            bulletDir="ltr",  # Bullet direction (left-to-right)
        )

        reasons = [reason_title, reason_list]
        feedbacks = [feedback_title, feedback_list]

        data = [[self.title_paragraph('STAFF NAME'), '', '', '', payload['name']],
                [self.title_paragraph('POSITION'), '', '', '', payload['position']],
                [self.title_paragraph('DEPARTMENT'), '', '', '', payload['department']],
                [self.title_paragraph('NAME OF SUPERVISION'), '', '', '', payload['supervisor_name']],
                [self.title_paragraph('SIGNATURE OF SUPERVISOR'), '', '', '', self.draw_signature(payload['supervisor_signature'])],
                [[self.title_paragraph('VEHICLE REG. NO'), self.content_paragraph('(Only Required for Official Duty)')],
                 '', '',
                 '',
                 self.content_paragraph(payload['vehicle_licence'])],
                [self.title_paragraph('DEPARTURE TIME'), '', '', '', self.content_paragraph(payload['departure_time'])],
                [self.title_paragraph('RETURN TIME'), '', '', '', self.content_paragraph(payload['return_time'])],
                [[self.title_paragraph('TYPE OF GATE PASS'), self.content_paragraph('(Check Appropriate Box)')], '',
                 self.title_paragraph('OFFICIAL'), self.chosen_type() if payload['type'] == 1 else '',
                 self.title_paragraph('PERSONAL'), self.chosen_type() if payload['type'] == 2 else '',
                 self.title_paragraph('LUNCHTIME'), self.chosen_type() if payload['type'] == 3 else ''],
                [reasons,
                 '', '', '',
                 feedbacks],
                [[self.draw_signature(payload['employee_approval']['signature']),
                  self.signature_label('---------------------------'),
                  self.signature_label('Signature')], '',
                 [self.signature_label(payload['employee_approval']['date']),
                  self.signature_label('---------------------------'),
                  self.signature_label('Date')], '',
                 [self.draw_signature(payload['feedback_approval']['signature']),
                  self.signature_label('---------------------------'),
                  self.signature_label('Signature')], '',
                 [self.signature_label(payload['feedback_approval']['date']),
                  self.signature_label('---------------------------'),
                  self.signature_label('Date')]]]
        t = Table(data, style=[('BOX', (0, 0), (-1, -1), 1, colors.black),
                               ('GRID', (0, 0), (-1, -2), 0.5, colors.black),
                               ("SPAN", (0, 0), (3, 0)),
                               ("SPAN", (0, 1), (3, 1)),
                               ("SPAN", (0, 2), (3, 2)),
                               ("SPAN", (0, 3), (3, 3)),
                               ("SPAN", (0, 4), (3, 4)),
                               ("SPAN", (0, 5), (3, 5)),
                               ("SPAN", (0, 6), (3, 6)),
                               ("SPAN", (0, 7), (3, 7)),
                               ("SPAN", (4, 0), (7, 0)),
                               ("SPAN", (4, 1), (7, 1)),
                               ("SPAN", (4, 2), (7, 2)),
                               ("SPAN", (4, 3), (7, 3)),
                               ("SPAN", (4, 4), (7, 4)),
                               ("SPAN", (4, 5), (7, 5)),
                               ("SPAN", (4, 6), (7, 6)),
                               ("SPAN", (4, 7), (7, 7)),
                               ("SPAN", (0, 9), (3, 9)),
                               ("SPAN", (4, 9), (7, 9)),
                               ("SPAN", (0, 10), (1, 10)),
                               ("SPAN", (2, 10), (3, 10)),
                               ("SPAN", (4, 10), (5, 10)),
                               ("SPAN", (6, 10), (7, 10)),
                               ("SPAN", (0, 8), (1, 8)),
                               ('VALIGN', (0, 0), (9, -1), 'MIDDLE'),
                               ('TOPPADDING', (0, 0), (-1, -1), 10),
                               ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                               ('ALIGN', (3, 8), (4, 9), 'CENTER'),
                               ('ALIGN', (5, 8), (6, 9), 'CENTER'),
                               ('ALIGN', (7, 8), (-1, 9), 'CENTER'),
                               ('ALIGN', (0, 10), (2, -1), 'CENTER'),
                               ('ALIGN', (4, 10), (6, -1), 'CENTER'),
                               ('VALIGN', (0, 10), (-1, -1), 'BOTTOM'),
                               ('LINEAFTER', (2, 10), (3, -1), 0.5, colors.black),
                               ])
        t._argW[3] = 1.5 * inch
        # Calculate the width of each column
        num_columns = 8  # Assuming all rows have the same number of columns
        column_width = self.table_frame.width / num_columns

        # Create a list of equal widths for all columns
        column_widths = [column_width] * num_columns
        # Set the column widths for the table
        t._argW = column_widths

        self.table_frame_content.append(t)

    def generate(self, data):
        self.draw_logo()
        self.draw_title('GATE PASS')
        self.draw_table(data)

        self.table_frame.addFromList(self.table_frame_content, self.canvas)
        self.canvas.save()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    form_data = {
        'name': 'Stephen Tipa Augustine',
        'position': 'DEN',
        'department': 'PD',
        'supervisor_name': 'Fred Matovu',
        'supervisor_signature': 'signature-2.png',
        'vehicle_licence': 'UG 1234Z',
        'departure_time': '10:25',
        'return_time': '13:44',
        'type': 1,
        'reasons': ('Am going to pick my certificate from Makerere University',
                       'I want to make tuition fee payment in the bank'),
        'feedbacks': ('I got my certificate', 'I completed my payment'),
        'employee_approval': {
            'signature': 'signature.png',
            'date': '02/06/2023'
        },
        'feedback_approval': {
            'signature': 'signature-2.png',
            'date': '02/06/2023'
        }
    }
    obj = GatePassTemplate(response_type='file', filename='print-review.pdf')
    obj.generate(form_data)
