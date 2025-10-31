import os
import sys

def parse_xml_line(line):
    """
    Parse a single XML line to extract string name if it's a string element.
    
    Args:
        line (str): A line from the XML file
        
    Returns:
        tuple: (is_string_element, string_name, original_line)
    """
    line = line.strip()
    
    # Skip empty lines and comments
    if not line or line.startswith('<!--'):
        return False, None, line
    
    # Check if this is a string element
    if line.startswith('<string name="') and '">' in line and line.endswith('</string>'):
        try:
            # Extract the string name from: <string name="string_name">string_value</string>
            start_index = line.find('name="') + 6  # 6 is length of 'name="'
            end_index = line.find('">', start_index)
            string_name = line[start_index:end_index]
            return True, string_name, line
        except:
            return False, None, line
    
    # For non-string elements, return the original line
    return False, None, line

def compare_xml_files_line_by_line(base_file_path, translated_file_path):
    """
    Compare two XML files line by line and check if string names match at the same positions.
    Stops after first mismatch to avoid cascade effect.
    
    Args:
        base_file_path (str): Path to the base XML file (reference)
        translated_file_path (str): Path to the translated XML file
    """
    print(f"🔍 Comparing XML files line by line:")
    print(f"📄 Base file: {base_file_path}")
    print(f"🌍 Translated file: {translated_file_path}")
    print("=" * 80)
    
    # Check if files exist
    if not os.path.exists(base_file_path):
        print(f"❌ ERROR: Base file '{base_file_path}' not found!")
        return
    
    if not os.path.exists(translated_file_path):
        print(f"❌ ERROR: Translated file '{translated_file_path}' not found!")
        return
    
    # Read both files
    try:
        with open(base_file_path, 'r', encoding='utf-8') as file:
            base_lines = file.readlines()
        
        with open(translated_file_path, 'r', encoding='utf-8') as file:
            translated_lines = file.readlines()
    except Exception as e:
        print(f"❌ ERROR reading files: {e}")
        return
    
    print(f"Base file has {len(base_lines)} lines")
    print(f"Translated file has {len(translated_lines)} lines")
    print("=" * 80)
    
    # Track statistics
    total_lines = min(len(base_lines), len(translated_lines))  # Use min to avoid index errors
    string_matches = 0
    non_string_lines = 0
    first_mismatch_found = False
    first_mismatch_line = None
    
    # Compare line by line
    for line_num in range(total_lines):
        line_display_num = line_num + 1  # Human-readable line numbers (starting from 1)
        
        # Get lines from both files
        base_line = base_lines[line_num]
        translated_line = translated_lines[line_num]
        
        # Parse both lines
        base_is_string, base_string_name, base_parsed_line = parse_xml_line(base_line)
        trans_is_string, trans_string_name, trans_parsed_line = parse_xml_line(translated_line)
        
        # If we already found a mismatch, stop detailed checking
        if first_mismatch_found:
            # Just count what type of lines we're seeing
            if base_is_string and trans_is_string:
                string_matches += 1
            else:
                non_string_lines += 1
            continue
        
        # Case 1: Both lines are string elements
        if base_is_string and trans_is_string:
            if base_string_name == trans_string_name:
                string_matches += 1
                # print(f"✅ Line {line_display_num}: MATCH - '{base_string_name}'")
            else:
                # FIRST MISMATCH FOUND - this will cause cascade effect
                first_mismatch_found = True
                first_mismatch_line = line_display_num
                print(f"🚨 FIRST MISMATCH FOUND at Line {line_display_num}:")
                print(f"   Base: '{base_string_name}'")
                print(f"   Trans: '{trans_string_name}'")
                print(f"   ⚠️  This mismatch will cause ALL subsequent lines to be out of sync!")
                print(f"   💡 Fix line {line_display_num} first, then run the comparison again.")
                print("-" * 80)
        
        # Case 2: Base has string but translated doesn't (or vice versa)
        elif base_is_string and not trans_is_string:
            first_mismatch_found = True
            first_mismatch_line = line_display_num
            print(f"🚨 FIRST MISMATCH FOUND at Line {line_display_num}:")
            print(f"   Base has string: '{base_string_name}'")
            print(f"   Translated has: '{trans_parsed_line if trans_parsed_line else 'NOTHING (empty/missing line)'}'")
            print(f"   ⚠️  This mismatch will cause ALL subsequent lines to be out of sync!")
            print(f"   💡 Fix line {line_display_num} first, then run the comparison again.")
            print("-" * 80)
        
        elif not base_is_string and trans_is_string:
            first_mismatch_found = True
            first_mismatch_line = line_display_num
            print(f"🚨 FIRST MISMATCH FOUND at Line {line_display_num}:")
            print(f"   Base has: '{base_parsed_line if base_parsed_line else 'NOTHING (empty/missing line)'}'")
            print(f"   Translated has string: '{trans_string_name}'")
            print(f"   ⚠️  This mismatch will cause ALL subsequent lines to be out of sync!")
            print(f"   💡 Fix line {line_display_num} first, then run the comparison again.")
            print("-" * 80)
        
        # Case 3: Both lines are non-string content (comments, other tags, etc.)
        else:
            non_string_lines += 1
    
    # Handle case where files have different lengths
    if len(base_lines) != len(translated_lines) and not first_mismatch_found:
        first_mismatch_found = True
        first_mismatch_line = total_lines + 1
        print(f"🚨 FILES HAVE DIFFERENT LENGTHS:")
        print(f"   Base file: {len(base_lines)} lines")
        print(f"   Translated file: {len(translated_lines)} lines")
        print(f"   ⚠️  This will cause mismatches starting from line {total_lines + 1}")
        print(f"   💡 Make sure both files have the same number of lines.")
        print("-" * 80)
    
    # Print summary
    print("=" * 80)
    print("📊 COMPARISON SUMMARY:")
    print(f"📈 Total lines checked: {total_lines}")
    print(f"✅ String matches before first mismatch: {string_matches}")
    print(f"📝 Non-string lines: {non_string_lines}")
    
    if first_mismatch_found:
        print(f"❌ FIRST MISMATCH at line: {first_mismatch_line}")
        print(f"💡 Fix this line first, then run the comparison again.")
        print(f"⚠️  Note: All lines after {first_mismatch_line} are likely out of sync due to cascade effect.")
    else:
        print("\n🎉 SUCCESS: All string names match perfectly!")
        print("✅ Files are perfectly synchronized!")

def main():
    """
    Main function to run the XML comparison.
    """
    # File paths
    base_file = "AlpineQuest_En.xml"
    translated_file = "AlpineQuest_Si.xml"
    
    # Compare the files
    compare_xml_files_line_by_line(base_file, translated_file)

if __name__ == "__main__":
    main()