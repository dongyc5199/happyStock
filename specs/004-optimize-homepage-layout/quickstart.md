# Quickstart Guide: 首页布局优化与整页滚动

**Feature**: 004-optimize-homepage-layout  
**Date**: 2025-10-30  
**Purpose**: 端到端测试场景，验证所有用户故事和功能需求

## Overview

本文档提供完整的测试场景，用于验证首页布局优化功能的正确性。每个场景对应 spec.md 中的用户故事和验收标准。

## Prerequisites (前置条件)

### 环境准备

1. **启动开发服务器**:
   ```bash
   cd frontend
   npm run dev
   ```
   
2. **访问首页**:
   - URL: http://localhost:3000
   - 期望: 页面正常加载，无控制台错误

3. **浏览器准备**:
   - 推荐: Chrome 90+ (用于 DevTools Performance 分析)
   - 测试: Firefox, Safari, Edge 最新版本
   - 移动设备: iOS Safari, Android Chrome

4. **清除缓存** (首次测试):
   ```javascript
   // 在浏览器控制台执行
   localStorage.clear();
   location.reload();
   ```

---

## Scenario 1: 快速浏览首页关键信息 (US1-P1)

**目标**: 验证内容组织清晰，用户能快速识别各功能区域

### Test 1.1: 首屏内容识别

**Given**: 用户首次访问首页  
**When**: 页面加载完成  
**Then**: 验证以下要素

✅ **验证步骤**:
1. 打开 http://localhost:3000
2. 等待 2 秒（确保所有内容加载完成）
3. 检查首屏可见元素：
   - [ ] Hero Section 显示核心价值主张（"专业图表工具 + AI模拟交易 + 投资社交平台"）
   - [ ] 可见至少 3 个主要 CTA 按钮（"开始交易"、"查看图表"、"加入社区"）
   - [ ] 核心市场数据卡片可见（如 Happy300 指数）
4. 使用秒表计时：用户能否在 5 秒内说出 3 个主要功能区域？

**Expected Result**:
- 首屏包含价值主张、CTA、核心数据
- 视觉层次清晰，无信息过载
- 5秒内完成关键信息识别

---

### Test 1.2: 区域视觉边界

**Given**: 用户浏览首页  
**When**: 滚动查看所有区域  
**Then**: 每个区域有清晰的视觉分隔

✅ **验证步骤**:
1. 慢速滚动整个页面（不触发整页滚动）
2. 检查每个区域：
   - [ ] Hero Section: 独特的背景色/渐变
   - [ ] Market Overview: 卡片容器 + 边框/阴影
   - [ ] Hot Stock List: 表格/列表样式，与其他区域区分
   - [ ] Quick Start Guide: 步骤卡片 + 明确标题
   - [ ] Feature Showcase: 功能卡片网格布局
   - [ ] Education Footer: 底部区域，不同背景色
3. 验证区域间距：
   - [ ] 区域间有足够留白（至少 2rem/32px）
   - [ ] 使用 DevTools 检查 margin/padding

**Expected Result**:
- 每个区域有唯一的视觉风格
- 区域边界清晰可辨
- 无视觉混乱或内容重叠

---

### Test 1.3: 内容聚合验证

**Given**: 首页有多个功能区域  
**When**: 查看内容组织  
**Then**: 相关内容被聚合在同一区域

✅ **验证步骤**:
1. 检查市场数据聚合：
   - [ ] 所有指数数据在 "Market Overview" 区域
   - [ ] 热门股票在 "Hot Stock List" 区域
   - [ ] 无市场数据分散在其他区域
2. 检查学习资源聚合：
   - [ ] 所有教育链接在 "Education Footer" 区域
   - [ ] 包括：新手指南、交易教程、社区论坛
3. 检查功能入口聚合：
   - [ ] 专业图表、AI助手、社交功能在 "Feature Showcase" 区域
   - [ ] 每个功能卡片包含标题、描述、图标

**Expected Result**:
- 相关内容集中展示，无分散
- 用户无需跨区域查找相关信息
- 内容分类逻辑清晰

---

### Test 1.4: 移动端响应式

**Given**: 用户在移动设备访问  
**When**: 查看首页  
**Then**: 内容保持清晰层级，无横向溢出

