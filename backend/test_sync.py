import sys
sys.path.insert(0, '.')
from dotenv import load_dotenv
load_dotenv()
from app.services.sync_service import sync_service

# 测试获取素材
print('=== 测试 sync_service ===')
library = sync_service.load_library()
print(f'本地素材库: {len(library)} 条')

# 过滤各风格
for style in ['banfo', 'mimeng']:
    samples = [x for x in library if x.get('style', '').lower() == style]
    print(f'\n{style} 风格素材: {len(samples)} 条')
    for i, x in enumerate(samples[:3], 1):
        st = x.get('snippet_type', 'N/A')
        ev = x.get('emotional_valence', 'N/A')
        lp = x.get('logic_pattern', '')[:20] if x.get('logic_pattern') else 'N/A'
        print(f'  {i}. type={st}, emotion={ev}, logic={lp}...')

# 测试 get_samples
print('\n=== 测试 get_samples(banfo) ===')
samples = sync_service.get_samples(style='banfo', count=3)
print(f'获取到 {len(samples)} 条样本')
for i, s in enumerate(samples, 1):
    print(f'  {i}. {s.get("snippet_type", "N/A")} | {s.get("emotional_valence", "N/A")}')
