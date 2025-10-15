## 🧠 Overview
**eCourts Scraper** is a Python project that automates fetching case details from the official [eCourts India website](https://services.ecourts.gov.in/ecourtindia_v6/).  

It allows you to search by **CNR number**, scrape the case status page, and extract important details such as:

- **Case Type**
- **Filing Date**
- **Registration Number**
- **Next Hearing Date**
- **Court Name**
- **Petitioner and Respondent**

The results are saved in **JSON format** for easy access and automation.

---

## ⚙️ Requirements

1. **Python 3.8+**  
2. **Google Chrome** browser  

Create a virtual environment and install dependencies:


# Create virtual environment
```bash
python -m venv venv
```
# Activate virtual environment (Windows)
```bash
venv\Scripts\activate
```
# Activate virtual environment (Linux/Mac)
```bash
source venv/bin/activate
```
# Install dependencies
```bash
pip install -r requirements.txt
```

🚀 How to Run

Run the main script:
```bash
python ecourts_scraper.py
```

Enter your CNR number when asked, for example:
```bash
Enter CNR number (e.g., MHAU019999992015): TSHC050008262025
```

The program will:

Open the eCourts website in Chrome

Automatically fill your CNR number

Wait for you to manually solve the CAPTCHA and click Search

Scrape the case details

Save the results to a JSON file in the results/ folder

Example Output:
```bash
{
  "CNR": "TSHC050008262025",
  "checked_on": "2025-10-15T18:58:23",
  "results": {
    "case_type": "EP - EXECUTION PETITION",
    "filing_number": "1006/2025",
    "filing_date": "04-08-2025",
    "next_hearing_date": "18th November 2025",
    "court_name": "1-I Addl Chief Judge",
    "petitioner": "CHURCH OF SOUTH INDIA TRUST ASSOCIATION",
    "respondent": "THE STATE OF TELANGANA"
  }
}
```

## 🧩 Folder Structure
```bash
ecourts_scraper/
│
├── ecourts_scraper.py      # Main script
├── requirements.txt         # Dependencies
├── README.md                # Documentation
└── results/ (auto-created)  # Scraped results saved here
```
## 🧾 Notes

The site requires a CAPTCHA, so manual input is necessary.

The browser opens automatically; please do not close it until the program finishes.

The script runs in visible Chrome mode (not headless) for ease of captcha entry.

You can delete the results/ folder anytime; it will auto-generate again.

## 🏁 Author

- **Internship Project**: eCourts Scraper
- **Developed by**: S V Vishnu Vamsi
- **Date**: October 2025