✅ **验证步骤**:
1. 打开 Chrome DevTools (F12)
2. 切换到 Device Mode (Ctrl+Shift+M)
3. 测试以下尺寸：
   - [ ] iPhone SE (375x667px)
   - [ ] iPad (768x1024px)
   - [ ] Galaxy Fold (280x653px - 极端窄屏)
4. 检查每个尺寸：
   - [ ] 无横向滚动条
   - [ ] 文本可读（字体大小 ≥14px）
   - [ ] 按钮足够大（至少 44x44px）
   - [ ] 图片/图表适应屏幕宽度

**Expected Result**:
- 所有设备尺寸下内容正常显示
- 无布局错位或内容截断
- 触摸目标足够大，易于点击

---

## Scenario 2: 使用整页滚动快速导航 (US2-P1)

**目标**: 验证整页滚动功能流畅，导航点正确工作

### Test 2.1: 鼠标滚轮滚动

**Given**: 用户在首页任意位置  
**When**: 向下滚动鼠标滚轮  
**Then**: 页面平滑滚动到下一个内容区域的顶部

✅ **验证步骤**:
1. 刷新页面，确保在顶部（Hero Section）
2. 向下滚动鼠标滚轮一次
3. 观察滚动行为：
   - [ ] 页面开始平滑滚动（不是瞬间跳转）
   - [ ] 滚动持续时间 600-1000ms
   - [ ] 最终停在 Market Overview 区域顶部
   - [ ] 无滚动过冲或回弹
4. 继续向下滚动：
   - [ ] 每次滚动移动一个完整区域
   - [ ] Hot Stocks → Quick Start → Feature Showcase → Education
5. 向上滚动测试：
   - [ ] 滚动方向正确，回到上一个区域
   - [ ] 滚动行为与向下一致

**Expected Result**:
- 滚动流畅，无卡顿
- 自动对齐到区域边界
- 每次滚动只移动一个区域

**Performance Check** (Chrome DevTools):
1. 打开 Performance 面板
2. 开始录制
3. 滚动 3 次
4. 停止录制
5. 验证：
   - [ ] 帧率保持 60fps (无红色长条)
   - [ ] 无 Long Task (>50ms)
   - [ ] Scripting 时间 <10% 总时间

---

### Test 2.2: 键盘导航

**Given**: 用户在首页  
**When**: 按下键盘方向键或 Page Down  
**Then**: 页面跳转到下一个区域

✅ **验证步骤**:
1. 刷新页面，点击页面任意位置获得焦点
2. 测试键盘快捷键：
   - [ ] **Down Arrow**: 跳转到下一个区域
   - [ ] **Up Arrow**: 跳转到上一个区域
   - [ ] **Page Down**: 跳转到下一个区域
   - [ ] **Page Up**: 跳转到上一个区域
   - [ ] **Home**: 跳转到第一个区域 (Hero)
   - [ ] **End**: 跳转到最后一个区域 (Education)
3. 验证跳转动画：
   - [ ] 使用平滑滚动（不是瞬移）
   - [ ] 动画持续时间与鼠标滚动一致

**Expected Result**:
- 所有键盘快捷键正常工作
- 跳转目标正确
- 无焦点丢失

---

### Test 2.3: 触摸手势 (移动端)

**Given**: 用户在移动设备  
**When**: 快速滑动屏幕  
**Then**: 页面自动对齐到最近的区域边界

✅ **验证步骤**:
1. 使用真实移动设备或 Chrome Device Mode
2. 在 Hero Section 快速向上滑动
3. 观察滚动行为：
   - [ ] 滑动停止后，页面自动对齐到下一个区域
   - [ ] 对齐动画平滑（使用 CSS `scroll-snap`）
   - [ ] 无滚动卡顿或延迟
4. 测试慢速滑动：
   - [ ] 慢速滑动不触发整页跳转
   - [ ] 可以停在区域中间（使用 `scroll-snap-type: y proximity`）
5. 测试快速连续滑动：
   - [ ] 快速滑动 3 次，页面移动 3 个区域
   - [ ] 无跳跃或错误对齐

**Expected Result**:
- 触摸手势响应灵敏
- 对齐行为符合预期
- 移动端性能流畅

---

### Test 2.4: 导航点交互

**Given**: 整页滚动已启用  
**When**: 用户点击侧边导航点  
**Then**: 页面直接跳转到对应区域

