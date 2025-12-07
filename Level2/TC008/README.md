## ASS3 - Data-driven Automation Testing

This project contains the implementation for Assignment 3 – data-driven automation testing for the Saucedemo website.

### Structure

```
ASS3/
├── TC-003/                    # Checkout test cases
│   ├── data/
│   │   ├── checkout_data.csv  # Test data for checkout tests
│   │   └── locators.csv       # Locators for checkout tests (Level 2)
│   ├── src/
│   │   ├── level1_checkout_datadriven.py
│   │   └── level2_checkout_datadriven.py
│   └── TC-003.krecorder       # Original Katalon Recorder test cases
│
├── TC-008/                    # Cart test cases
│   ├── data/
│   │   ├── cart_data.csv      # Test data for cart tests
│   │   └── locators.csv       # Locators for cart tests (Level 2)
│   ├── src/
│   │   ├── level1_cart_datadriven.py
│   │   └── level2_cart_datadriven.py
│   └── TC-008.krecorder       # Original Katalon Recorder test cases
│
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

### Setup

1. Install Python 3.10+.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Download `chromedriver` compatible with your Chrome version and place `chromedriver.exe` in the project root (`ASS3`) or adjust the path in the scripts.

### Run tests

From the `ASS3` directory:

**Checkout tests (TC-003):**
```bash
cd TC-003
python src/level1_checkout_datadriven.py
python src/level2_checkout_datadriven.py
```

**Cart tests (TC-008):**
```bash
cd TC-008
python src/level1_cart_datadriven.py
python src/level2_cart_datadriven.py
```

### Test Cases

- **TC-003**: Checkout form validation tests (7 test cases)
  - TC003_001: Missing first name validation
  - TC003_002: Valid data with short first name
  - TC003_003: Valid data with very long first name
  - TC003_004: Missing postal code validation
  - TC003_005: Valid data with "OK" values
  - TC003_006: All fields empty validation
  - TC003_007: Valid data with lowercase values

- **TC-008**: Cart functionality tests (7 test cases)
  - TC008_001: Navigate to cart and verify title
  - TC008_002: Add all 6 items and verify cart badge
  - TC008_003: Add item, verify in cart, continue shopping, verify remove button
  - TC008_004: Add item without login, verify error
  - TC008_005: Add one item and verify cart badge
  - TC008_006: Verify cart badge and remove item
  - TC008_007: Complex flow - add multiple items, remove items, verify buttons


