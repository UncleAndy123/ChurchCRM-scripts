"""
Agape Church Directory Form v6
Base: v3 (multi-box dates, comb fields, all original layout)
Change: Children spouse name split into First Name / Middle Initial / Last Name

This script generates a fillable PDF form for church family information collection.
The form includes sections for family info, head of household, spouse, grandparents, and children.
"""

# ════════════════════════════════════════════════════════════════════════════════
# IMPORTS
# ════════════════════════════════════════════════════════════════════════════════
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

# ════════════════════════════════════════════════════════════════════════════════
# PAGE LAYOUT & DIMENSIONS
# ════════════════════════════════════════════════════════════════════════════════
W, H = letter  # Page width and height (8.5" x 11")
M = 0.5 * inch  # Left/right margin
C = W - 2 * M  # Content width (usable area)

# ════════════════════════════════════════════════════════════════════════════════
# COLOR PALETTE
# ════════════════════════════════════════════════════════════════════════════════
NAVY  = colors.HexColor('#1a3560')  # Primary heading color
GOLD  = colors.HexColor('#c8a951')  # Accent stripe on section headers
PURP  = colors.HexColor('#4a148c')  # Paternal grandparents section color
TEAL  = colors.HexColor('#00695c')  # Maternal grandparents section color
LGRAY = colors.HexColor('#f5f5f5')  # Light gray for alternating rows
MGRAY = colors.HexColor('#bbbbbb')  # Medium gray for form borders
WHITE = colors.white               # White background
BLACK = colors.black               # Black text

# ════════════════════════════════════════════════════════════════════════════════
# FORM GEOMETRY (vertical spacing, field dimensions)
# ════════════════════════════════════════════════════════════════════════════════
SPACING = 2     # Gap between label and field (points)
LBL_H  = 2      # Label height
FLD_H  = 15     # Standard field height
ROW_H  = 30     # Vertical step per row (label + field + gap)
SEC_H  = 20     # Section header height + gap


# ════════════════════════════════════════════════════════════════════════════════
# FORM FIELD CREATION FUNCTIONS
# ════════════════════════════════════════════════════════════════════════════════