✅ **验证步骤**:
1. 刷新页面，检查导航点位置：
   - [ ] 桌面端：右侧固定位置（如 `right: 2rem`）
   - [ ] 移动端：底部固定位置（如 `bottom: 2rem`）
2. 检查导航点样式：
   - [ ] 当前区域的点高亮显示（不同颜色/大小）
   - [ ] 其他点为次要样式
   - [ ] 点击区域足够大（至少 44x44px）
3. 点击导航点：
   - [ ] 点击第 3 个点 → 跳转到 Hot Stocks
   - [ ] 点击第 1 个点 → 跳转回 Hero
   - [ ] 点击当前区域的点 → 无动作或重新对齐
4. 验证点击后高亮更新：
   - [ ] 被点击的点变为激活状态
   - [ ] 之前激活的点恢复次要状态

**Expected Result**:
- 导航点位置合理，不遮挡内容
- 点击响应快速（<100ms）
- 高亮状态实时更新

---

### Test 2.5: 导航点自动高亮

**Given**: 用户正在查看某个区域  
**When**: 页面滚动到该区域  
**Then**: 对应的导航点高亮显示当前位置

✅ **验证步骤**:
1. 使用鼠标滚轮慢速滚动页面
2. 观察导航点高亮变化：
   - [ ] Hero Section 可见 → 第 1 个点高亮
   - [ ] Market Overview 进入视口 → 第 2 个点高亮
   - [ ] Hot Stocks 进入视口 → 第 3 个点高亮
3. 验证切换时机：
   - [ ] 使用 Intersection Observer，50% 可见时切换
   - [ ] 无延迟或闪烁
4. 测试边缘情况：
   - [ ] 快速滚动 → 高亮跳过中间区域，直接到达目标
   - [ ] 滚动到页面底部 → 最后一个点高亮

**Expected Result**:
- 高亮状态与可见区域同步
- 无误报或漏报
- 切换动画平滑（可选）

---

## Scenario 3: 折叠和展开次要内容 (US3-P2)

**目标**: 验证折叠功能正常工作，状态持久化

### Test 3.1: 折叠区域内容

**Given**: 某个内容区域支持折叠  
**When**: 用户点击区域标题旁的折叠图标  
**Then**: 该区域内容收起，只显示标题栏

✅ **验证步骤**:
1. 识别可折叠区域（应显示折叠图标）：
   - [ ] Quick Start Guide (右上角折叠按钮)
   - [ ] Feature Showcase (右上角折叠按钮)
   - [ ] Education Footer (右上角折叠按钮)
2. 点击 "Quick Start Guide" 折叠按钮：
   - [ ] 内容开始折叠动画（高度从 auto → 0）
   - [ ] 动画持续 600ms
   - [ ] 折叠完成后，只显示标题栏
   - [ ] 折叠图标变为展开图标（如 ▼ → ▶）
3. 验证折叠状态：
   - [ ] 区域高度为标题栏高度（如 64px）
   - [ ] 内容完全不可见（`overflow: hidden`）
   - [ ] 区域仍占据布局空间（不是 `display: none`）

**Expected Result**:
- 折叠动画平滑，无跳跃
- 折叠后布局稳定，无其他区域移位
- 图标状态正确切换

---

### Test 3.2: 展开折叠的区域

**Given**: 某个区域已折叠  
**When**: 用户点击展开图标  
**Then**: 区域内容完整显示

✅ **验证步骤**:
1. 继续上一步（Quick Start 已折叠）
2. 点击展开图标：
   - [ ] 内容开始展开动画（高度从 0 → auto）
   - [ ] 动画持续 600ms
   - [ ] 展开完成后，所有内容可见
   - [ ] 展开图标变回折叠图标（▶ → ▼）
3. 验证内容完整性：
   - [ ] 所有步骤卡片显示
   - [ ] 图片/图标加载完成
   - [ ] 无内容截断或溢出

**Expected Result**:
- 展开动画与折叠对称
- 内容完整恢复
- 无重复加载或数据丢失

---

### Test 3.3: 折叠状态持久化

**Given**: 用户折叠了部分区域  
**When**: 刷新页面或重新访问  
**Then**: 折叠状态保持不变

✅ **验证步骤**:
1. 折叠 Education Footer 区域
2. 打开浏览器 DevTools → Application → Local Storage
3. 检查存储数据：
   - [ ] Key: `happystock.layout.preferences`
   - [ ] Value 包含: `"collapsedSections": ["education"]`
