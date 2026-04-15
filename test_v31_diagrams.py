import sys
sys.path.insert(0, r'C:\Users\GHC\.gemini\antigravity\scratch\cuongtan12345678_sync')
from interaction_diagrams import match_question_to_diagram, DIAGRAM_MASTER, DIAGRAMS

# Test matching
tests = [
    'co nen dau tu khong',
    'mat dien thoai o dau',
    'khi nao thi co tien',
    'benh nay co chua duoc khong',
    'kinh doanh gi tot',
    'toi bao nhieu tuoi',
    'tai sao thua lo',
    'chon cai nao tot hon',
]
for q in tests:
    d_id, d_info = match_question_to_diagram(q)
    name = d_info.get('name', '?')
    print(f"  {q:35s} => {d_id} ({name})")

print()
print(f"Total diagrams: {len(DIAGRAMS)}")
print(f"Master diagram: {'YES' if DIAGRAM_MASTER else 'NO'}")
print(f"Master name: {DIAGRAM_MASTER['name']}")
