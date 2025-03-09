# utils.py
def excel_column_to_index(col_letter):
    """Конвертирует буквенное обозначение колонки Excel в 0-based индекс"""
    col = ''.join([c for c in str(col_letter).upper().strip() if c.isalpha()])
    if not col:
        raise ValueError("Пустое обозначение колонки")
    
    index = 0
    for char in col:
        if char < 'A' or char > 'Z':
            raise ValueError(f"Недопустимый символ: {char}")
        index = index * 26 + (ord(char) - ord('A'))
    return index

# utils.py (новый файл)
def excel_column_to_index(col_letter):
    """Конвертирует буквенное обозначение колонки Excel в 0-based индекс"""
    col = col_letter.upper().strip()
    index = 0
    for char in col:
        if not char.isalpha():
            break  # Игнорируем цифры и другие символы
        index = index * 26 + (ord(char) - ord('A')) + 1
    return index - 1  # Переводим в 0-based индекс