4. 刷新页面 (F5)：
   - [ ] Education Footer 保持折叠状态
   - [ ] 其他区域正常显示
5. 展开 Education Footer，再刷新：
   - [ ] Education Footer 显示为展开状态
   - [ ] localStorage 更新为 `"collapsedSections": []`

**Expected Result**:
- 折叠状态正确保存到 localStorage
- 刷新后状态恢复
- 无数据丢失或错误

---

### Test 3.4: 折叠动画与滚动冲突处理

**Given**: 某个区域正在折叠或展开  
**When**: 动画进行中  
**Then**: 整页滚动暂时禁用，避免冲突

✅ **验证步骤**:
1. 点击 Feature Showcase 折叠按钮
2. 在动画进行中（前 600ms）快速滚动鼠标滚轮：
   - [ ] 整页滚动被阻止（页面不跳转到下一个区域）
   - [ ] 折叠动画继续进行，不被中断
3. 等待动画完成（600ms 后）：
   - [ ] 整页滚动恢复正常
   - [ ] 滚动鼠标滚轮可以跳转到下一个区域
4. 检查实现逻辑：
   - [ ] `isAnimating` 状态在 Zustand store 中
   - [ ] `useScrollSnap` Hook 检查 `isAnimating`
   - [ ] 动画期间 `scroll-snap-type` 临时设为 `none`

**Expected Result**:
- 折叠动画不受滚动干扰
- 动画完成后滚动恢复
- 无布局抖动或错位

---

## Scenario 4: 自定义首页区域顺序 (US4-P3)

**目标**: 验证拖拽重排功能 (可选实现)

### Test 4.1: 进入编辑模式

**Given**: 用户点击"自定义布局"按钮  
**When**: 进入编辑模式  
**Then**: 所有区域显示拖拽手柄，可以上下移动

✅ **验证步骤**:
1. 寻找"自定义布局"按钮（可能在页面右上角或设置菜单）
2. 点击按钮：
   - [ ] 页面进入编辑模式（视觉提示，如边框高亮）
   - [ ] 每个区域左侧显示拖拽手柄图标（如 ⋮⋮）
   - [ ] 出现"保存"和"取消"按钮
3. 验证拖拽手柄可交互：
   - [ ] 鼠标悬停显示抓取光标（`cursor: grab`）
   - [ ] 区域不可折叠（折叠按钮禁用）

**Expected Result**:
- 编辑模式视觉清晰
- 拖拽手柄易于识别
- 用户知道如何保存或取消

---

### Test 4.2: 拖拽调整顺序

**Given**: 用户在编辑模式  
**When**: 拖拽某个区域到新位置  
**Then**: 其他区域自动调整顺序

✅ **验证步骤**:
1. 拖拽 Hot Stocks 区域：
   - [ ] 点击并按住拖拽手柄
   - [ ] 区域开始跟随鼠标移动
   - [ ] 其他区域自动为其腾出空间（动画过渡）
2. 将 Hot Stocks 拖到 Hero 上方：
   - [ ] 释放鼠标
   - [ ] Hot Stocks 插入到新位置
   - [ ] 其他区域顺序更新：Hot Stocks → Hero → Market → ...
3. 验证拖拽动画：
   - [ ] 区域移动使用 `transform`（不是 `top/left`）
   - [ ] 动画平滑，帧率 60fps
   - [ ] 无布局抖动

**Expected Result**:
- 拖拽响应灵敏
- 动画流畅自然
- 顺序更新正确

---

### Test 4.3: 保存自定义顺序

**Given**: 用户完成布局调整  
**When**: 点击保存按钮  
**Then**: 新顺序立即生效并持久化保存

✅ **验证步骤**:
1. 点击"保存"按钮：
   - [ ] 编辑模式退出
   - [ ] 拖拽手柄消失
   - [ ] 新顺序保持不变
2. 检查 localStorage：
   - [ ] Key: `happystock.layout.preferences`
   - [ ] Value 包含: `"sectionOrder": ["hot-stocks", "hero", "market-overview", ...]`
3. 刷新页面：
   - [ ] 自定义顺序保持
   - [ ] 所有区域正常显示

**Expected Result**:
- 保存操作即时生效
- 自定义顺序持久化
- 刷新后无丢失

---

### Test 4.4: 恢复默认顺序

