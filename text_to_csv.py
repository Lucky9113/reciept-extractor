import argparse
import re
import csv
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from collections import Counter

# Download required NLTK data
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)

def extract_invoice_fields_regex(text):
    """Extract invoice fields using regex patterns"""
    
    fields = {}
    
    # 1. Vendor Name - Look for company names (usually in caps or with Ltd/Inc)
    vendor_patterns = [
        r'([A-Z][A-Za-z\s&]+(?:Ltd|Inc|Corporation|Corp|International|Limited))',
        r'SONICWALL[^\n]*\n([A-Za-z\s]+(?:Ltd|Inc|International))',
        r'From:\s*([A-Za-z\s]+(?:Ltd|Inc|International))'
    ]
    vendor_name = extract_with_patterns(text, vendor_patterns)
    fields['Vendor Name'] = vendor_name if vendor_name else 'null'
    
    # 2. PO Number - Purchase Order Number
    po_patterns = [
        r'Purchase Order Number[:\s]+(\d+)',
        r'PO[:\s#]+(\d+)',
        r'P\.O\.[:\s#]+(\d+)'
    ]
    po_number = extract_with_patterns(text, po_patterns)
    fields['PO Number'] = po_number if po_number else 'null'
    
    # 3. PO Date - Look for dates near PO
    date_patterns = [
        r'(\d{1,2}[-/]\w{3}[-/]\d{4})',
        r'(\d{1,2}[-/]\d{1,2}[-/]\d{4})',
        r'(\d{4}[-/]\d{1,2}[-/]\d{1,2})'
    ]
    po_date = extract_with_patterns(text, date_patterns)
    fields['PO Date'] = po_date if po_date else 'null'
    
    # 4. Document Number - Invoice/Document number
    doc_patterns = [
        r'Invoice Number[:\s]+(\w+)',
        r'Document Number[:\s]+(\w+)',
        r'Invoice[:\s#]+(\w+)'
    ]
    doc_number = extract_with_patterns(text, doc_patterns)
    fields['Document Number'] = doc_number if doc_number else 'null'
    
    # 5. Document Date - Same as PO date for now
    fields['Document Date'] = fields['PO Date']
    
    # 6. Bill To - Extract first line after "Bill To:"
    bill_to_pattern = r'Bill To:\s*\n([^\n]+)'
    bill_to = extract_with_patterns(text, [bill_to_pattern])
    fields['Bill To (First Line)'] = bill_to if bill_to else 'null'
    
    # 7. Ship To - Extract first line after "Ship To:"
    ship_to_pattern = r'Ship To:\s*\n([^\n]+)'
    ship_to = extract_with_patterns(text, [ship_to_pattern])
    fields['Ship To (First Line)'] = ship_to if ship_to else 'null'
    
    # 8. Payment Terms - Extract numeric part
    terms_patterns = [
        r'Net\s+(\d+)',
        r'Terms[:\s]+Net\s+(\d+)',
        r'Payment Terms[:\s]+(\d+)'
    ]
    payment_terms = extract_with_patterns(text, terms_patterns)
    fields['Payment Terms (numeric part)'] = payment_terms if payment_terms else 'null'
    
    # 9-11. Default null for missing fields
    fields['Mode of Shipment'] = 'null'
    fields['Transaction Type'] = 'null'
    fields['HS Code'] = 'null'
    
    # 12. Part Number - Look for product codes
    part_patterns = [
        r'(\d{2}-[A-Z]{3}-\d{4})',
        r'Part[:\s#]+([A-Z0-9-]+)',
        r'SKU[:\s#]+([A-Z0-9-]+)'
    ]
    part_no = extract_with_patterns(text, part_patterns)
    fields['Part No'] = part_no if part_no else 'null'
    
    # 13. Quantity - Look for quantity numbers
    qty_patterns = [
        r'Qty[:\s]+(\d+)',
        r'Quantity[:\s]+(\d+)',
        r'\s(\d+)\s+\d+[.,]\d{2}\s+\d+[.,]\d{2}'  # Table format
    ]
    qty = extract_with_patterns(text, qty_patterns)
    fields['Qty Ordered'] = qty if qty else 'null'
    
    # 14. Unit Price - Look for price format
    price_patterns = [
        r'Unit Price[:\s]+(\d+[.,]\d{2})',
        r'(\d+[.,]\d{2})\s+\d+[.,]\d{2}$',  # Table format
        r'Price[:\s]+(\d+[.,]\d{2})'
    ]
    unit_price = extract_with_patterns(text, price_patterns)
    fields['Unit Price'] = unit_price.replace(',', '') if unit_price else 'null'
    
    # 15. Net Amount - Look for subtotal/net amount
    net_patterns = [
        r'Subtotal[:\s]+(\d+[.,]\d{2})',
        r'Net Amount[:\s]+(\d+[.,]\d{2})',
        r'(\d+[.,]\d{2})\s+0\s*$'  # Amount before tax
    ]
    net_amount = extract_with_patterns(text, net_patterns)
    fields['Net Amount'] = net_amount.replace(',', '') if net_amount else 'null'
    
    # 16. Tax/VAT Amount
    tax_patterns = [
        r'VAT[:\s]+(\d+[.,]\d{2})',
        r'Tax[:\s]+(\d+[.,]\d{2})',
        r'GST[:\s]+(\d+[.,]\d{2})'
    ]
    tax_amount = extract_with_patterns(text, tax_patterns)
    fields['Tax/VAT Amount'] = tax_amount.replace(',', '') if tax_amount else '0'
    
    # 17. Total Invoice Amount
    total_patterns = [
        r'Total[:\s]+(\d+[.,]\d{2})',
        r'Amount Due[:\s]+(\d+[.,]\d{2})',
        r'Invoice Total[:\s]+(\d+[.,]\d{2})'
    ]
    total_amount = extract_with_patterns(text, total_patterns)
    fields['Total Invoice Amount'] = total_amount.replace(',', '') if total_amount else 'null'
    
    # 18. Due Date
    due_patterns = [
        r'Due Date[:\s]+(\d{1,2}[-/]\w{3}[-/]\d{2,4})',
        r'Payment Due[:\s]+(\d{1,2}[-/]\w{3}[-/]\d{2,4})'
    ]
    due_date = extract_with_patterns(text, due_patterns)
    fields['Due Date'] = due_date if due_date else 'null'
    
    return fields

