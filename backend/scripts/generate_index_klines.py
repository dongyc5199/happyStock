"""
生成指数历史K线数据
T043: Generate 90-day historical index values
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.index_calculator import generate_all_indices_historical_data

if __name__ == '__main__':
    print("=" * 80)
    print("📊 生成指数历史K线数据")
    print("=" * 80)
    print()
    
    try:
        total = generate_all_indices_historical_data(days=90)
        
        print()
        print("=" * 80)
        if total > 0:
            print("🎉 指数历史数据生成完成！")
            print()
            print("📌 下一步:")
            print("  运行: pipenv run python scripts/check_indices.py")
            print("  验证指数数据是否正确")
        else:
            print("⚠️  没有生成任何数据，请检查股票价格数据是否存在")
        print("=" * 80)
        
        sys.exit(0 if total > 0 else 1)
        
    except Exception as e:
        print()
        print("=" * 80)
        print(f"❌ 生成失败: {e}")
        print("=" * 80)
        import traceback
        traceback.print_exc()
        sys.exit(1)
