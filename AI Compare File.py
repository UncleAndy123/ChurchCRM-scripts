"""
Agape Church Directory Form v6
Changes from v5:
  - Notes field is a tall scrollable multiline box (unlimited text)
  - Children spouse split into: First Name / Middle Initial / Last Name
  - Disclaimer text cleaned up (removed blank first line)
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
FLD_H   = 15
ROW_H   = 30
SEC_H   = 20

DATE_PLACEHOLDER = '__/__/____'


def tf(c, name, x, y, w, h=FLD_H, tip='', value='', multiline=False):
    """Text field. y = TOP of field."""
    c.acroForm.textfield(
        name=name, tooltip=tip or name,
        x=x, y=y - h, width=w, height=h,
        value=value,
        fieldFlags='multiline' if multiline else '',
        borderColor=MGRAY, fillColor=WHITE,
        textColor=BLACK, forceBorder=True, fontSize=9,
    )


def date_field(c, name, x, y, w, h=FLD_H):
    """Date field pre-filled with __/__/____ so slashes are visible."""
    tf(c, name, x, y, w, h, tip='mm/dd/yyyy', value=DATE_PLACEHOLDER)


def cb(c, name, x, y, tip='Member'):
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
    c.setFillColor(color or colors.HexColor('#333333'))
    c.setFont('Helvetica-Bold' if bold else 'Helvetica', size)
    c.drawString(x, y, text)


def field_with_label(c, label_text, name, x, y, w,
                     tip='', required=False, is_date=False):
    req = ' *' if required else ''
    lbl(c, label_text + req, x, y, size=7)
    if is_date:
        date_field(c, name, x, y - SPACING, w)
    else:
        tf(c, name, x, y - SPACING, w, FLD_H, tip)
    return x + w


def cb_with_label(c, name, x, y, text='Member?'):
    lbl(c, text, x, y, size=7)
    cb(c, name, x, y - SPACING - 11)


def sec(c, y, title, color=NAVY):
    """Section header bar. Returns y for first content row (top of label)."""
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
               show_last=True, last_label='Last/Maiden Name', show_email=False,
               show_mobile=False, show_deceased=False, show_birthdate=False):
    """
    Draw a generic person row: name + birthdate + [member checkbox].
    y = top of label row.
    Returns new y after this row.
    """
    # Row 1: First / Middle / [Last] / Birthdate / [Member checkbox]
    col_widths = []
    x = M

    # First name
    w = C * (0.22 if show_last else 0.28)
    field_with_label(c, name_label, f'{prefix}_first', x, y, w - 4, required=required)
    x += w

    # Middle
    w = C * 0.16
    field_with_label(c, 'Middle Initial', f'{prefix}_middle', x, y, w - 4)
    x += w

    # Optional Last / Maiden
    if show_last:
        w = C * 0.20
        field_with_label(c, last_label, f'{prefix}_last', x, y, w - 4)
        x += w

    # Birthdate (optional)
    if show_birthdate:
        w = C * 0.15
        field_with_label(c, 'Birthdate', f'{prefix}_birthdate', x, y, w - 4,
                         tip='mm/dd/yyyy', is_date=True)
        x += w

    # Deceased (grandparents)
    if show_deceased:
        w = C * 0.14
        field_with_label(c, 'Deceased?', f'{prefix}_deceased', x, y, w - 4,
                         tip='Y or year')
        x += w

    # Member checkbox
    if show_member:
        gap = M + C - x - 18
        if gap < 0:
            gap = 0
        cb_with_label(c, f'{prefix}_member', x + gap, y, 'Member?')

    y -= ROW_H

    # Optional row 2: Email + Mobile
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

    # ── FAMILY INFORMATION ────────────────
    y = sec(c, y, 'FAMILY INFORMATION')

    # Church Name / Family Last Name
    x = M
    field_with_label(c, 'Church Name', 'church_name', x, y, C * 0.42 - 4)
    field_with_label(c, 'Family Last Name', 'family_last_name',
                     x + C * 0.44, y, C * 0.56 - 2)
    y -= ROW_H

    # Address
    field_with_label(c, 'Street Address', 'address1', M, y, C * 0.64 - 4)
    #field_with_label(c, 'Address Line 2', 'address2', M + C * 0.66, y, C * 0.34 - 2)
    y -= ROW_H

    # City / State / ZIP / Country
    field_with_label(c, 'City',           'city',    M,             y, C * 0.40 - 4)
    field_with_label(c, 'State/Province', 'state',   M + C * 0.42,  y, C * 0.17 - 4)
    field_with_label(c, 'ZIP/Postal',     'zip',     M + C * 0.61,  y, C * 0.19 - 4)
    field_with_label(c, 'Country',        'country', M + C * 0.82,  y, C * 0.18 - 2,
                     tip='US / CA')
    y -= ROW_H

    field_with_label(c, 'Home Phone',    'home_phone',   M,            y, C * 0.28 - 4)
    field_with_label(c, 'Marriage Date', 'wedding_date', M + C * 0.30, y, C * 0.20 - 4,
                     is_date=True)
    field_with_label(c, 'Occupation (head of household)', 'occupation',
                     M + C * 0.52, y, C * 0.48 - 2)
    y -= ROW_H + 4

    # ── HEAD OF HOUSEHOLD ─────────────────

    y = sec(c, y, 'HEAD OF HOUSEHOLD')
    y = person_row(c, y, 'head', show_last=False,
                   show_birthdate=True, show_email=True, show_mobile=True)
    y -= 4

    # ── SPOUSE ────────────────────────────

    y = sec(c, y, 'SPOUSE')
    y = person_row(c, y, 'spouse', show_last=False,
                   show_birthdate=True, show_email=True, show_mobile=True)
    y -= 4

    # ── PATERNAL GRANDPARENTS ─────────────

    y = sec(c, y, "PATERNAL GRANDPARENTS  (Head of Household's parents)", PURP)
    y = person_row(c, y, 'pat_gf', name_label='Grandfather First Name', show_last=True)
    y = person_row(c, y, 'pat_gm', name_label='Grandmother First Name',
                   show_last=True, last_label='Maiden Name')
    y -= 4

    # ── MATERNAL GRANDPARENTS ─────────────
    y = sec(c, y, "MATERNAL GRANDPARENTS  (Spouse's parents)", TEAL)
    y = person_row(c, y, 'mat_gf', name_label='Grandfather First Name', show_last=True)
    y = person_row(c, y, 'mat_gm', name_label='Grandmother First Name',
                   show_last=True, last_label='Maiden Name')

    draw_footer(c, 1, 2)
    c.showPage()

    # ══════════════════════════════════════
    # PAGE 2 — CHILDREN
    # ══════════════════════════════════════
    draw_header(c)
    y = H - 0.96 * inch

    y = sec(c, y, 'CHILDREN  (up to 20 — leave blank rows empty)')

    # ── Column header row ─────────────────
    # Layout proportions for child rows:
    #   #          : fixed ~20px
    #   First      : C*0.23
    #   Middle     : C*0.13
    #   Birthdate  : C*0.12
    #   Sp. First  : C*0.13
    #   Sp. MI     : C*0.06
    #   Sp. Last   : C*0.11
    #   Member     : ~18px checkbox

    SP_FIRST_X = M + C * 0.58
    SP_MI_X    = M + C * 0.71
    SP_LAST_X  = M + C * 0.77
    MBR_X      = M + C * 0.88

    c.setFillColor(colors.HexColor('#e8e8e8'))
    c.rect(M, y - 14, C, 14, fill=1, stroke=0)
    c.setFont('Helvetica-Bold', 7)
    c.setFillColor(colors.HexColor('#333333'))
    for hx, ht in [
        (M + 2,          '#'),
        (M + 22,         'First Name'),
        (M + C * 0.26,   'Middle Name'),
        (M + C * 0.43,   'Birthdate (mm/dd/yyyy)'),
        (SP_FIRST_X,     'Spouse First'),
        (SP_MI_X,        'MI'),
        (SP_LAST_X,      'Spouse Last Name'),
        (MBR_X,          'Member?'),
    ]:
        c.drawString(hx, y - 10, ht)
    y -= 18

    # ── Child rows ────────────────────────
    for i in range(1, 21):
        c.setFillColor(LGRAY if i % 2 == 1 else WHITE)
        c.rect(M, y - 16, C, 20, fill=1, stroke=0)
        c.setFillColor(colors.HexColor('#aaaaaa'))
        c.setFont('Helvetica', 7)
        c.drawString(M + 5, y - 8, str(i))

        p  = f'child{i}'
        ft = y - 1

        # Name fields
        tf(c, f'{p}_first',            M + 22,       ft, C * 0.23 - 4, 14)
        tf(c, f'{p}_middle',           M + C * 0.26, ft, C * 0.13 - 4, 14)

        # Birthdate
        date_field(c, f'{p}_birthdate', M + C * 0.43, ft, C * 0.12 - 4, 14)

        # Spouse: First / MI / Last  (replaces single spouse name field)
        tf(c, f'{p}_spouse_first',     SP_FIRST_X,   ft, C * 0.13 - 4, 14)
        tf(c, f'{p}_spouse_mi',        SP_MI_X,      ft, C * 0.06 - 4, 14)
        tf(c, f'{p}_spouse_last',      SP_LAST_X,    ft, C * 0.11 - 4, 14)

        # Member checkbox
        cb(c, f'{p}_member',           MBR_X,        ft + 1)

        y -= 20

    y -= 10

    # ── NOTES ────────────────────────────
    # Tall scrollable multiline field — users can type as much as they want.
    NOTES_H = 100
    y = sec(c, y, 'NOTES')
    tf(c, 'notes', M, y - 2, C - 2, NOTES_H, multiline=True,
       tip='Type as much as needed — scroll to read more.')
    y -= NOTES_H + 10

    # ── Disclaimer ────────────────────────
    disclaimer_height = 42
    c.setFillColor(colors.HexColor('#f0f0f0'))
    c.rect(M, y - disclaimer_height, C, disclaimer_height, fill=1, stroke=0)
    c.setFillColor(colors.HexColor('#464545'))
    c.setFont('Helvetica', 7.5)
    # Paragraph 1
    c.drawString(M + 6, y - 10,
        'Fill out the form as completely as possible. Leave blank any fields that do not apply to you. '
        'Add any other relevant information in the Notes section.')
    c.drawString(M + 6, y - 20,
        'Please note that the member check box applies to being a member at any Agape church, '
        'not necessarily the one you attend.')
    c.drawString(M + 6, y - 30,
        'Please verify all information is correct and spelled as you want it to appear in the '
        'directory then submit the form to the contact below.')
    y -= disclaimer_height + 4

    # ── FORM SUBMISSION CONTACT ───────────
    y = sec(c, y, 'FORM SUBMISSION CONTACT')
    field_with_label(c, 'Name',                'submitter_name',      M,            y, C * 0.50 - 4)
    field_with_label(c, 'Email Address',       'submitter_email',     M + C * 0.52, y, C * 0.48 - 2)
    field_with_label(c, 'Submission Deadline', 'submission_deadline', M,            y - ROW_H, C * 0.30 - 2)

    draw_footer(c, 2, 2)
    c.showPage()
    c.save()
    print(f'Saved: {path}')


if __name__ == '__main__':
       build(r'C:\Users\AndrewTravel\Downloads\Agape_Church_Directory_Form_v4.9.pdf')