**Given**: 用户自定义了布局  
**When**: 点击"恢复默认"按钮  
**Then**: 布局重置为系统默认顺序

✅ **验证步骤**:
1. 在自定义布局后，找到"恢复默认"按钮
2. 点击按钮：
   - [ ] 弹出确认对话框："确定恢复默认布局吗？"
   - [ ] 点击"确定"
3. 验证顺序重置：
   - [ ] 区域顺序恢复为：Hero → Market → Hot Stocks → Quick Start → Feature → Education
   - [ ] localStorage 中 `sectionOrder` 被删除或设为 `undefined`
4. 刷新页面：
   - [ ] 默认顺序保持

**Expected Result**:
- 恢复默认操作正确
- 无遗留自定义配置
- 确认对话框防止误操作

---

## Scenario 5: 响应式设计 (FR-015~017)

**目标**: 验证所有功能在不同设备尺寸下正常工作

### Test 5.1: 桌面端布局

✅ **验证步骤** (≥1024px):
1. 设置浏览器窗口宽度为 1920px
2. 检查布局：
   - [ ] 导航点在右侧固定位置（`right: 2rem`）
   - [ ] 整页滚动使用 `scroll-snap-type: y mandatory`
   - [ ] 区域最小高度为 `100vh`
   - [ ] 内容居中，最大宽度限制（如 `max-w-7xl`）
3. 检查折叠按钮：
   - [ ] 位置：区域右上角
   - [ ] 大小：至少 32x32px
   - [ ] 图标清晰可见

**Expected Result**:
- 桌面端布局美观，空间利用合理
- 交互元素大小适中
- 无横向溢出

---

### Test 5.2: 平板端布局

✅ **验证步骤** (768-1023px):
1. 设置浏览器窗口宽度为 800px
2. 检查布局：
   - [ ] 导航点位置调整（可能移到底部）
   - [ ] 整页滚动仍然工作
   - [ ] 区域宽度适应屏幕
   - [ ] 多列布局变为单列或两列
3. 检查折叠功能：
   - [ ] 折叠按钮足够大（至少 44x44px）
   - [ ] 动画流畅，无卡顿

**Expected Result**:
- 平板端布局合理
- 所有功能正常工作
- 触摸目标足够大

---

### Test 5.3: 移动端布局

✅ **验证步骤** (<768px):
1. 设置浏览器窗口宽度为 375px (iPhone SE)
2. 检查布局：
   - [ ] 导航点在底部固定位置（`bottom: 2rem`）
   - [ ] 整页滚动使用 `scroll-snap-type: y proximity`（更灵活）
   - [ ] 区域高度可以超过一屏（自动调整）
   - [ ] 所有内容单列显示
3. 检查触摸操作：
   - [ ] 导航点足够大（至少 44x44px）
   - [ ] 折叠按钮足够大
   - [ ] 触摸滚动流畅
4. 测试极端窄屏 (280px - Galaxy Fold):
   - [ ] 无横向溢出
   - [ ] 文本无截断
   - [ ] 按钮/图标正常显示

**Expected Result**:
- 移动端布局紧凑但可用
- 触摸目标符合人机工程学
- 极端尺寸下无破坏

---

## Scenario 6: 性能验证 (FR-018~019)

**目标**: 验证性能目标达成

### Test 6.1: 滚动帧率测试

✅ **验证步骤**:
1. 打开 Chrome DevTools → Performance
2. 点击 Record (Ctrl+E)
3. 快速滚动页面 5 次（上下交替）
4. 停止录制 (Ctrl+E)
5. 分析录制结果：
   - [ ] FPS 图表保持绿色（60fps）
   - [ ] 无红色长条（掉帧）
   - [ ] Scripting 时间 <10% 总时间
   - [ ] Rendering 时间 <20% 总时间

**Expected Result**:
- 滚动帧率稳定在 60fps
- 无长时间 JavaScript 执行
- GPU 加速生效（检查 Layers）

---

### Test 6.2: 首屏加载时间

✅ **验证步骤**:
1. 打开 Chrome DevTools → Lighthouse
2. 选择 "Navigation" 模式
3. 运行审计
4. 检查指标：
   - [ ] First Contentful Paint (FCP) <1.5s
   - [ ] Largest Contentful Paint (LCP) <3s
   - [ ] Cumulative Layout Shift (CLS) <0.1
   - [ ] Time to Interactive (TTI) <5s
