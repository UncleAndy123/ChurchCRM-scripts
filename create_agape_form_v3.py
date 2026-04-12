"""
Agape Church Directory Form v3
- Fixed label/field overlap (labels now clearly above fields)
- Member checkbox for every person
- 15 children rows
- Grandparents with Deceased field
- Occupation field
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

W, H = letter
M = 0.5 * inch          # left/right margin
C = W - 2 * M           # usable column width

NAVY  = colors.HexColor('#1a3560')
GOLD  = colors.HexColor('#c8a951')
PURP  = colors.HexColor('#4a148c')
TEAL  = colors.HexColor('#00695c')
LGRAY = colors.HexColor('#f5f5f5')
MGRAY = colors.HexColor('#bbbbbb')
WHITE = colors.white
BLACK = colors.black

# Row geometry — labels sit ABOVE fields with clear gap
SPACING = 2  # Gap between label and field (adjust this to change all spacing)
LBL_H  = 2   # label sits 2pt above field top
FLD_H  = 15   # field height
ROW_H  = 30   # total vertical step per row (label + field + gap)
SEC_H  = 20   # section header height + gap


def tf(c, name, x, y, w, h=FLD_H, tip='', multiline=False, comb=False):
    """Text field. y = TOP of field."""
    flags = []
    if multiline:
        flags.append('multiline')
    if comb:
        flags.append('comb')
    flags_str = ' '.join(flags) if flags else ''
    c.acroForm.textfield(
        name=name, tooltip=tip or name,
        x=x, y=y - h, width=w, height=h,
        value='', fieldFlags=flags_str,
        borderColor=MGRAY, fillColor=WHITE,
        textColor=BLACK, forceBorder=True, fontSize=9,
    )


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


def field_with_label(c, label_text, name, x, y, w, tip='', required=False, comb=False):
    """
    Draw label above field.
    y = TOP of the label text.
    Field sits below label with a SPACING gap.
    Returns x + w (right edge) for chaining.
    """
    req = ' *' if required else ''
    lbl(c, label_text + req, x, y, size=7)
    tf(c, name, x, y - SPACING, w, FLD_H, tip, comb=comb)
    return x + w


def cb_with_label(c, name, x, y, text='Member?'):
    """Checkbox with label above it."""
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
    # Return y of first label row, with gap below header
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
        field_with_label(c, 'Birthdate', f'{prefix}_birthdate', x, y, w - 4, tip='00/00/0000', comb=True)
        x += w

    # Deceased (grandparents)
    if show_deceased:
        w = C * 0.14
        field_with_label(c, 'Deceased?', f'{prefix}_deceased', x, y, w - 4, tip='Y or year')
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
    field_with_label(c, 'Family Last Name ', 'family_last_name',
                     x + C * 0.44, y, C * 0.56 - 2, required=False)
    y -= ROW_H

    # Address
    field_with_label(c, 'Street Address', 'address1', M, y, C * 0.64 - 4)
    #field_with_label(c, 'Address Line 2', 'address2', M + C * 0.66, y, C * 0.34 - 2)
    y -= ROW_H

    # City / State / ZIP / Country
    field_with_label(c, 'City', 'city', M, y, C * 0.40 - 4)
    field_with_label(c, 'State/Province', 'state', M + C * 0.42, y, C * 0.17 - 4)
    field_with_label(c, 'ZIP/Postal', 'zip', M + C * 0.61, y, C * 0.19 - 4)
    field_with_label(c, 'Country', 'country', M + C * 0.82, y, C * 0.18 - 2, tip='US / CA')
    y -= ROW_H

    # Phone / Wedding / Occupation
    field_with_label(c, 'Home Phone', 'home_phone', M, y, C * 0.28 - 4)
    field_with_label(c, 'Marriage Date', 'wedding_date',
                     M + C * 0.30, y, C * 0.20 - 4, tip='00/00/0000', comb=True)
    field_with_label(c, 'Occupation (head of household)', 'occupation', M + C * 0.52, y, C * 0.48 - 2)
    y -= ROW_H + 4

    # ── HEAD OF HOUSEHOLD ─────────────────
    y = sec(c, y, 'HEAD OF HOUSEHOLD')
    y = person_row(c, y, 'head', show_member=True,
                   name_label='First Name', required=False,
                   show_last=False, show_birthdate=True, show_email=True, show_mobile=True)
    y -= 4

    # ── SPOUSE ────────────────────────────
    y = sec(c, y, 'SPOUSE')
    y = person_row(c, y, 'spouse', show_member=True,
                   name_label='First Name',
                   show_last=False, show_birthdate=True, show_email=True, show_mobile=True)
    y -= 4

    # ── PATERNAL GRANDPARENTS ─────────────
    y = sec(c, y, "PATERNAL GRANDPARENTS  (Head of Household's parents)", PURP)
    y = person_row(c, y, 'pat_gf', show_member=True,
                   name_label='Grandfather First Name',
                   show_last=True, show_deceased=False)
    y = person_row(c, y, 'pat_gm', show_member=True,
                   name_label='Grandmother First Name',
                   show_last=True, last_label='Maiden Name', show_deceased=False)
    y -= 4

    # ── MATERNAL GRANDPARENTS ─────────────
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

    # Column header row
    c.setFillColor(colors.HexColor('#e8e8e8'))
    c.rect(M, y - 14, C, 14, fill=1, stroke=0)
    c.setFont('Helvetica-Bold', 7)
    c.setFillColor(colors.HexColor('#333333'))
    headers = [
        (M + 2,        '#'),
        (M + 22,       'First Name'),
        (M + C*0.26,   'Middle Name (or initial)'),
        (M + C*0.43,   'Birthdate (mm/dd/yyyy)'),
        (M + C*0.58,   'Spouse Name e.g. John L. Smith'),
        (M + C*0.84,   'Member?'),
    ]
    for hx, ht in headers:
        c.drawString(hx, y - 10, ht)
    y -= 18

    for i in range(1, 21):
        bg = LGRAY if i % 2 == 1 else WHITE
        row_h = 20
        c.setFillColor(bg)
        c.rect(M, y - row_h + 4, C, row_h, fill=1, stroke=0)

        # Row number
        c.setFillColor(colors.HexColor('#aaaaaa'))
        c.setFont('Helvetica', 7)
        c.drawString(M + 5, y - 8, str(i))

        p = f'child{i}'
        # Fields sit with top at y-1
        ft = y - 1
        tf(c, f'{p}_first',     M + 22,      ft, C*0.23 - 4, 14)
        tf(c, f'{p}_middle',    M + C*0.26,  ft, C*0.16 - 4, 14)
        tf(c, f'{p}_birthdate', M + C*0.43,  ft, C*0.12 - 4, 14, '00/00/0000', comb=True)
        tf(c, f'{p}_spouse',    M + C*0.58,  ft, C*0.25 - 4, 14,
           'Spouse name → PersonCustom:Married:')
        cb(c, f'{p}_member',    M + C*0.85,  ft + 1)

        y -= row_h

    y -= 10

    # ── NOTES ────────────────────────────
    y = sec(c, y, 'NOTES')
    tf(c, 'notes', M, y - 2, C - 2, 50, multiline=True)
    y -= 60

    # Disclaimer (2 paragraphs)
    disclaimer_height = 50
    c.setFillColor(colors.HexColor('#f0f0f0'))
    c.rect(M, y - disclaimer_height, C, disclaimer_height, fill=1, stroke=0)
    c.setFillColor(colors.HexColor("#464545"))
    c.setFont('Helvetica', 7.5)
    # Paragraph 1
    c.drawString(M + 6, y - 10,
        '')
    c.drawString(M + 6, y - 18,
        'Fill out the form as completely as possible. Leave blank any fields that do not apply to you. Add any other relevant information in the Notes section. ')
    c.drawString(M + 6, y - 26,
                 'Please note that the member check box applies to being a member at any Agape church, not necessarily the one you attend.')
    # Paragraph 2
    c.drawString(M + 6, y - 34,
        'Please verify all information is correct and spelled as you want it to appear in the directory then submit theform to the contact below.')
    y -= 50

    # ── SUBMITTER CONTACT ─────────────────
    y = sec(c, y, 'FORM SUBMISSION CONTACT')
    field_with_label(c, 'Name', 'submitter_name', M, y, C * 0.50 - 4)
    field_with_label(c, 'Email Address', 'submitter_email', M + C * 0.52, y, C * 0.48 - 2)
    field_with_label(c, 'Submission Deadline', 'submission_deadline', M, y - ROW_H, C * 0.25 - 2)
    draw_footer(c, 2, 2)
    c.showPage()
    c.save()
    print(f'Saved: {path}')


if __name__ == '__main__':
       build(r'C:\Users\AndrewTravel\Downloads\Agape_Church_Directory_Form_v4.pdf')
