/**
 * CollapsibleSection - 可折叠区块组件
 * 
 * 功能:
 * - 区块折叠/展开功能
 * - 动画过渡效果
 * - 状态持久化
 * 
 * 对应需求: US3 (FR-013, FR-014, FR-015, FR-016)
 */

import React, { useState, useRef } from 'react';
import styles from './CollapsibleSection.module.css';

export interface CollapsibleSectionProps {
  /** 区块ID */
  id: string;
  /** 区块标题 */
  title: string;
  /** 子内容 */
  children: React.ReactNode;
  /** 初始折叠状态 */
  defaultCollapsed?: boolean;
  /** 折叠状态改变回调 */
  onToggle?: (collapsed: boolean) => void;
  /** 自定义类名 */
  className?: string;
}

export const CollapsibleSection: React.FC<CollapsibleSectionProps> = ({
  id,
  title,
  children,
  defaultCollapsed = false,
  onToggle,
  className = '',
}) => {
  const [isCollapsed, setIsCollapsed] = useState(defaultCollapsed);
  const contentRef = useRef<HTMLDivElement>(null);

  const handleToggle = () => {
    const newState = !isCollapsed;
    setIsCollapsed(newState);
    onToggle?.(newState);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      handleToggle();
    }
  };

  return (
    <div
      className={`${styles.collapsibleSection} ${isCollapsed ? styles.collapsed : styles.expanded} ${className}`}
      data-section-id={id}
    >
      <div className={styles.header}>
        <button
          type="button"
          className={styles.toggleButton}
          onClick={handleToggle}
          onKeyDown={handleKeyDown}
          aria-expanded={!isCollapsed}
          aria-controls={`${id}-content`}
          aria-label={`${isCollapsed ? '展开' : '折叠'} ${title}`}
        >
          <span className={styles.title}>{title}</span>
          <span
            className={styles.icon}
            aria-hidden="true"
          >
            {isCollapsed ? '▼' : '▲'}
          </span>
        </button>
      </div>
      
      <div
        id={`${id}-content`}
        ref={contentRef}
        className={styles.content}
        aria-hidden={isCollapsed}
      >
        <div className={styles.contentInner}>
          {children}
        </div>
      </div>
    </div>
  );
};

export default CollapsibleSection;