def extract_with_patterns(text, patterns):
    """Try multiple regex patterns and return first match"""
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            return match.group(1).strip()
    return None

def enhance_with_nltk(text, extracted_fields):
    """Use NLTK to enhance extraction with context analysis"""
    
    # Tokenize and find important terms
    tokens = word_tokenize(text.lower())
    stop_words = set(stopwords.words('english'))
    important_tokens = [w for w in tokens if w.isalnum() and w not in stop_words]
    
    # Find most common terms (could indicate vendor/product names)
    common_terms = Counter(important_tokens).most_common(10)
    
    # Enhance vendor name if not found
    if extracted_fields['Vendor Name'] == 'null':
        # Look for capitalized company-like terms
        company_indicators = ['ltd', 'inc', 'corp', 'international', 'limited']
        for term, freq in common_terms:
            if any(indicator in term.lower() for indicator in company_indicators):
                extracted_fields['Vendor Name'] = term.title()
                break
    
    return extracted_fields

def validate_extraction(fields):
    """Validate extracted fields and perform calculations"""
    
    # Validate Net Amount = Qty * Unit Price
    try:
        if (fields['Qty Ordered'] != 'null' and 
            fields['Unit Price'] != 'null' and 
            fields['Net Amount'] != 'null'):
            
            qty = float(fields['Qty Ordered'])
            unit_price = float(fields['Unit Price'])
            net_amount = float(fields['Net Amount'])
            calculated_net = qty * unit_price
            
            if abs(calculated_net - net_amount) > 0.01:
                print(f"Warning: Net amount validation failed. "
                      f"Calculated: {calculated_net}, Found: {net_amount}")
    except ValueError:
        print("Warning: Could not validate numeric fields")
    
    return fields

def save_to_csv(fields, output_file):
    """Save extracted fields to CSV file"""
    
    # Define the field order
    field_order = [
        'Vendor Name', 'PO Number', 'PO Date', 'Document Number', 
        'Document Date', 'Bill To (First Line)', 'Ship To (First Line)',
        'Payment Terms (numeric part)', 'Mode of Shipment', 'Transaction Type',
        'HS Code', 'Part No', 'Qty Ordered', 'Unit Price', 'Net Amount',
        'Tax/VAT Amount', 'Total Invoice Amount', 'Due Date'
    ]
    
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=field_order)
        writer.writeheader()
        writer.writerow(fields)
    
    print(f"Data extracted and saved to {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Extract invoice details using regex/NLTK approach.")
    parser.add_argument("-t", "--text_file", required=True, help="Path to the text document to analyze")
    parser.add_argument("-o", "--output", default="extracted_invoice_data.csv", help="Output CSV file path")
    args = parser.parse_args()
    
    # Read the text file
    with open(args.text_file, 'r', encoding='utf-8') as f:
        text_content = f.read()
    
    # Extract fields using regex
    extracted_fields = extract_invoice_fields_regex(text_content)
    
    # Enhance with NLTK
    enhanced_fields = enhance_with_nltk(text_content, extracted_fields)
    
    # Validate extraction
    validated_fields = validate_extraction(enhanced_fields)
    
    # Save to CSV
    save_to_csv(validated_fields, args.output)
    
    # Print results
    print("\nExtracted Fields:")
    for i, (key, value) in enumerate(validated_fields.items(), 1):
        print(f"{i:2d}. {key}: {value}")

if __name__ == "__main__":
    main()

