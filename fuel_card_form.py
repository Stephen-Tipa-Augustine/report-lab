import io

from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, Paragraph, Frame, ListFlowable, Image, TableStyle, Spacer

VERTICAL_MARGIN = 32
HORIZONTAL_MARGIN = 32


class FuelFormTemplate:

    def __init__(self, response_type='file', filename='print-review.pdf'):
        if response_type == 'file':
            self.canvas = canvas.Canvas(filename, pagesize=landscape(A4))
        else:
            buffer = io.BytesIO()
            self.canvas = canvas.Canvas(buffer, pagesize=landscape(A4))
        self.page_width, self.page_height = self.canvas._pagesize
        self.logo_frame = Frame(HORIZONTAL_MARGIN, (self.page_height - 2 * VERTICAL_MARGIN) * 0.83,
                                (self.page_width - 2 * HORIZONTAL_MARGIN) / 2,
                                (self.page_height - 2 * VERTICAL_MARGIN) * 0.2, showBoundary=1)
        self.vehicle_frame = Frame(HORIZONTAL_MARGIN + (self.page_width - 2 * HORIZONTAL_MARGIN) / 2,
                                   (self.page_height - 2 * VERTICAL_MARGIN) * 0.83,
                                   (self.page_width - 2 * HORIZONTAL_MARGIN) / 2,
                                   (self.page_height - 2 * VERTICAL_MARGIN) * 0.2, showBoundary=1)
        self.body_frame = Frame(HORIZONTAL_MARGIN, VERTICAL_MARGIN, self.page_width - 2 * HORIZONTAL_MARGIN,
                                (self.page_height - 2 * VERTICAL_MARGIN) * 0.76, showBoundary=1)
        self.styleSheet = getSampleStyleSheet()
        self.logo_frame_content = []
        self.vehicle_frame_content = []
        self.body_frame_content = []
        self.response_type = response_type

    def draw_logo(self):
        image = Image('kmc-doc-logo.jpg')
        image.drawHeight = 4.25 * inch * image.drawHeight / image.drawWidth
        image.drawWidth = 4.25 * inch
        self.logo_frame_content.append(image)

    def draw_vehicle_info(self, info):
        data = [['FUEL CARD MANAGEMENT FORM', ''],
                ['VEHICLE REG NO.', info['vehicle_licence']],
                ['MAKE/MODEL', info['vehicle_model']],
                ['ENGINE CAPACITY (CC)', info['engine_capacity']],
                ['FUEL CARD NO.', info['fuel_card_no']]]
        t = Table(data)
        t.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                               ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                               ('GRID', (0, 0), (-1, -1), 1, colors.black),
                               ('SPAN', (0, 0), (-1, 1)),
                               ('ALIGN', (0, 0), (-1, 1), 'CENTER'),
                               ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
                               ('TOPPADDING', (0, 0), (-1, -1), 5),
                               ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                               ]))
        # Calculate the width of each column
        num_columns = 2  # Assuming all rows have the same number of columns
        column_width = self.vehicle_frame.width / num_columns
        # Create a list of equal widths for all columns
        column_widths = [column_width] * num_columns
        # Set the column widths for the table
        t._argW = column_widths
        self.vehicle_frame_content.append(t)

    def draw_approval_info(self, info):
        data = [[self.underlined_paragraph('<b>Prepared By</b>'), self.underlined_paragraph('<b>Checked By</b>'),
                 self.underlined_paragraph('<b>Approved By</b>')],
                [self.content_paragraph(f"<b>Name:</b> {info['prepared']['name']}"),
                 self.content_paragraph(f"<b>Name:</b> {info['checked']['name']}"),
                 self.content_paragraph(f"<b>Name:</b> {info['approved']['name']}")],
                [self.content_paragraph(f"<b>Position:</b> {info['prepared']['position']}"),
                 self.content_paragraph(f"<b>Position:</b> {info['prepared']['position']}"),
                 self.content_paragraph(f"<b>Position:</b> {info['prepared']['position']}")],
                [self.signature_date({'signature': info['prepared']['signature'], 'date': info['prepared']['date']}),
                 self.signature_date({'signature': info['checked']['signature'], 'date': info['prepared']['date']}),
                 self.signature_date({'signature': info['approved']['signature'], 'date': info['prepared']['date']})]]
        t = Table(data)
        t.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                               ('BOX', (0, 0), (-1, -1), 1, colors.black),
                               ('LINEAFTER', (0, 0), (1, -1), 1, colors.black),
                               ('LINEAFTER', (2, 0), (1, -1), 1, colors.black),
                               ('ALIGN', (0, 0), (-1, 1), 'CENTER'),
                               ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
                               ('TOPPADDING', (0, 0), (-1, -1), 3),
                               ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                               ('BOTTOMPADDING', (0, 2), (-1, 2), 12),
                               ]))
        # Calculate the width of each column
        num_columns = 3  # Assuming all rows have the same number of columns
        column_width = self.body_frame.width / num_columns
        # Create a list of equal widths for all columns
        column_widths = [column_width] * num_columns
        # Set the column widths for the table
        t._argW = column_widths
        self.body_frame_content.append(t)

    def draw_accountability_info(self, info):
        data = [[self.underlined_paragraph('Accountability Checked By'),
                 self.underlined_paragraph('Accountability Verified By')],
                [self.accountability_signature(info['checked']), self.accountability_signature(info['verified'])]]
        t = Table(data)
        t.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                               ('BOX', (0, 0), (-1, -1), 1, colors.black),
                               ('ALIGN', (0, 0), (-1, 1), 'CENTER'),
                               ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
                               ('LINEAFTER', (0, 0), (1, -1), 1, colors.black),
                               ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                               ]))
        # Calculate the width of each column
        num_columns = 2  # Assuming all rows have the same number of columns
        column_width = self.body_frame.width / num_columns
        # Create a list of equal widths for all columns
        column_widths = [column_width] * num_columns
        # Set the column widths for the table
        t._argW = column_widths
        self.body_frame_content.append(t)

    def draw_agreement_info(self):
        self.body_frame_content.append(self.underlined_paragraph('Fuel Card User Agreement'))
        self.body_frame_content.append(Spacer(1, 0.05 * inch))
        agreement_list = ListFlowable(
            [
                self.content_paragraph(
                    'I understand that I will make financial commitments on behalf of KMC by using '
                    'the fuel card issued to me.'),
                self.content_paragraph('I understand that I have to take all possible measures to secure the fuel '
                                       'card in my possession to protect it against loss, theft or damage.'),
                self.content_paragraph(
                    'I understand that under no circumstances will i make fuel purchases not dully '
                    'authorized, either for myself or others. Willful intent to use the fuel card for '
                    'personal gain will result into disciplinary action up to and including '
                    'termination of my employment at KMC and criminal prosecution.'),
                self.content_paragraph('I will follow established procedures for using the KMC fuel card including '
                                       'retention and timely submission of receipts for all fuel purchases along with '
                                       'the '
                                       'fuel card upon return from this journey.'),
                self.content_paragraph(
                    'I agree to coordinate with the Department of Operational Support in auditing '
                    'and any investigations related to my fuel card usage.'),
                self.content_paragraph('I will not reveal any information relating to the PIN Number to any third '
                                       'party including the fuel pump attendant either in writing or verbally.')
            ],
            bulletType='1'
        )
        data = [[agreement_list]]
        t = Table(data)
        t.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                               ('BOX', (0, 0), (-1, -1), 1, colors.black),
                               ('TOPPADDING', (0, 0), (-1, -1), 3),
                               ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                               ]))
        # Calculate the width of each column
        num_columns = 1  # Assuming all rows have the same number of columns
        column_width = self.body_frame.width / num_columns
        # Create a list of equal widths for all columns
        column_widths = [column_width] * num_columns
        # Set the column widths for the table
        t._argW = column_widths
        self.body_frame_content.append(t)
        self.body_frame_content.append(Spacer(1, 0.1 * inch))

    def draw_business_info(self, info):
        data = [[self.content_paragraph('<b>SN</b>'), self.content_paragraph('<b>DATE</b>'),
                 self.content_paragraph('<b>BUSINESS PURPOSE</b>'), self.title_paragraph('DISTANCE (KM) (ATTACH MAP)'),
                 self.content_paragraph('<b>RATE (UGX)</b>'),
                 self.content_paragraph('<b>AMOUNT (UGX)</b>')],
                ['1', info['date'], self.content_paragraph(info['purpose']), info['distance'], info['rate'],
                 info['amount']], ['Total', info['amount']],
                [self.content_paragraph('<b>Approved Amount in Words</b>'), '',
                 info['amount_in_words'], self.content_paragraph('<b>Amount Not Taken</b>'),
                 '', info['amount_not_taken']]]
        t = Table(data)
        t.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                               ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                               ('GRID', (0, 0), (-1, -1), 1, colors.black),
                               ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                               ('ALIGN', (4, 1), (4, 1), 'RIGHT'),
                               ('ALIGN', (5, 1), (-1, -1), 'RIGHT'),
                               ('TOPPADDING', (0, 0), (-1, -1), 2),
                               ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                               ('SPAN', (0, 3), (1, 3)),
                               ('SPAN', (0, 2), (4, 2)),
                               ('SPAN', (3, 3), (4, 3))
                               ]))
        # Calculate the width of each column
        num_columns = 6  # Assuming all rows have the same number of columns
        column_width = self.body_frame.width / num_columns
        # Create a list of equal widths for all columns
        column_widths = [column_width * 0.2, column_width * 0.9, column_width * 3, column_width * 0.7,
                         column_width * 0.6,
                         column_width * 0.6]
        # Set the column widths for the table
        t._argW = column_widths
        self.body_frame_content.append(t)
        self.body_frame_content.append(Spacer(1, 0.2 * inch))

    def title_paragraph(self, title):
        return Paragraph('''
                   <para align=left fontSize=9 spaceb=3><b>{:}<font color=black></font></b></para>'''.format(title),
                         self.styleSheet["BodyText"])

    def content_paragraph(self, text):
        return Paragraph('''
                   <para align=left fontSize=9 spaceb=3>{:}</para>'''.format(text),
                         self.styleSheet["BodyText"])

    def receipt_acknowledgement(self, info):
        signature = self.make_image_responsive(info['signature'])
        benefactor_signature = self.make_image_responsive(info['benefactor_signature'])
        p = Paragraph('''
                   <para align=left fontSize=9 align="left">I {:} (Signature:   <img src="{:}" width="{:}" height="{:}" 
                   />  ) acknowledge receipt of KMC Fuel Card No. {:} from {:} (Signature:   <img src="{:}" width="{:}" 
                   height="{:}" />  ) 
                   Date: {:}</para>'''.format(info['name'], info['signature'], signature[0], signature[1],
                                              info['card_number'], info['benefactor'],
                                              info['benefactor_signature'], benefactor_signature[0],
                                              benefactor_signature[1], info['date']),
                      self.styleSheet["BodyText"])
        self.body_frame_content.append(p)
        self.body_frame_content.append(Spacer(1, 0.1 * inch))

    def underlined_paragraph(self, text):
        return Paragraph('''
                   <para align=left fontSize=10 align="center"><u>{:}</u></para>'''.format(text),
                         self.styleSheet["BodyText"])

    def signature_label(self, text):
        return Paragraph('''
                   <para align=center fontSize=10 spaceBefore=0>{:}</para>'''.format(text),
                         self.styleSheet["BodyText"])

    def accountability_signature(self, info):
        signature = self.make_image_responsive(info['signature'])
        p = Paragraph('''
                   <para align=left fontSize=9 align="left"><b>Name:</b> {:}  <b>Signature:</b> <img src="{:}" width="{:}" 
                   height="{:}" />  <b>Date:</b> {:}</para>'''.format(info['name'], info['signature'], signature[0],
                                                               signature[1], info['date']),
                      self.styleSheet["BodyText"])
        return p

    def signature_date(self, info):
        signature = self.make_image_responsive(info['signature'])
        p = Paragraph('''
                   <para align=left fontSize=9 align="left"><b>Signature:</b> <img src="{:}" width="{:}" 
                   height="{:}" />  <b>Date:</b> {:}</para>'''.format(info['signature'], signature[0],
                                                                      signature[1], info['date']),
                      self.styleSheet["BodyText"])
        return p

    @staticmethod
    def draw_signature(url):
        image = Image(url)
        image.drawHeight = .5 * inch * image.drawHeight / image.drawWidth
        image.drawWidth = .5 * inch
        return image

    @staticmethod
    def make_image_responsive(url):
        image = Image(url)
        image.drawHeight = .5 * inch * image.drawHeight / image.drawWidth
        image.drawWidth = .5 * inch
        return image.drawWidth, image.drawHeight

    def generate(self, data):
        self.draw_logo()
        self.draw_vehicle_info(data['vehicle'])
        self.draw_business_info(data['business'])
        self.draw_approval_info(data['approval'])
        self.draw_agreement_info()
        self.receipt_acknowledgement(data['receipt'])
        self.draw_accountability_info(data['accountability'])

        self.logo_frame.addFromList(self.logo_frame_content, self.canvas)
        self.vehicle_frame.addFromList(self.vehicle_frame_content, self.canvas)
        self.body_frame.addFromList(self.body_frame_content, self.canvas)
        self.canvas.save()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    form_data = {
        'vehicle': {
            'vehicle_licence': 'UAY 452L',
            'vehicle_model': 'TOYOTA NOAH',
            'engine_capacity': '2000 CC',
            'fuel_card_no': '00012'
        },
        'business': {
            'date': '05.05.2023',
            'purpose': 'Travel to Ndeeba, John Lugendo for engine work',
            'distance': '10.5',
            'rate': '5,000',
            'amount': '52,500',
            'amount_in_words': 'Fifty Two Thousand Five Hundred Shillings Only',
            'amount_not_taken': ''
        },
        'approval': {
            'prepared': {
                'name': 'Agness Kabatesi',
                'position': 'Senior Administration Officer',
                'signature': 'signature-2.png',
                'date': '02/06/2023'
            },
            'checked': {
                'name': 'Sandra Ampumuza',
                'position': 'Senior Accountant',
                'signature': 'signature-2.png',
                'date': '02/06/2023'
            },
            'approved': {
                'name': 'Arthur Tumusiime Asiimwe',
                'position': 'Director Operational Support',
                'signature': 'signature-2.png',
                'date': '02/06/2023'
            }
        },
        'receipt': {
            'name': 'Agness Kabatesi',
            'signature': 'signature-2.png',
            'card_number': '012',
            'benefactor': 'Stephen Tipa Augustine',
            'benefactor_signature': 'signature.png',
            'date': '02/06/2023'
        },
        'accountability': {
            'checked': {
                'name': 'Agness Kabatesi',
                'signature': 'signature-2.png',
                'date': '02/06/2023'
            },
            'verified': {
                'name': 'Sandra Ampumuza',
                'signature': 'signature-2.png',
                'date': '02/06/2023'
            }
        }
    }
    obj = FuelFormTemplate(response_type='file', filename='fuel-form-print-review.pdf')
    obj.generate(form_data)
