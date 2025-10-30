#!/usr/bin/env python3
"""
数据库验证脚本

验证A股虚拟市场数据库的完整性和正确性
"""

import sys
import os
from typing import Dict, List, Tuple

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lib.db_models import get_db_manager, init_db_manager, StockMetadata
from sqlalchemy import text

# ANSI颜色代码
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    """打印标题"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'=' * 60}{Colors.RESET}")
    print(f"{Colors.BLUE}{Colors.BOLD}{text}{Colors.RESET}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'=' * 60}{Colors.RESET}\n")

def print_success(text: str):
    """打印成功信息"""
    print(f"{Colors.GREEN}✓{Colors.RESET} {text}")

def print_error(text: str):
    """打印错误信息"""
    print(f"{Colors.RED}✗{Colors.RESET} {text}")

def print_warning(text: str):
    """打印警告信息"""
    print(f"{Colors.YELLOW}⚠{Colors.RESET} {text}")

def print_info(text: str):
    """打印信息"""
    print(f"  {text}")


class DatabaseVerifier:
    """数据库验证器"""

    def __init__(self, db_manager=None):
        self.db = db_manager or get_db_manager()
        self.errors = []
        self.warnings = []

    def verify_all(self) -> bool:
        """执行所有验证"""
        print_header("数据库验证")

        # 1. 验证表结构
        tables_ok = self.verify_tables()

        # 2. 验证股票数据
        stocks_ok = self.verify_stocks()

        # 3. 验证指数数据
        indices_ok = self.verify_indices()

        # 4. 验证成分股
        constituents_ok = self.verify_constituents()

        # 5. 显示总结
        self.print_summary()

        return all([tables_ok, stocks_ok, indices_ok, constituents_ok])

    def verify_tables(self) -> bool:
        """验证表结构"""
        print_header("验证表结构")

        required_tables = {
            'stock_metadata': '股票元数据表',
            'market_klines': 'K线数据表',
            'stock_state': '股票状态表',
            'market_status': '市场状态表',
            'stock_realtime_price': '实时价格缓存表',
            'index_metadata': '指数元数据表',
            'market_indices': '指数历史数据表',
            'index_constituents': '指数成分股表',
            'sector_indices': '板块指数表',
            'market_global_state': '全局市场状态表',
        }

        all_ok = True

        with self.db.get_session() as session:
            for table_name, description in required_tables.items():
                try:
                    # 检查表是否存在
                    result = session.execute(text(f"""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables
                            WHERE table_name = '{table_name}'
                        );
                    """))
                    exists = result.scalar()

                    if exists:
                        # 获取行数
                        count_result = session.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                        count = count_result.scalar()
                        print_success(f"{description} ({table_name}): {count} 行")
                    else:
                        print_error(f"{description} ({table_name}): 表不存在")
                        self.errors.append(f"表 {table_name} 不存在")
                        all_ok = False

                except Exception as e:
                    print_error(f"{description} ({table_name}): 错误 - {e}")
                    self.errors.append(f"表 {table_name} 验证失败: {e}")
                    all_ok = False

        return all_ok

    def verify_stocks(self) -> bool:
        """验证股票数据"""
        print_header("验证股票数据")

        all_ok = True

        with self.db.get_session() as session:
            # 1. 验证股票总数
            total_count = session.query(StockMetadata).filter_by(is_active=True).count()

            if total_count == 106:
                print_success(f"股票总数: {total_count} ✓")
            else:
                print_error(f"股票总数: {total_count}（期望106只）")
                self.errors.append(f"股票数量不正确: {total_count}/106")
                all_ok = False

            # 2. 验证板块分布
            sector_query = text("""
                SELECT sector, COUNT(*) as count
                FROM stock_metadata
                WHERE is_active = TRUE
                GROUP BY sector
                ORDER BY count DESC
            """)
            sector_result = session.execute(sector_query)
            sectors = sector_result.fetchall()

            expected_sectors = {
                'Finance': 12,
                'Technology': 20,
                'Consumer': 15,
                'NewEnergy': 10,
                'Healthcare': 12,
                'Industry': 10,
                'RealEstate': 8,
                'Energy': 8,
                'Materials': 6,
                'Utilities': 5,
                'Telecom': 5,
            }

            print_info("\n板块分布:")
            for sector, count in sectors:
                expected = expected_sectors.get(sector, 0)
                if count == expected:
                    print_success(f"  {sector}: {count} 只 ✓")
                else:
                    print_warning(f"  {sector}: {count} 只（期望{expected}）")
                    self.warnings.append(f"{sector}板块数量: {count}/{expected}")

            # 3. 验证市值分布
            marketcap_query = text("""
                SELECT
                    CASE
                        WHEN market_cap >= 5000 THEN '超大盘(>5000亿)'
                        WHEN market_cap >= 1000 THEN '大盘(1000-5000亿)'
                        WHEN market_cap >= 300 THEN '中盘(300-1000亿)'
                        WHEN market_cap >= 100 THEN '小盘(100-300亿)'
                        ELSE '微盘(<100亿)'
                    END AS tier,
                    COUNT(*) as count,
                    ROUND(SUM(market_cap)) as total_cap
                FROM stock_metadata
                WHERE is_active = TRUE
                GROUP BY tier
                ORDER BY MIN(market_cap) DESC
            """)
            marketcap_result = session.execute(marketcap_query)
            tiers = marketcap_result.fetchall()

            print_info("\n市值分布:")
            for tier, count, total_cap in tiers:
                print_success(f"  {tier}: {count} 只，总市值 {total_cap:,} 亿元")

            # 4. 验证Beta系数范围
            beta_query = text("""
                SELECT
                    MIN(beta) as min_beta,
                    MAX(beta) as max_beta,
                    AVG(beta) as avg_beta
                FROM stock_metadata
                WHERE is_active = TRUE
            """)
            beta_result = session.execute(beta_query)
            beta_stats = beta_result.fetchone()

            print_info(f"\nBeta系数统计:")
            print_success(f"  最小Beta: {beta_stats[0]:.2f}")
            print_success(f"  最大Beta: {beta_stats[1]:.2f}")
            print_success(f"  平均Beta: {beta_stats[2]:.2f}")

            if not (0.6 <= beta_stats[0] <= 0.7 and 1.7 <= beta_stats[1] <= 1.9):
                print_warning(f"  Beta范围异常（期望0.65-1.80）")
                self.warnings.append(f"Beta范围: {beta_stats[0]:.2f}-{beta_stats[1]:.2f}")

        return all_ok

    def verify_indices(self) -> bool:
        """验证指数数据"""
        print_header("验证指数元数据")

        all_ok = True

        with self.db.get_session() as session:
            # 验证核心指数
            core_indices = ['HAPPY300', 'HAPPY50', 'GROW100']

            for index_code in core_indices:
                result = session.execute(text(f"""
                    SELECT index_name, base_value, constituent_count
                    FROM index_metadata
                    WHERE index_code = '{index_code}'
                """))
                index_info = result.fetchone()

                if index_info:
                    print_success(f"{index_code} ({index_info[0]}): "
                                f"基点 {index_info[1]}, "
                                f"成分股 {index_info[2]} 只")
                else:
                    print_error(f"{index_code}: 未找到")
                    self.errors.append(f"指数 {index_code} 不存在")
                    all_ok = False

            # 验证板块指数
            sector_indices = session.execute(text("""
                SELECT index_code, index_name
                FROM index_metadata
                WHERE index_type = 'sector'
            """))

            print_info("\n板块指数:")
            for code, name in sector_indices:
                print_success(f"  {code} - {name}")

        return all_ok

    def verify_constituents(self) -> bool:
        """验证指数成分股"""
        print_header("验证指数成分股")

        all_ok = True

        with self.db.get_session() as session:
            # 验证HAPPY300成分股
            happy300_query = text("""
                SELECT COUNT(*) as count
                FROM index_constituents
                WHERE index_code = 'HAPPY300' AND is_active = TRUE
            """)
            happy300_count = session.execute(happy300_query).scalar()

            if happy300_count == 100:
                print_success(f"HAPPY300成分股: {happy300_count} 只 ✓")
            else:
                print_error(f"HAPPY300成分股: {happy300_count} 只（期望100）")
                self.errors.append(f"HAPPY300成分股数量: {happy300_count}/100")
                all_ok = False

            # 验证HAPPY50成分股
            happy50_query = text("""
                SELECT COUNT(*) as count
                FROM index_constituents
                WHERE index_code = 'HAPPY50' AND is_active = TRUE
            """)
            happy50_count = session.execute(happy50_query).scalar()

            if happy50_count == 50:
                print_success(f"HAPPY50成分股: {happy50_count} 只 ✓")
            else:
                print_warning(f"HAPPY50成分股: {happy50_count} 只（期望50）")
                self.warnings.append(f"HAPPY50成分股数量: {happy50_count}/50")

            # 验证HAPPY300板块分布
            sector_dist_query = text("""
                SELECT sm.sector, COUNT(*) as count
                FROM index_constituents ic
                JOIN stock_metadata sm ON ic.stock_symbol = sm.symbol
                WHERE ic.index_code = 'HAPPY300' AND ic.is_active = TRUE
                GROUP BY sm.sector
                ORDER BY count DESC
            """)
            sector_dist = session.execute(sector_dist_query).fetchall()

            print_info("\nHAPPY300板块分布:")
            for sector, count in sector_dist:
                print_info(f"  {sector}: {count} 只")

            # 验证权重总和
            weight_sum_query = text("""
                SELECT SUM(weight) as total_weight
                FROM index_constituents
                WHERE index_code = 'HAPPY300' AND is_active = TRUE
            """)
            weight_sum = session.execute(weight_sum_query).scalar()

            print_info(f"\nHAPPY300权重总和: {weight_sum:.4f}")
            if abs(weight_sum - 1.0) > 0.01:
                print_warning(f"  权重总和应接近1.0")
                self.warnings.append(f"HAPPY300权重总和: {weight_sum:.4f}")

        return all_ok

    def print_summary(self):
        """打印验证总结"""
        print_header("验证总结")

        if not self.errors and not self.warnings:
            print(f"{Colors.GREEN}{Colors.BOLD}✓ 所有验证通过！数据库状态完好。{Colors.RESET}\n")
        else:
            if self.errors:
                print(f"{Colors.RED}发现 {len(self.errors)} 个错误：{Colors.RESET}")
                for error in self.errors:
                    print(f"  {Colors.RED}✗{Colors.RESET} {error}")
                print()

            if self.warnings:
                print(f"{Colors.YELLOW}发现 {len(self.warnings)} 个警告：{Colors.RESET}")
                for warning in self.warnings:
                    print(f"  {Colors.YELLOW}⚠{Colors.RESET} {warning}")
                print()


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="验证A股虚拟市场数据库")
    parser.add_argument('--db-url', type=str, help='数据库URL')

    args = parser.parse_args()

    # 初始化数据库
    db_kwargs = {}
    if args.db_url:
        db_kwargs['db_url'] = args.db_url

    db = init_db_manager(**db_kwargs)

    print(f"\n数据库连接: {db.db_url}\n")

    # 创建验证器并执行验证
    verifier = DatabaseVerifier(db_manager=db)
    success = verifier.verify_all()

    # 返回状态码
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
