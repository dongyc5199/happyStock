'use client';

export interface Sector {
  code: string;
  name: string;
  name_en: string;
  beta: number;
  description: string;
  stock_count: number;
  avg_change_pct: number;
  total_market_cap: number;
}

interface SectorHeatMapProps {
  sectors: Sector[];
  onSectorClick?: (sector: Sector) => void;
}

export default function SectorHeatMap({
  sectors,
  onSectorClick,
}: SectorHeatMapProps) {
  // 根据涨跌幅计算背景色强度
  const getBackgroundColor = (changePct: number): string => {
    // 上涨：红色系
    if (changePct > 3) {
      return 'bg-red-200 border-red-400';
    } else if (changePct > 2) {
      return 'bg-red-100 border-red-300';
    } else if (changePct > 1) {
      return 'bg-red-50 border-red-200';
    } else if (changePct > 0) {
      return 'bg-red-25 border-red-100';
    }
    // 平盘：灰色
    else if (changePct === 0) {
      return 'bg-gray-100 border-gray-300';
    }
    // 下跌：绿色系
    else if (changePct > -1) {
      return 'bg-green-25 border-green-100';
    } else if (changePct > -2) {
      return 'bg-green-50 border-green-200';
    } else if (changePct > -3) {
      return 'bg-green-100 border-green-300';
    } else {
      return 'bg-green-200 border-green-400';
    }
  };

  const getTextColor = (changePct: number): string => {
    if (changePct > 0) {
      return 'text-red-600';
    } else if (changePct < 0) {
      return 'text-green-600';
    } else {
      return 'text-gray-600';
    }
  };

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
      {sectors.map((sector) => (
        <SectorCell
          key={sector.code}
          sector={sector}
          backgroundClass={getBackgroundColor(sector.avg_change_pct || 0)}
          textColorClass={getTextColor(sector.avg_change_pct || 0)}
          onClick={() => onSectorClick?.(sector)}
        />
      ))}
    </div>
  );
}

interface SectorCellProps {
  sector: Sector;
  backgroundClass: string;
  textColorClass: string;
  onClick?: () => void;
}

function SectorCell({
  sector,
  backgroundClass,
  textColorClass,
  onClick,
}: SectorCellProps) {
  const changePct = sector.avg_change_pct || 0;

  return (
    <div
      className={`p-4 rounded-lg border-2 transition-all hover:scale-105 hover:shadow-lg cursor-pointer ${backgroundClass}`}
      onClick={onClick}
    >
      <div className="text-center">
        {/* 板块名称 */}
        <div className="text-lg font-bold mb-1 text-gray-900">
          {sector.name}
        </div>
        <div className="text-xs text-gray-600 mb-3">{sector.name_en}</div>

        {/* 涨跌幅 */}
        <div className={`text-3xl font-bold mb-3 ${textColorClass}`}>
          {changePct >= 0 ? '+' : ''}
          {changePct.toFixed(2)}%
        </div>

        {/* 统计信息 */}
        <div className="text-xs space-y-1 text-gray-700 border-t border-gray-300 pt-2">
          <div className="flex justify-between">
            <span>Beta:</span>
            <span className="font-semibold">{sector.beta.toFixed(2)}</span>
          </div>
          <div className="flex justify-between">
            <span>股票:</span>
            <span className="font-semibold">{sector.stock_count}只</span>
          </div>
          <div className="flex justify-between">
            <span>市值:</span>
            <span className="font-semibold">
              {(sector.total_market_cap / 100000000).toFixed(0)}亿
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}

// 导出辅助组件
export function HeatMapLegend() {
  return (
    <div className="flex flex-wrap items-center justify-center gap-4 text-sm text-gray-600">
      <LegendItem color="bg-red-200" label="大幅上涨 (&gt;3%)" />
      <LegendItem color="bg-red-100" label="上涨 (2~3%)" />
      <LegendItem color="bg-red-50" label="微涨 (0~2%)" />
      <LegendItem color="bg-gray-100" label="平盘 (±0%)" />
      <LegendItem color="bg-green-50" label="微跌 (0~-2%)" />
      <LegendItem color="bg-green-100" label="下跌 (-2~-3%)" />
      <LegendItem color="bg-green-200" label="大幅下跌 (&lt;-3%)" />
    </div>
  );
}

function LegendItem({ color, label }: { color: string; label: string }) {
  return (
    <div className="flex items-center gap-2">
      <div className={`w-4 h-4 ${color} border border-gray-400 rounded`}></div>
      <span>{label}</span>
    </div>
  );
}
