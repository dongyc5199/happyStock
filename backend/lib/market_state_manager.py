"""
市场状态管理器
Market State Manager

管理全局市场状态（牛市/熊市/横盘），影响所有股票的价格生成。
"""

from typing import Optional, Dict
from datetime import datetime, timedelta
import random
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.db_manager_sqlite import DatabaseManager


class MarketStateManager:
    """市场状态管理器"""

    # 市场状态常量
    STATE_BULL = "BULL"  # 牛市
    STATE_BEAR = "BEAR"  # 熊市
    STATE_SIDEWAYS = "SIDEWAYS"  # 横盘震荡

    # 状态转换规则
    STATE_TRANSITIONS = {
        STATE_BULL: [STATE_SIDEWAYS, STATE_BULL],  # 牛市可转横盘或继续牛市
        STATE_BEAR: [STATE_SIDEWAYS, STATE_BEAR],  # 熊市可转横盘或继续熊市
        STATE_SIDEWAYS: [STATE_BULL, STATE_BEAR, STATE_SIDEWAYS],  # 横盘可转任何状态
    }

    # 每个状态的daily_trend范围
    STATE_TREND_RANGES = {
        STATE_BULL: (0.003, 0.01),  # 牛市：0.3% ~ 1.0% 日均涨幅
        STATE_BEAR: (-0.01, -0.003),  # 熊市：-1.0% ~ -0.3% 日均跌幅
        STATE_SIDEWAYS: (-0.002, 0.002),  # 横盘：-0.2% ~ 0.2% 小幅波动
    }

    # 最小持续天数
    MIN_DURATION_DAYS = 7

    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        """
        初始化市场状态管理器

        Args:
            db_manager: 数据库管理器（可选，默认创建新实例）
        """
        self.db_manager = db_manager or DatabaseManager()

    def get_current_state(self) -> Optional[Dict]:
        """
        获取当前市场状态

        Returns:
            当前状态字典，包含:
            - state: 状态类型 (BULL/BEAR/SIDEWAYS)
            - start_time: 开始时间
            - daily_trend: 日均趋势
            - volatility_multiplier: 波动率乘数
            - description: 状态描述
        """
        conn = self.db_manager.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, state, start_time, end_time, daily_trend,
                       volatility_multiplier, description, is_current
                FROM market_states
                WHERE is_current = 1
                ORDER BY start_time DESC
                LIMIT 1
                """
            )
            row = cursor.fetchone()

            if row:
                return {
                    "id": row[0],
                    "state": row[1],
                    "start_time": row[2],
                    "end_time": row[3],
                    "daily_trend": row[4],
                    "volatility_multiplier": row[5],
                    "description": row[6],
                    "is_current": row[7],
                }
            return None
        finally:
            conn.close()

    def get_market_trend(self) -> float:
        """
        获取当前市场趋势值（用于价格生成）

        Returns:
            daily_trend值，范围根据市场状态而定
        """
        state = self.get_current_state()
        if state:
            return state["daily_trend"]
        return 0.0

    def transition_state(
        self,
        force_state: Optional[str] = None,
        force_trend: Optional[float] = None,
        ignore_duration: bool = False,
    ) -> Dict:
        """
        市场状态转换

        Args:
            force_state: 强制指定新状态（可选，用于测试）
            force_trend: 强制指定daily_trend（可选，用于测试）
            ignore_duration: 忽略最小持续时间限制（用于force_*方法）

        Returns:
            新状态字典
        """
        current = self.get_current_state()

        # 检查是否满足最小持续时间（除非ignore_duration=True）
        if current and not ignore_duration:
            start_time = datetime.fromisoformat(current["start_time"])
            now = datetime.now()
            duration_days = (now - start_time).days

            if duration_days < self.MIN_DURATION_DAYS:
                print(
                    f"[*] Market state {current['state']} has only lasted {duration_days} days "
                    f"(min: {self.MIN_DURATION_DAYS}), keeping current state"
                )
                return current

        # 确定新状态
        if force_state:
            new_state = force_state
        elif current:
            # 根据转换规则选择新状态
            possible_states = self.STATE_TRANSITIONS.get(
                current["state"], [self.STATE_SIDEWAYS]
            )
            # 70%概率保持当前状态，30%概率转换
            if random.random() < 0.7 and current["state"] in possible_states:
                new_state = current["state"]
            else:
                new_state = random.choice(possible_states)
        else:
            # 没有当前状态，默认横盘
            new_state = self.STATE_SIDEWAYS

        # 确定daily_trend
        if force_trend is not None:
            daily_trend = force_trend
        else:
            min_trend, max_trend = self.STATE_TREND_RANGES[new_state]
            daily_trend = random.uniform(min_trend, max_trend)

        # 确定波动率乘数
        volatility_multiplier = {
            self.STATE_BULL: 1.2,  # 牛市波动稍大
            self.STATE_BEAR: 1.5,  # 熊市波动更大
            self.STATE_SIDEWAYS: 1.0,  # 横盘波动正常
        }[new_state]

        # 生成描述
        state_names = {
            self.STATE_BULL: "牛市",
            self.STATE_BEAR: "熊市",
            self.STATE_SIDEWAYS: "横盘震荡",
        }
        description = f"{state_names[new_state]}阶段，日均{'涨幅' if daily_trend > 0 else '跌幅' if daily_trend < 0 else '波动'}约{abs(daily_trend)*100:.2f}%"

        # 保存到数据库
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn = self.db_manager.get_connection()
        try:
            cursor = conn.cursor()

            # 将旧状态标记为非当前
            if current:
                cursor.execute(
                    """
                    UPDATE market_states
                    SET is_current = 0, end_time = ?
                    WHERE id = ?
                    """,
                    (now_str, current["id"]),
                )

            # 插入新状态
            cursor.execute(
                """
                INSERT INTO market_states
                (state, start_time, daily_trend, volatility_multiplier, description, is_current)
                VALUES (?, ?, ?, ?, ?, 1)
                """,
                (new_state, now_str, daily_trend, volatility_multiplier, description),
            )

            new_state_id = cursor.lastrowid
            conn.commit()

            print(f"[+] Market state transitioned to: {new_state} (trend={daily_trend:.4f})")
            print(f"    Description: {description}")

            return {
                "id": new_state_id,
                "state": new_state,
                "start_time": now_str,
                "end_time": None,
                "daily_trend": daily_trend,
                "volatility_multiplier": volatility_multiplier,
                "description": description,
                "is_current": 1,
            }
        finally:
            conn.close()

    def force_bull_market(self, trend: float = 0.005):
        """强制进入牛市（用于演示）"""
        return self.transition_state(
            force_state=self.STATE_BULL, force_trend=trend, ignore_duration=True
        )

    def force_bear_market(self, trend: float = -0.005):
        """强制进入熊市（用于演示）"""
        return self.transition_state(
            force_state=self.STATE_BEAR, force_trend=trend, ignore_duration=True
        )

    def force_sideways_market(self, trend: float = 0.0):
        """强制进入横盘（用于演示）"""
        return self.transition_state(
            force_state=self.STATE_SIDEWAYS, force_trend=trend, ignore_duration=True
        )


def test_market_state_manager():
    """测试市场状态管理器"""
    print("=== Testing MarketStateManager ===\n")

    manager = MarketStateManager()

    # 1. 获取当前状态
    print("1. Get current state:")
    current = manager.get_current_state()
    if current:
        print(f"   State: {current['state']}")
        print(f"   Trend: {current['daily_trend']}")
        print(f"   Description: {current['description']}")
    else:
        print("   No current state found")

    # 2. 测试状态转换
    print("\n2. Transition to BULL market:")
    manager.force_bull_market(trend=0.008)

    print("\n3. Get current state after transition:")
    current = manager.get_current_state()
    print(f"   State: {current['state']}")
    print(f"   Trend: {current['daily_trend']}")

    # 4. 测试最小持续时间限制（应该保持牛市）
    print("\n4. Try immediate transition (should be blocked):")
    result = manager.transition_state()
    print(f"   State remains: {result['state']}")

    print("\n=== Test Complete ===")


if __name__ == "__main__":
    test_market_state_manager()