5. 对比 Feature 003 baseline：
   - [ ] LCP 增长 <10%
   - [ ] Total Blocking Time 增长 <10%

**Expected Result**:
- 首屏加载时间符合目标
- 无明显性能回归
- Lighthouse Performance 分数 >90

---

### Test 6.3: 内存占用

✅ **验证步骤**:
1. 打开 Chrome DevTools → Memory
2. 拍摄 Heap Snapshot（页面初始状态）
3. 滚动页面 10 次，折叠/展开区域 5 次
4. 拍摄第二个 Heap Snapshot
5. 对比两个快照：
   - [ ] 内存增长 <5MB
   - [ ] 无明显内存泄漏（Detached DOM nodes <10）
6. 检查 localStorage 占用：
   ```javascript
   const used = new Blob([localStorage.getItem('happystock.layout.preferences')]).size;
   console.log(`localStorage usage: ${used} bytes`);
   ```
   - [ ] 占用 <1KB

**Expected Result**:
- 内存占用低
- 无内存泄漏
- localStorage 占用极小

---

## Scenario 7: 可访问性 (FR-020~023)

**目标**: 验证 WCAG 2.1 AA 合规性

### Test 7.1: 屏幕阅读器测试

✅ **验证步骤** (使用 NVDA/JAWS/VoiceOver):
1. 启动屏幕阅读器
2. 导航到首页
3. 使用 Tab 键遍历页面：
   - [ ] 每个区域被正确宣布（"核心价值主张区域"）
   - [ ] 导航点被识别为导航元素
   - [ ] 折叠按钮宣布状态（"折叠"或"展开"）
4. 触发整页滚动：
   - [ ] 滚动到新区域时，屏幕阅读器宣布区域标题
   - [ ] 使用 ARIA live region 通知用户

**Expected Result**:
- 所有交互元素可通过键盘访问
- 屏幕阅读器正确宣布内容
- 无焦点陷阱

---

### Test 7.2: ARIA 属性验证

✅ **验证步骤**:
1. 打开 Chrome DevTools → Elements
2. 检查 PageSection 元素：
   - [ ] `role="region"`
   - [ ] `aria-label="[区域标题]"`
3. 检查导航点容器：
   - [ ] `role="navigation"`
   - [ ] `aria-label="页面导航"`
4. 检查每个导航点按钮：
   - [ ] `aria-label="跳转到[区域名称]"`
   - [ ] 当前激活的点：`aria-current="true"`
5. 检查折叠按钮：
   - [ ] `aria-expanded="true"` (展开状态)
   - [ ] `aria-expanded="false"` (折叠状态)
   - [ ] `aria-controls="[内容区域ID]"`

**Expected Result**:
- 所有 ARIA 属性正确设置
- 属性值动态更新
- 语义化 HTML 标签使用正确

---

### Test 7.3: 键盘导航完整性

✅ **验证步骤**:
1. 刷新页面，使用 Tab 键导航：
   - [ ] 焦点顺序逻辑（从上到下，从左到右）
   - [ ] 焦点可见（清晰的焦点环）
   - [ ] 无焦点跳跃或丢失
2. 测试导航点键盘操作：
   - [ ] Tab 键聚焦到导航点
   - [ ] Enter/Space 触发点击
   - [ ] Arrow Up/Down 在导航点间移动焦点
3. 测试折叠按钮键盘操作：
   - [ ] Tab 键聚焦
   - [ ] Enter/Space 触发折叠/展开

**Expected Result**:
- 所有功能可通过键盘完成
- 焦点管理合理
- 无键盘陷阱

---

### Test 7.4: 减少动画偏好支持

✅ **验证步骤**:
1. 打开操作系统设置：
   - Windows: 设置 → 轻松访问 → 显示 → "显示动画" 关闭
   - macOS: 系统偏好设置 → 辅助功能 → 显示 → "减少动画" 启用
2. 刷新页面
3. 测试滚动和折叠：
   - [ ] 整页滚动变为瞬时跳转（无动画）
   - [ ] 折叠/展开瞬时完成（无过渡）
   - [ ] 导航点切换无淡入淡出
4. 检查 CSS 实现：
   ```css
   @media (prefers-reduced-motion: reduce) {
     * {
       animation-duration: 0.01ms !important;
       transition-duration: 0.01ms !important;
     }
   }
   ```

