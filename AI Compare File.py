"""
Agape Church Directory Form v6
Base: v3 (multi-box dates, comb fields, all original layout)
Change: Children spouse name split into First Name / Middle Initial / Last Name
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

W, H = letter
M = 0.5 * inch
C = W - 2 * M

NAVY  = colors.HexColor('#1a3560')
GOLD  = colors.HexColor('#c8a951')
PURP  = colors.HexColor('#4a148c')
TEAL  = colors.HexColor('#00695c')
LGRAY = colors.HexColor('#f5f5f5')
MGRAY = colors.HexColor('#bbbbbb')
WHITE = colors.white
BLACK = colors.black

SPACING = 2
LBL_H  = 2
FLD_H  = 15
ROW_H  = 30
SEC_H  = 20


def tf(c, name, x, y, w, h=FLD_H, tip='', multiline=False, comb=False, maxlen=0):
    """Text field. y = TOP of field."""
    flags = []
    if multiline:
        flags.append('multiline')
    if comb:
        flags.append('comb')
    flags_str = ' '.join(flags) if flags else ''
 
    kwargs = dict(
        name=name, tooltip=tip or name,
        x=x, y=y - h, width=w, height=h,
        value='', fieldFlags=flags_str,
        borderColor=MGRAY, fillColor=WHITE,
        textColor=BLACK, forceBorder=True, fontSize=9,
        maxlen=maxlen,
    )
 
    c.acroForm.textfield(**kwargs)
 


def date_tf(c, name, x, y, w, h=FLD_H, tip='MM/DD/YYYY'):
    """
    Draw a date as 3 separate fields: MM / DD / YYYY
    Slashes are static page text between fields, so they remain visible in Edge.
    y = TOP of field area.
    """
    slash_gap = 6
    total_slash_space = slash_gap * 2

    unit = (w - total_slash_space) / 8.0
    mm_w   = unit * 2
    dd_w   = unit * 2
    yyyy_w = unit * 4

    x1 = x
    x2 = x1 + mm_w + slash_gap
    x3 = x2 + dd_w + slash_gap

    tf(c, f'{name}_mm',   x1, y, mm_w,   h, tip='MM',   comb=True, maxlen=2)
    tf(c, f'{name}_dd',   x2, y, dd_w,   h, tip='DD',   comb=True, maxlen=2)
    tf(c, f'{name}_yyyy', x3, y, yyyy_w, h, tip='YYYY', comb=True, maxlen=4)

    c.saveState()
    c.setFont('Helvetica', 9)
    c.setFillColor(colors.HexColor('#666666'))
    slash_y = y - h + 4
    c.drawCentredString(x1 + mm_w + slash_gap / 2.0, slash_y, '/')
    c.drawCentredString(x2 + dd_w + slash_gap / 2.0, slash_y, '/')
    c.restoreState()


def cb(c, name, x, y, tip='Member'):
    """Checkbox. y = TOP of box."""
    size = 11
    c.acroForm.checkbox(
        name=name, tooltip=tip,
        x=x, y=y - size, size=size,
        checked=False,
        borderColor=MGRAY, fillColor=WHITE,
        textColor=NAVY, forceBorder=True,
        buttonStyle='check',
    )


def lbl(c, text, x, y, size=7, bold=False, color=None):
    """Label. y = baseline of text."""
    c.setFillColor(color or colors.HexColor('#333333'))
    c.setFont('Helvetica-Bold' if bold else 'Helvetica', size)
    c.drawString(x, y, text)


def field_with_label(c, label_text, name, x, y, w, tip='', required=False, comb=False, maxlen=None):
    req = ' *' if required else ''
    lbl(c, label_text + req, x, y, size=7)
    tf(c, name, x, y - SPACING, w, FLD_H, tip, comb=comb, maxlen=maxlen)
    return x + w


def cb_with_label(c, name, x, y, text='Member?'):
    lbl(c, text, x, y, size=7)
    cb(c, name, x, y - SPACING - 11)


def sec(c, y, title, color=NAVY):
    c.setFillColor(color)
    c.rect(M, y - SEC_H + 4, C, SEC_H - 2, fill=1, stroke=0)
    c.setFillColor(GOLD)
    c.rect(M, y - SEC_H + 4, 4, SEC_H - 2, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont('Helvetica-Bold', 8.5)
    c.drawString(M + 10, y - 10, title)
    return y - SEC_H - 2


def draw_header(c):
    c.setFillColor(NAVY)
    c.rect(0, H - 0.85*inch, W, 0.85*inch, fill=1, stroke=0)
    c.setFillColor(GOLD)
    c.rect(0, H - 0.9*inch, W, 0.05*inch, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont('Helvetica-Bold', 16)
    c.drawCentredString(W/2, H - 0.44*inch, 'Agape Church Directory')
    c.setFont('Helvetica', 9)
    c.drawCentredString(W/2, H - 0.60*inch, 'Family Information Form')
    c.setFont('Helvetica', 7.5)
    c.setFillColor(colors.HexColor('#aaaaaa'))
    c.drawCentredString(W/2, H - 0.76*inch,
                        'Questions? Contact agapecfdirectory@outlook.com')


def draw_footer(c, page, total):
    c.setFillColor(colors.HexColor('#e0e0e0'))
    c.rect(0, 0, W, 0.28*inch, fill=1, stroke=0)
    c.setFillColor(colors.HexColor('#888888'))
    c.setFont('Helvetica', 7)
    c.drawCentredString(W/2, 0.13*inch, 'Agape Christian Fellowships 2026.')
    c.drawCentredString(W/2, 0.05*inch, f'Page {page} of {total}')


def person_row(c, y, prefix, show_member=True,
               name_label='First Name', required=False,
               show_last=True, last_label='Last Name', show_email=False,
               show_mobile=False, show_deceased=False, show_birthdate=False):
    x = M

    w = C * (0.22 if show_last else 0.28)
    field_with_label(c, name_label, f'{prefix}_first', x, y, w - 4, required=required)
    x += w

    w = C * 0.16
    field_with_label(c, 'Middle Initial', f'{prefix}_middle', x, y, w - 4)
    x += w

    if show_last:
        w = C * 0.20
        field_with_label(c, last_label, f'{prefix}_last', x, y, w - 4)
        x += w

    if show_birthdate:
        w = C * 0.15
        lbl(c, 'Birthdate', x, y, size=7)
        date_tf(c, f'{prefix}_birthdate', x, y - SPACING, w - 4, FLD_H)
        x += w

    if show_deceased:
        w = C * 0.14
        field_with_label(c, 'Deceased?', f'{prefix}_deceased', x, y, w - 4, tip='Y or year')
        x += w

    if show_member:
        gap = M + C - x - 18
        if gap < 0:
            gap = 0
        cb_with_label(c, f'{prefix}_member', x + gap, y, 'Member?')

    y -= ROW_H

    if show_email or show_mobile:
        x = M
        if show_email:
            w = C * 0.55
            field_with_label(c, 'Email Address', f'{prefix}_email', x, y, w - 4)
            x += w
        if show_mobile:
            w = M + C - x
            field_with_label(c, 'Mobile Phone', f'{prefix}_mobile', x, y, w - 4)
        y -= ROW_H

    return y


def build(path):
    c = canvas.Canvas(path, pagesize=letter)
    c.setTitle('Agape Church Directory Form')

    # ══════════════════════════════════════
    # PAGE 1
    # ══════════════════════════════════════
    draw_header(c)
    y = H - 0.96 * inch

    y = sec(c, y, 'FAMILY INFORMATION')

    x = M
    field_with_label(c, 'Church Name', 'church_name', x, y, C * 0.42 - 4)
    field_with_label(c, 'Family Last Name ', 'family_last_name',
                     x + C * 0.44, y, C * 0.56 - 2, required=False)
    y -= ROW_H

    field_with_label(c, 'Street Address', 'address1', M, y, C * 0.64 - 4)
    y -= ROW_H

    field_with_label(c, 'City', 'city', M, y, C * 0.40 - 4)
    field_with_label(c, 'State/Province', 'state', M + C * 0.42, y, C * 0.17 - 4)
    field_with_label(c, 'ZIP/Postal', 'zip', M + C * 0.61, y, C * 0.19 - 4)
    field_with_label(c, 'Country', 'country', M + C * 0.82, y, C * 0.18 - 2, tip='US / CA')
    y -= ROW_H

    field_with_label(c, 'Home Phone', 'home_phone', M, y, C * 0.28 - 4)
    lbl(c, 'Marriage Date', M + C * 0.30, y, size=7)
    date_tf(c, 'wedding_date', M + C * 0.30, y - SPACING, C * 0.20 - 4, FLD_H)
    field_with_label(c, 'Occupation (head of household)', 'occupation',
                     M + C * 0.52, y, C * 0.48 - 2)
    y -= ROW_H + 4

    y = sec(c, y, 'HEAD OF HOUSEHOLD')
    y = person_row(c, y, 'head', show_member=True,
                   name_label='First Name', required=False,
                   show_last=False, show_birthdate=True, show_email=True, show_mobile=True)
    y -= 4

    y = sec(c, y, 'SPOUSE')
    y = person_row(c, y, 'spouse', show_member=True,
                   name_label='First Name',
                   show_last=False, show_birthdate=True, show_email=True, show_mobile=True)
    y -= 4

    y = sec(c, y, "PATERNAL GRANDPARENTS  (Head of Household's parents)", PURP)
    y = person_row(c, y, 'pat_gf', show_member=True,
                   name_label='Grandfather First Name',
                   show_last=True, show_deceased=False)
    y = person_row(c, y, 'pat_gm', show_member=True,
                   name_label='Grandmother First Name',
                   show_last=True, last_label='Maiden Name', show_deceased=False)
    y -= 4

    y = sec(c, y, "MATERNAL GRANDPARENTS  (Spouse's parents)", TEAL)
    y = person_row(c, y, 'mat_gf', show_member=True,
                   name_label='Grandfather First Name',
                   show_last=True, show_deceased=False)
    y = person_row(c, y, 'mat_gm', show_member=True,
                   name_label='Grandmother First Name',
                   show_last=True, last_label='Maiden Name', show_deceased=False)

    draw_footer(c, 1, 2)
    c.showPage()

    # ══════════════════════════════════════
    # PAGE 2 — CHILDREN
    # ══════════════════════════════════════
    draw_header(c)
    y = H - 0.96 * inch

    y = sec(c, y, 'CHILDREN  (up to 20 — leave blank rows empty)')

    # Column x anchors for spouse split
    SP_FST_X = M + C * 0.58
    SP_MI_X  = M + C * 0.71
    SP_LST_X = M + C * 0.77
    MBR_X    = M + C * 0.89

    # Column header bar
    c.setFillColor(colors.HexColor('#e8e8e8'))
    c.rect(M, y - 14, C, 14, fill=1, stroke=0)
    c.setFont('Helvetica-Bold', 7)
    c.setFillColor(colors.HexColor('#333333'))
    for hx, ht in [
        (M + 2,       '#'),
        (M + 22,      'First Name'),
        (M + C*0.26,  'Middle Name'),
        (M + C*0.43,  'Birthdate (mm/dd/yyyy)'),
        (SP_FST_X,    'Spouse First'),
        (SP_MI_X,     'MI'),
        (SP_LST_X,    'Spouse Last Name'),
        (MBR_X,       'Member?'),
    ]:
        c.drawString(hx, y - 10, ht)
    y -= 18

    # Child rows
    for i in range(1, 21):
        bg = LGRAY if i % 2 == 1 else WHITE
        row_h = 20
        c.setFillColor(bg)
        c.rect(M, y - row_h + 4, C, row_h, fill=1, stroke=0)

        c.setFillColor(colors.HexColor('#aaaaaa'))
        c.setFont('Helvetica', 7)
        c.drawString(M + 5, y - 8, str(i))

        p  = f'child{i}'
        ft = y - 1

        # Name
        tf(c, f'{p}_first',        M + 22,      ft, C*0.23 - 4,              14)
        tf(c, f'{p}_middle',       M + C*0.26,  ft, C*0.14 - 4,              14)

        # Birthdate (comb split-date boxes)
        date_tf(c, f'{p}_birthdate', M + C*0.43, ft, C*0.12 - 4, 14)

        # Spouse: First / MI / Last
        tf(c, f'{p}_spouse_first', SP_FST_X,    ft, SP_MI_X  - SP_FST_X - 4, 14)
        tf(c, f'{p}_spouse_mi',    SP_MI_X,     ft, SP_LST_X - SP_MI_X  - 4, 14)
        tf(c, f'{p}_spouse_last',  SP_LST_X,    ft, MBR_X    - SP_LST_X - 6, 14)

        cb(c, f'{p}_member', MBR_X, ft + 1)

        y -= row_h

    y -= 10

    # NOTES
    y = sec(c, y, 'NOTES')
    tf(c, 'notes', M, y - 2, C - 2, 50, multiline=True)
    y -= 60

    # Disclaimer
    disclaimer_height = 50
    c.setFillColor(colors.HexColor('#f0f0f0'))
    c.rect(M, y - disclaimer_height, C, disclaimer_height, fill=1, stroke=0)
    c.setFillColor(colors.HexColor('#464545'))
    c.setFont('Helvetica', 7.5)
    c.drawString(M + 6, y - 10, '')
    c.drawString(M + 6, y - 18,
        'Fill out the form as completely as possible. Leave blank any fields that do not apply '
        'to you. Add any other relevant information in the Notes section.')
    c.drawString(M + 6, y - 26,
        'Please note that the member check box applies to being a member at any Agape church, '
        'not necessarily the one you attend.')
    c.drawString(M + 6, y - 34,
        'Please verify all information is correct and spelled as you want it to appear in the '
        'directory then submit the form to the contact below.')
    y -= 50

    # Form Submission Contact
    y = sec(c, y, 'FORM SUBMISSION CONTACT')
    field_with_label(c, 'Name',                'submitter_name',      M,            y, C * 0.50 - 4)
    field_with_label(c, 'Email Address',       'submitter_email',     M + C * 0.52, y, C * 0.48 - 2)
    field_with_label(c, 'Submission Deadline', 'submission_deadline', M,            y - ROW_H, C * 0.25 - 2)

    draw_footer(c, 2, 2)
    c.showPage()
    c.save()
    print(f'Saved: {path}')


if __name__ == '__main__':
       build(r'C:\Users\AndrewTravel\Downloads\Agape_Church_Directory_Form_v6.1.pdf')
