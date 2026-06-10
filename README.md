# ChurchCRM Scripts

A collection of Python automation scripts for managing Agape Church Directory and ChurchCRM data.

## Overview

This repository contains utility scripts to streamline church member data collection, conversion, and import workflows. The primary use case is converting filled PDF church directory forms to CSV files for import into ChurchCRM systems.

## Scripts

### 1. **agape_converter_gui_v4.py** (Latest Converter)
The main GUI application for converting church directory PDF forms to CSV format.

**Features:**
- 🖱️ **Drag & Drop Support** — Easily add multiple PDF files
- 📋 **Preview Panel** — Review extracted data with color-coded family roles
- 📊 **Bulk Export** — Export single or multiple family records as CSV
- ✅ **Data Validation** — Automatic date and phone number normalization
- 🎨 **User-Friendly Interface** — Intuitive tkinter-based GUI

**Requirements:**
```bash
pip install pypdf
pip install tkinterdnd2  # Optional: for drag & drop support
```

**Usage:**
```bash
python agape_converter_gui_v4.py
```

**Workflow:**
1. Add filled PDF forms by dragging & dropping or clicking "Browse for PDFs…"
2. Review extracted data in the preview panel
3. Click color-coded family members to see details:
   - 🔵 Blue = Head of Household
   - 🔴 Pink = Spouse
   - 🟣 Purple = Grandparents
   - 🟢 Green = Children
4. Export as CSV for import into ChurchCRM

**CSV Output Columns:**
- Family Information: `FamilyID`, `FamilyRole`, `Address1`, `City`, `State`, `Zip`, `Country`
- Personal Details: `Title`, `FirstName`, `MiddleName`, `LastName`, `Suffix`, `Gender`
- Contact: `HomePhone`, `WorkPhone`, `MobilePhone`, `Email`, `WorkEmail`
- Important Dates: `BirthDate`, `MembershipDate`, `WeddingDate`
- Classification & Custom Fields: `Classification`, `PersonCustom:Married:`, `PersonCustom:Occupation:`, `FamilyCustom:CustomField1`

---

### 2. **AI Compare File.py**
Generates the Agape Church Directory PDF form template using ReportLab.

**Features:**
- 📄 **Multi-Page Form** — 2-page interactive PDF form
- 📋 **Dynamic Fields** — Support for head of household, spouse, grandparents, and up to 20 children
- 🎨 **Professional Design** — Navy and gold branding with organized sections
- 🔲 **Interactive Elements** — Fillable text fields, checkboxes, and date fields

**Requirements:**
```bash
pip install reportlab
```

**Usage:**
```bash
python "AI Compare File.py"
```

**Generated Form Sections:**
- Family Information (address, phone, marriage date, occupation)
- Head of Household (with email and mobile)
- Spouse (with email and mobile)
- Paternal Grandparents
- Maternal Grandparents
- Children (rows for 20 children with spouse information)
- Notes & Submission Contact

---

### 3. **Legacy Versions**
- `agape_converter_gui.py` — Original converter version
- `agape_converter_gui_v2.py` — Version 2 with enhancements
- `create_agape_form_v3.py` — Earlier form generation version

---

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/UncleAndy123/ChurchCRM-scripts.git
   cd ChurchCRM-scripts
   ```

2. **Install dependencies:**
   ```bash
   pip install pypdf reportlab
   ```

3. **Optional - Enable drag & drop:**
   ```bash
   pip install tkinterdnd2
   ```

---

## Quick Start

### Convert PDF Forms to CSV

```bash
python agape_converter_gui_v4.py
```

Then follow the in-app prompts to:
1. Add your filled PDF forms
2. Review the extracted data
3. Export to CSV
4. Import into ChurchCRM (Admin ⚙ → CSV Import)

### Generate a Church Directory Form

```bash
python "AI Compare File.py"
```

This creates an interactive PDF form ready for distribution.

---

## ChurchCRM Import Guide

After exporting CSV from the converter:

1. Open ChurchCRM
2. Navigate to **Admin ⚙ → CSV Import**
3. Upload your exported CSV file
4. Enable **"Generate Family records by Last Name + Address"**
5. Review and confirm the import

---

## Data Normalization

The converter automatically handles:
- **Phone Numbers**: Converts to `(XXX) XXX-XXXX` format
- **Dates**: Normalizes to `YYYY-MM-DD` format (accepts multiple input formats)
- **Classifications**: Checkbox status → "Member" or "Regular Attender"

---

## Field Mapping

| Form Field | CSV Output | Notes |
|------------|-----------|-------|
| Member Checkbox | `Classification` | ✓ = Member, ✗ = Regular Attender |
| Children's Spouse Name | `PersonCustom:Married:` | Spouse name of child |
| Occupation | `PersonCustom:Occupation:` | Head of household only |
| Notes | `FamilyCustom:CustomField1` | Free-form family notes |

---

## Requirements

- **Python 3.7+**
- **Dependencies:**
  - `pypdf` — PDF reading & manipulation
  - `reportlab` — PDF generation
  - `tkinterdnd2` — (Optional) Drag & drop support

---

## Troubleshooting

### Drag & drop not working?
The app will still work with the "Browse for PDFs…" button. To enable drag & drop:
```bash
pip install tkinterdnd2
```

### "Empty Form" warning?
Ensure the PDF was:
- Properly filled out (text entered in fields)
- Saved after filling (many PDF readers don't auto-save)
- Compatible with v4 form template

### Encoding issues with special characters?
The CSV export uses UTF-8 encoding. Most spreadsheet applications handle this automatically.

---

## Support & Contact

For issues or questions about the Agape Church Directory form:
📧 **agapecfdirectory@outlook.com**

---

## License

This project is provided as-is for use by Agape Christian Fellowships. Please contact the church for licensing information.

---

## Version History

| Version | Script | Date | Changes |
|---------|--------|------|---------|
| v4 | `agape_converter_gui_v4.py` | Latest | Enhanced GUI with color-coded preview, improved export |
| v2 | `agape_converter_gui_v2.py` | | Multi-version support |
| v1 | `agape_converter_gui.py` | | Original converter |
| Form v6 | `AI Compare File.py` | | Split children spouse name fields |

---

**Last Updated:** 2026-04-25

**Made with ❤️ for Agape Christian Fellowships**