**Expected Result**:
- 动画完全禁用或极短
- 功能仍然正常工作
- 无视觉不适

---

## Scenario 8: 边缘案例处理

**目标**: 验证所有边缘案例正确处理

### Test 8.1: 慢速滚动判断

**Given**: 用户慢速滚动  
**When**: 滚动速度低于阈值  
**Then**: 不触发整页对齐，允许停在区域中间

✅ **验证步骤**:
1. 非常缓慢地滚动鼠标滚轮（每秒 <10px）
2. 在两个区域之间停止滚动
3. 验证行为：
   - [ ] 页面停在中间位置（不自动对齐）
   - [ ] 导航点显示最接近的区域（如 50% 可见度）

**Expected Result**:
- 慢速滚动不强制对齐
- 用户保持控制权

---

### Test 8.2: 小高度区域处理

**Given**: 某个内容区域高度小于视口高度  
**When**: 滚动到该区域  
**Then**: 整页滚动仍然工作

✅ **验证步骤**:
1. 检查 Hot Stocks 区域（可能 <100vh）
2. 滚动到该区域：
   - [ ] 区域顶部对齐到视口顶部
   - [ ] 下一个区域部分可见（填充剩余空间）
   - [ ] 继续滚动移动到下一个区域

**Expected Result**:
- 小高度区域正常对齐
- 无空白区域
- 滚动逻辑一致

---

### Test 8.3: 大高度区域处理 (移动端)

**Given**: 在移动设备，某区域高度 >视口高度  
**When**: 滚动到该区域  
**Then**: 滚动行为智能判断对齐位置

✅ **验证步骤**:
1. 切换到移动端模式（375px 宽度）
2. 假设 Feature Showcase 高度 >667px (iPhone SE 高度)
3. 滚动到该区域：
   - [ ] 首次进入：对齐到区域顶部
   - [ ] 继续向下：在区域内自由滚动（不跳转）
   - [ ] 滚动到区域底部：下一次滚动跳转到下一个区域

**Expected Result**:
- 大高度区域可完整浏览
- 不会跳过内容
- 滚动逻辑智能

---

### Test 8.4: 嵌套滚动冲突

**Given**: Hot Stock List 有内部滚动容器  
**When**: 在列表内滚动  
**Then**: 整页滚动暂停，不影响列表滚动

✅ **验证步骤**:
1. 滚动到 Hot Stock List 区域
2. 鼠标悬停在股票列表上（假设列表有滚动条）
3. 向下滚动鼠标滚轮：
   - [ ] 列表内容滚动（不是整页跳转）
   - [ ] 滚动到列表底部后，继续滚动才触发整页跳转
4. 检查实现：
   - [ ] 列表容器设置 `overscroll-behavior: contain`
   - [ ] 或监听滚动事件，检测是否在边界

**Expected Result**:
- 嵌套滚动正常工作
- 无滚动冲突
- 用户体验自然

---

### Test 8.5: JavaScript 禁用降级

**Given**: 用户禁用了 JavaScript  
**When**: 访问首页  
**Then**: 页面基本可用，可滚动和阅读

✅ **验证步骤**:
1. 打开 Chrome DevTools → Settings → Debugger → Disable JavaScript
2. 刷新页面
3. 验证降级行为：
   - [ ] 页面内容正常显示（SSR 渲染）
   - [ ] 可以使用标准滚动（无 scroll-snap）
   - [ ] 导航点不显示或不可交互
   - [ ] 折叠按钮不显示或禁用
4. 内容可访问性：
   - [ ] 所有文本可阅读
   - [ ] 图片正常加载
   - [ ] 链接可点击

**Expected Result**:
- 核心内容可访问
- 无 JavaScript 错误
- 渐进增强策略生效

---

## Success Criteria Validation

根据 spec.md 的成功标准验证：

| ID | 成功标准 | 验证场景 | 通过标准 |
|----|---------|---------|---------|
| SC-001 | 5秒内识别所有主要功能区域 | Test 1.1 | 用户测试 5 秒计时 |
| SC-002 | 首屏加载时间 ≤110% baseline | Test 6.2 | Lighthouse 对比 |
| SC-003 | 90%+ 滚动完成率 | Test 2.1-2.5 | 所有滚动测试通过 |
| SC-004 | 60fps 滚动性能 | Test 6.1 | Performance 分析 |
| SC-005 | <100ms 触摸响应 | Test 2.3 | 移动端测试 |
| SC-006 | 90% 首次用户理解 | Test 2.4-2.5 | 导航点直观性 |
| SC-007 | 30%+ 折叠功能使用率 | Test 3.1-3.3 | (需生产数据验证) |
| SC-008 | 20% 跳出率降低 | - | (需 Analytics 数据) |
| SC-009 | 最新 2 版本浏览器支持 | Test 5.1-5.3 | 浏览器兼容性测试 |
| SC-010 | WCAG 2.1 AA 合规 | Test 7.1-7.4 | axe DevTools 扫描 |