def tf(c, name, x, y, w, h=FLD_H, tip='', multiline=False, comb=False, maxlen=0):
    """Create a text field in the PDF form.
    
    Args:
        c: Canvas object
        name: Field name (used for form submission)
        x, y: Position (y = top of field)
        w: Field width
        h: Field height (default: FLD_H=15pt)
        tip: Tooltip text
        multiline: Allow multiple lines if True
        comb: Use comb field (fixed-width character boxes) if True
        maxlen: Maximum character limit (0 = unlimited)
    """
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
    """Create a date field as 3 separate comb fields (MM/DD/YYYY).
    
    Slashes are drawn as static text on the page, so they remain visible
    when the PDF is viewed in Microsoft Edge (which sometimes hides field borders).
    
    Args:
        c: Canvas object
        name: Base field name (fields created as {name}_mm, {name}_dd, {name}_yyyy)
        x, y: Position (y = top of field area)
        w: Total width for all 3 fields plus slashes
        h: Field height
        tip: Tooltip text
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
    """Create a checkbox field.
    
    Args:
        c: Canvas object
        name: Field name
        x, y: Position (y = top of checkbox)
        tip: Tooltip text
    """
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
    """Draw a label text on the page.
    
    Args:
        c: Canvas object
        text: Label text to display
        x, y: Position (y = baseline of text)
        size: Font size in points
        bold: Use bold font if True
        color: Text color (default: dark gray)
    """
    c.setFillColor(color or colors.HexColor('#333333'))
    c.setFont('Helvetica-Bold' if bold else 'Helvetica', size)
    c.drawString(x, y, text)


def field_with_label(c, label_text, name, x, y, w, tip='', required=False, comb=False, maxlen=None):
    """Create a labeled text field (label above field).
    
    Args:
        c: Canvas object
        label_text: Label to display above field
        name: Field name
        x, y: Position (y = top of label)
        w: Field width
        tip: Tooltip for the field
        required: Add asterisk (*) to label if True
        comb: Use comb field format if True
        maxlen: Maximum characters (None = unlimited)
        
    Returns:
        x + w: Right edge position for chaining
    """
    req = ' *' if required else ''
    lbl(c, label_text + req, x, y, size=7)
    tf(c, name, x, y - SPACING, w, FLD_H, tip, comb=comb, maxlen=maxlen)
    return x + w


def cb_with_label(c, name, x, y, text='Member?'):
    """Create a labeled checkbox (label above checkbox).
    
    Args:
        c: Canvas object
        name: Field name
        x, y: Position (y = top of label)
        text: Label text
    """
    lbl(c, text, x, y, size=7)
    cb(c, name, x, y - SPACING)


def sec(c, y, title, color=NAVY):
    """Draw a section header bar with colored background.
    
    Args:
        c: Canvas object
        y: Y position for section header
        title: Section title text
        color: Background color (default: NAVY)
        
    Returns:
        y coordinate for first content row below header
    """
    # Draw colored background bar
    c.setFillColor(color)
    c.rect(M, y - SEC_H + 4, C, SEC_H - 2, fill=1, stroke=0)
    # Draw gold accent stripe on left
    c.setFillColor(GOLD)
    c.rect(M, y - SEC_H + 4, 4, SEC_H - 2, fill=1, stroke=0)
    # Draw white title text
    c.setFillColor(WHITE)
    c.setFont('Helvetica-Bold', 8.5)
    c.drawString(M + 10, y - 10, title)
    # Return y position for content below header
    return y - SEC_H - 2


def draw_header(c):
    """Draw the page header with title and contact information.
    
    Args:
        c: Canvas object
    """
    # Navy background bar
    c.setFillColor(NAVY)
    c.rect(0, H - 0.85*inch, W, 0.85*inch, fill=1, stroke=0)
    # Gold accent line
    c.setFillColor(GOLD)
    c.rect(0, H - 0.9*inch, W, 0.05*inch, fill=1, stroke=0)
    # Main title
    c.setFillColor(WHITE)
    c.setFont('Helvetica-Bold', 16)
    c.drawCentredString(W/2, H - 0.44*inch, 'Agape Church Directory')
    # Subtitle
    c.setFont('Helvetica', 9)
    c.drawCentredString(W/2, H - 0.60*inch, 'Family Information Form')
    # Contact info
    c.setFont('Helvetica', 7.5)
    c.setFillColor(colors.HexColor('#aaaaaa'))
    c.drawCentredString(W/2, H - 0.76*inch,
                        'Questions? Contact agapecfdirectory@outlook.com')


def draw_footer(c, page, total):
    """Draw the page footer with copyright and page numbers.
    
    Args:
        c: Canvas object
        page: Current page number
        total: Total number of pages
    """
    # Light gray background bar
    c.setFillColor(colors.HexColor('#e0e0e0'))
    c.rect(0, 0, W, 0.28*inch, fill=1, stroke=0)
    # Footer text (copyright and page number)
    c.setFillColor(colors.HexColor('#888888'))
    c.setFont('Helvetica', 7)
    c.drawCentredString(W/2, 0.13*inch, 'Agape Christian Fellowships 2026.')
    c.drawCentredString(W/2, 0.05*inch, f'Page {page} of {total}')


def person_row(c, y, prefix, show_member=True,
               name_label='First Name', required=False,
               show_last=True, last_label='Last Name', show_email=False,
               show_mobile=False, show_deceased=False, show_birthdate=False):
    """Draw a flexible person data row with name fields and optional details.
    
    Args:
        c: Canvas object
        y: Starting Y position (top of row)
        prefix: Field name prefix (e.g., 'head', 'spouse', 'pat_gf')
        show_member: Include member checkbox if True
        name_label: Label for first name field
        required: Mark fields as required if True
        show_last: Include last name field if True
        last_label: Label for last name field
        show_email: Include email field if True
        show_mobile: Include mobile phone field if True
        show_deceased: Include deceased field if True
        show_birthdate: Include birthdate field if True
        
    Returns:
        New Y position after this row
    """
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

    # Deceased (grandparents)
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
    """Generate the PDF form and save to the specified path.
    
    Args:
        path: Output file path for the PDF
    """
    c = canvas.Canvas(path, pagesize=letter)
    c.setTitle('Agape Church Directory Form')

    # ╔════════════════════════════════════════════════════════════════════════╗
    # ║ PAGE 1: FAMILY INFORMATION, HEAD OF HOUSEHOLD, SPOUSE, GRANDPARENTS     ║
    # ╚════════════════════════════════════════════════════════════════════════╝
    draw_header(c)
    y = H - 0.96 * inch

    # ══════════════════════════════════════════════════════════════════════════
    # FAMILY INFORMATION SECTION
    # ══════════════════════════════════════════════════════════════════════════
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

    # ══════════════════════════════════════════════════════════════════════════
    # HEAD OF HOUSEHOLD SECTION
    # ══════════════════════════════════════════════════════════════════════════
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

    # ╔════════════════════════════════════════════════════════════════════════╗
    # ║ PAGE 2: CHILDREN, NOTES, AND SUBMISSION CONTACT INFORMATION             ║
    # ╚════════════════════════════════════════════════════════════════════════╝
    draw_header(c)
    y = H - 0.96 * inch

    # ══════════════════════════════════════════════════════════════════════════
    # CHILDREN SECTION
    # ══════════════════════════════════════════════════════════════════════════
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
    
    # Save the PDF to disk
    c.save()
    print(f'Saved: {path}')


# ════════════════════════════════════════════════════════════════════════════════
# MAIN EXECUTION
# ════════════════════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    # Generate the PDF form
    build(r'C:\Users\AndrewTravel\Downloads\Agape_Church_Directory_Form_v6.1.pdf')
