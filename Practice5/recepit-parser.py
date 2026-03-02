import re
import json
from datetime import datetime

def parse_receipt(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        content = file.read()
    
    receipt_data = {
        'store_info': {},
        'items': [],
        'totals': {},
        'payment': {},
        'datetime': None,
        'fiscal_data': {}
    }
    
    store_match = re.search(r'Филиал\s+(.+?)(?:\n|$)', content)
    if store_match:
        receipt_data['store_info']['name'] = store_match.group(1).strip()
    
    bin_match = re.search(r'БИН\s+(\d+)', content)
    if bin_match:
        receipt_data['store_info']['bin'] = bin_match.group(1)
    
    items = []
    item_blocks = re.finditer(r'(\d+)\.\s*(.+?)(?=\n\d+\.|\nБанковская карта:|\Z)', content, re.DOTALL)
    
    for block in item_blocks:
        item_text = block.group(2).strip()
        lines = item_text.split('\n')
        
        quantity_line_idx = -1
        for i, line in enumerate(lines):
            if re.search(r'\d+[,.]?\d*\s*x\s*\d+[,.]?\d*', line):
                quantity_line_idx = i
                break
        
        if quantity_line_idx > 0:
            product_name = ' '.join(lines[:quantity_line_idx]).strip()
            
            quantity_match = re.search(r'(\d+[,.]?\d*)\s*x\s*(\d+[,.]?\d*)', lines[quantity_line_idx])
            if quantity_match:
                quantity = float(quantity_match.group(1).replace(',', '.'))
                unit_price = float(quantity_match.group(2).replace(',', '.').replace(' ', ''))
                
                total_price = None
                for line in lines[quantity_line_idx+1:]:
                    price_match = re.search(r'(\d+[,.]?\d*\s*\d*)', line.replace(' ', ''))
                    if price_match and not re.search(r'Стоимость', line):
                        total_price = float(price_match.group(1).replace(',', '.'))
                        break
                
                if total_price is None:
                    total_match = re.search(r'x\s*\d+[,.]?\d*\s*(\d+[,.]?\d*)', lines[quantity_line_idx])
                    if total_match:
                        total_price = float(total_match.group(1).replace(',', '.').replace(' ', ''))
                
                items.append({
                    'name': product_name,
                    'quantity': quantity,
                    'unit_price': unit_price,
                    'total': total_price if total_price else quantity * unit_price
                })
    
    receipt_data['items'] = items
    
    all_prices = re.findall(r'(?<!\d)(\d{1,3}(?:\s?\d{3})*[,.]?\d*)(?=\s*(?:,00|\.00)?\s*(?:\n|$))', content)
    processed_prices = []
    for price in all_prices:
        clean_price = price.replace(' ', '').replace(',', '.')
        try:
            processed_prices.append(float(clean_price))
        except ValueError:
            pass
    
    receipt_data['all_prices'] = processed_prices
    
    total_match = re.search(r'ИТОГО:\s*(\d{1,3}(?:\s?\d{3})*[,.]?\d*)', content)
    if total_match:
        total_str = total_match.group(1).replace(' ', '').replace(',', '.')
        receipt_data['totals']['total'] = float(total_str)
    
    subtotal_match = re.search(r'Банковская карта:\s*(\d{1,3}(?:\s?\d{3})*[,.]?\d*)', content)
    if subtotal_match:
        subtotal_str = subtotal_match.group(1).replace(' ', '').replace(',', '.')
        receipt_data['totals']['subtotal'] = float(subtotal_str)
    
    vat_match = re.search(r'в т\.ч\. НДС 12%:\s*(\d{1,3}(?:\s?\d{3})*[,.]?\d*)', content)
    if vat_match:
        vat_str = vat_match.group(1).replace(' ', '').replace(',', '.')
        receipt_data['totals']['vat'] = float(vat_str)
    
    datetime_match = re.search(r'Время:\s*(\d{2}\.\d{2}\.\d{4}\s*\d{2}:\d{2}:\d{2})', content)
    if datetime_match:
        datetime_str = datetime_match.group(1)
        try:
            dt = datetime.strptime(datetime_str, '%d.%m.%Y %H:%M:%S')
            receipt_data['datetime'] = dt.isoformat()
            receipt_data['date'] = dt.strftime('%Y-%m-%d')
            receipt_data['time'] = dt.strftime('%H:%M:%S')
        except ValueError:
            receipt_data['datetime'] = datetime_str
    
    if re.search(r'Банковская карта:', content):
        receipt_data['payment']['method'] = 'Банковская карта'
    
    fiscal_match = re.search(r'Фискальный признак:\s*(\d+)', content)
    if fiscal_match:
        receipt_data['fiscal_data']['fiscal_sign'] = fiscal_match.group(1)
    
    receipt_no_match = re.search(r'Чек №(\d+)', content)
    if receipt_no_match:
        receipt_data['fiscal_data']['receipt_number'] = receipt_no_match.group(1)
    
    rnm_match = re.search(r'Код ККМ КГД \(РНМ\):\s*(\d+)', content)
    if rnm_match:
        receipt_data['fiscal_data']['rnm'] = rnm_match.group(1)
    
    znm_match = re.search(r'ЗНМ:\s*(\S+)', content)
    if znm_match:
        receipt_data['fiscal_data']['znm'] = znm_match.group(1)
    
    return receipt_data

def format_output(data, format_type='text'):
    if format_type == 'json':
        return json.dumps(data, ensure_ascii=False, indent=2)
    
    output = []
    output.append("=" * 60)
    output.append("RECEIPT PARSER OUTPUT")
    output.append("=" * 60)
    
    output.append("\nSTORE INFORMATION:")
    output.append(f"  Name: {data['store_info'].get('name', 'N/A')}")
    output.append(f"  BIN: {data['store_info'].get('bin', 'N/A')}")
    
    if data.get('datetime'):
        output.append(f"\nDATE & TIME: {data['datetime']}")
    
    output.append(f"\nITEMS ({len(data['items'])}):")
    output.append("-" * 60)
    for i, item in enumerate(data['items'], 1):
        output.append(f"{i:2d}. {item['name'][:50]}")
        output.append(f"     Qty: {item['quantity']:6.3f}  @ {item['unit_price']:10.2f}  = {item['total']:10.2f}")
    
    output.append("-" * 60)
    if 'subtotal' in data['totals']:
        output.append(f"SUBTOTAL:                    {data['totals']['subtotal']:15.2f}")
    if 'vat' in data['totals']:
        output.append(f"VAT (12%):                    {data['totals']['vat']:15.2f}")
    if 'total' in data['totals']:
        output.append(f"TOTAL:                        {data['totals']['total']:15.2f}")
    
    if data['payment']:
        output.append(f"\nPAYMENT METHOD: {data['payment'].get('method', 'N/A')}")
    
    if data['fiscal_data']:
        output.append(f"\nFISCAL DATA:")
        for key, value in data['fiscal_data'].items():
            output.append(f"  {key}: {value}")
    
    output.append("\n" + "=" * 60)
    
    return '\n'.join(output)

def main():
    filename = 'raw.txt'
    
    try:
        parsed_data = parse_receipt(filename)
        print(format_output(parsed_data, 'text'))
        
        with open('receipt_output.json', 'w', encoding='utf-8') as f:
            f.write(format_output(parsed_data, 'json'))
        print("\nJSON output saved to receipt_output.json")
        
        print("\n" + "=" * 60)
        print("SUMMARY STATISTICS:")
        print(f"Total items: {len(parsed_data['items'])}")
        print(f"Total amount: {parsed_data['totals'].get('total', 0):.2f}")
        print(f"Payment method: {parsed_data['payment'].get('method', 'N/A')}")
        print(f"Date: {parsed_data.get('date', 'N/A')}")
        
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
    except Exception as e:
        print(f"Error parsing receipt: {e}")

if __name__ == "__main__":
    main()