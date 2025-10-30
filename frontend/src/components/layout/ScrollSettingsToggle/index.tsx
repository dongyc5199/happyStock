/**
 * ScrollSettingsToggle - 滚动设置切换组件
 * 
 * 功能:
 * - 允许用户禁用/启用整页滚动
 * - 状态持久化到 localStorage
 * - 可访问性支持
 * 
 * 对应需求: US2 (FR-009)
 */

'use client';

import { useState } from 'react';
import { useLayoutStore } from '@/store/layoutStore';
import styles from './ScrollSettingsToggle.module.css';

export interface ScrollSettingsToggleProps {
  /** 自定义类名 */
  className?: string;
  /** 显示位置 */
  position?: 'fixed' | 'inline';
}

export function ScrollSettingsToggle({
  className = '',
  position = 'fixed',
}: ScrollSettingsToggleProps) {
  const [isOpen, setIsOpen] = useState(false);
  
  const isScrollSnapEnabled = useLayoutStore(
    (state) => state.preferences.isScrollSnapEnabled
  );
  const setScrollSnap = useLayoutStore((state) => state.setScrollSnap);

  const handleToggle = () => {
    setScrollSnap(!isScrollSnapEnabled);
  };

  const toggleMenu = () => {
    setIsOpen(!isOpen);
  };

  return (
    <div
      className={`${styles.container} ${position === 'fixed' ? styles.fixed : styles.inline} ${className}`}
    >
      {/* 切换按钮 */}
      <button
        type="button"
        onClick={toggleMenu}
        className={styles.toggleButton}
        aria-label="滚动设置"
        aria-expanded={isOpen}
        aria-controls="scroll-settings-menu"
      >
        <svg
          className={styles.icon}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          aria-hidden="true"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
          />
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
          />
        </svg>
      </button>

      {/* 设置菜单 */}
      {isOpen && (
        <div
          id="scroll-settings-menu"
          className={styles.menu}
          role="menu"
          aria-label="滚动设置选项"
        >
          <div className={styles.menuHeader}>
            <h3 className={styles.menuTitle}>滚动设置</h3>
          </div>
          
          <div className={styles.menuContent}>
            {/* 整页滚动开关 */}
            <label 
              className={styles.settingItem} 
              role="menuitemcheckbox"
              aria-checked={isScrollSnapEnabled}
            >
              <div className={styles.settingInfo}>
                <span className={styles.settingLabel}>整页滚动</span>
                <span className={styles.settingDescription}>
                  滚动时自动对齐到内容区域边界
                </span>
              </div>
              
              <button
                type="button"
                onClick={handleToggle}
                className={`${styles.switch} ${isScrollSnapEnabled ? styles.switchOn : styles.switchOff}`}
                role="switch"
                aria-checked={isScrollSnapEnabled}
                aria-label="切换整页滚动"
              >
                <span
                  className={styles.switchThumb}
                  aria-hidden="true"
                />
              </button>
            </label>

            {/* 提示信息 */}
            <div className={styles.hint}>
              <svg className={styles.hintIcon} fill="currentColor" viewBox="0 0 20 20">
                <path
                  fillRule="evenodd"
                  d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                  clipRule="evenodd"
                />
              </svg>
              <span className={styles.hintText}>
                键盘导航: 使用 ↑↓ 箭头键或 PageUp/PageDown 在区域间快速切换
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default ScrollSettingsToggle;