---

## Automated Testing Commands

### 运行单元测试
```bash
npm test -- --coverage
# 期望覆盖率: >80% for hooks and components
```

### 运行 E2E 测试
```bash
npx playwright test
# 测试文件: tests/e2e/scroll-navigation.spec.ts
#          tests/e2e/collapsible-sections.spec.ts
#          tests/e2e/responsive-layout.spec.ts
```

### 运行 Lighthouse 审计
```bash
npx lighthouse http://localhost:3000 --output html --output-path ./lighthouse-report.html
```

### 运行可访问性扫描
```bash
npm run test:a11y
# 使用 axe-core + jest-axe
```

---

## Troubleshooting (故障排查)

### 问题 1: 整页滚动不工作

**症状**: 滚动鼠标滚轮，页面连续滚动而不对齐

**检查步骤**:
1. 打开 DevTools → Elements
2. 检查容器 CSS：
   - [ ] `scroll-snap-type: y mandatory` (桌面端)
   - [ ] `scroll-snap-type: y proximity` (移动端)
3. 检查区域 CSS：
   - [ ] `scroll-snap-align: start`
4. 检查浏览器兼容性：
   ```javascript
   console.log(CSS.supports('scroll-snap-type', 'y mandatory'));
   // 应返回 true
   ```

**解决方案**:
- 确保 CSS 属性正确应用
- 检查是否有 JavaScript 覆盖了样式
- 尝试禁用 `useScrollSnap` Hook，测试纯 CSS 方案

---

### 问题 2: 折叠动画卡顿

**症状**: 折叠/展开时有明显卡顿或掉帧

**检查步骤**:
1. 打开 Performance 面板，录制折叠操作
2. 检查是否有 Layout Thrashing：
   - [ ] 查找红色三角形警告
   - [ ] 检查是否动画了 `height` 属性（应避免）
3. 检查 CSS：
   ```css
   /* 错误示例（会导致 reflow） */
   .content {
     height: 500px;
     transition: height 0.6s;
   }
   
   /* 正确示例（GPU 加速） */
   .content {
     max-height: 500px;
     overflow: hidden;
     transition: max-height 0.6s, opacity 0.6s;
   }
   ```

**解决方案**:
- 使用 `max-height` 或 `transform: scaleY()` 替代 `height`
- 添加 `will-change: max-height` 提示浏览器优化

---

### 问题 3: localStorage 数据丢失

**症状**: 刷新后折叠状态未恢复

**检查步骤**:
1. 打开 DevTools → Application → Local Storage
2. 检查 `happystock.layout.preferences` 是否存在
3. 检查数据格式是否正确：
   ```json
   {
     "isScrollSnapEnabled": true,
     "collapsedSections": ["education"]
   }
   ```
4. 检查控制台是否有错误：
   - [ ] JSON 解析错误
   - [ ] localStorage quota exceeded

**解决方案**:
- 添加 try-catch 包裹 localStorage 操作
- 数据损坏时回退到默认值
- 定期清理旧数据（如果有版本迁移）

---

## Conclusion

完成以上所有测试场景后，验证清单：

- [ ] 所有 P1 用户故事功能正常 (US1, US2)
- [ ] 所有 P2 用户故事功能正常 (US3)
- [ ] P3 用户故事已实现或标记为未来增强 (US4)
- [ ] 性能指标达标 (60fps, <3s LCP)
- [ ] 可访问性测试通过 (WCAG 2.1 AA)
- [ ] 响应式设计在所有断点工作
- [ ] 边缘案例正确处理
- [ ] 无控制台错误或警告

**最终审批**: 所有测试通过后，特性可进入生产环境。

---

**Version**: 1.0  
**Last Updated**: 2025-10-30  
**Test Coverage**: 8 scenarios, 40+ test cases
