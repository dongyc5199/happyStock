/**
 * NavigationDots - 页面导航点组件
 * 
 * 功能:
 * - 显示页面区块导航点
 * - 指示当前激活区块
 * - 点击跳转到对应区块
 * 
 * 对应需求: US2 (FR-010, FR-011, FR-012)
 */

import React from 'react';
import styles from './NavigationDots.module.css';

export interface NavigationDot {
  /** 区块ID */
  sectionId: string;
  /** 导航标签 */
  label: string;
  /** 是否激活 */
  isActive: boolean;
  /** 索引位置 */
  index: number;
}

export interface NavigationDotsProps {
  /** 导航点数据 */
  dots: NavigationDot[];
  /** 点击导航点回调 */
  onDotClick: (sectionId: string, index: number) => void;
  /** 固定位置 (默认 'right') */
  position?: 'left' | 'right';
  /** 自定义类名 */
  className?: string;
}

export const NavigationDots: React.FC<NavigationDotsProps> = ({
  dots,
  onDotClick,
  position = 'right',
  className = '',
}) => {
  const handleKeyDown = (
    e: React.KeyboardEvent,
    sectionId: string,
    index: number
  ) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      onDotClick(sectionId, index);
    }
  };

  return (
    <nav
      className={`${styles.navigationDots} ${styles[position]} ${className}`}
      aria-label="页面导航"
      role="navigation"
    >
      <ul className={styles.dotList} role="list">
        {dots.map((dot) => (
          <li key={dot.sectionId} className={styles.dotItem}>
            <button
              type="button"
              className={`${styles.dot} ${dot.isActive ? styles.active : ''}`}
              onClick={() => onDotClick(dot.sectionId, dot.index)}
              onKeyDown={(e) => handleKeyDown(e, dot.sectionId, dot.index)}
              aria-label={`跳转到 ${dot.label}`}
              aria-current={dot.isActive ? 'true' : 'false'}
              title={dot.label}
            >
              <span className={styles.dotInner} aria-hidden="true" />
              <span className="sr-only">{dot.label}</span>
            </button>
          </li>
        ))}
      </ul>
    </nav>
  );
};

export default NavigationDots;
