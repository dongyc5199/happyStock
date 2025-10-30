/**
 * PageSection - 全屏滚动页面区块组件
 * 
 * 功能:
 * - 全屏高度布局容器
 * - 支持 scroll-snap 对齐
 * - 响应式设计
 * 
 * 对应需求: US1, US2 (FR-001, FR-007)
 */

import React from 'react';
import styles from './PageSection.module.css';

export interface PageSectionProps {
  /** 区块唯一标识符 */
  id: string;
  /** 子内容 */
  children: React.ReactNode;
  /** 区块标题(用于导航) */
  title?: string;
  /** 是否可折叠 */
  isCollapsible?: boolean;
  /** 自定义类名 */
  className?: string;
  /** 是否禁用 scroll-snap */
  disableSnap?: boolean;
}

export const PageSection: React.FC<PageSectionProps> = ({
  id,
  children,
  title,
  isCollapsible = false,
  className = '',
  disableSnap = false,
}) => {
  return (
    <section
      id={id}
      data-section-id={id}
      data-section-title={title}
      data-collapsible={isCollapsible}
      className={`${styles.pageSection} ${disableSnap ? styles.noSnap : ''} ${className}`}
      aria-labelledby={title ? `${id}-heading` : undefined}
    >
      {title && (
        <h2 id={`${id}-heading`} className="sr-only">
          {title}
        </h2>
      )}
      <div className={styles.sectionContent}>
        {children}
      </div>
    </section>
  );
};

export default PageSection;
