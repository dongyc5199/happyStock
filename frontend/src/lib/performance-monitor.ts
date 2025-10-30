/**
 * Performance Monitor - 性能监控工具
 * 
 * 用于监控滚动性能和动画帧率
 * 
 * 对应需求: US2 (FR-018)
 */

/**
 * 帧率监控器
 */
export class FPSMonitor {
  private frames: number[] = [];
  private lastTime = performance.now();
  private isRunning = false;

  /**
   * 开始监控
   */
  start() {
    this.isRunning = true;
    this.measure();
  }

  /**
   * 停止监控
   */
  stop() {
    this.isRunning = false;
  }

  /**
   * 测量帧率
   */
  private measure() {
    if (!this.isRunning) return;

    const now = performance.now();
    const delta = now - this.lastTime;
    this.lastTime = now;

    // 计算 FPS
    const fps = 1000 / delta;
    this.frames.push(fps);

    // 保留最近 60 帧的数据
    if (this.frames.length > 60) {
      this.frames.shift();
    }

    requestAnimationFrame(() => this.measure());
  }

  /**
   * 获取平均帧率
   */
  getAverageFPS(): number {
    if (this.frames.length === 0) return 0;
    const sum = this.frames.reduce((a, b) => a + b, 0);
    return Math.round(sum / this.frames.length);
  }

  /**
   * 获取最小帧率
   */
  getMinFPS(): number {
    if (this.frames.length === 0) return 0;
    return Math.round(Math.min(...this.frames));
  }

  /**
   * 重置数据
   */
  reset() {
    this.frames = [];
    this.lastTime = performance.now();
  }
}

/**
 * 滚动性能监控
 */
export class ScrollPerformanceMonitor {
  private scrollTimes: number[] = [];
  private startTime = 0;

  /**
   * 开始记录滚动
   */
  startScroll() {
    this.startTime = performance.now();
  }

  /**
   * 结束记录滚动
   */
  endScroll() {
    if (this.startTime === 0) return;

    const duration = performance.now() - this.startTime;
    this.scrollTimes.push(duration);

    // 保留最近 20 次滚动的数据
    if (this.scrollTimes.length > 20) {
      this.scrollTimes.shift();
    }

    this.startTime = 0;
  }

  /**
   * 获取平均滚动时间
   */
  getAverageScrollTime(): number {
    if (this.scrollTimes.length === 0) return 0;
    const sum = this.scrollTimes.reduce((a, b) => a + b, 0);
    return Math.round(sum / this.scrollTimes.length);
  }

  /**
   * 获取性能报告
   */
  getReport(): {
    averageTime: number;
    minTime: number;
    maxTime: number;
    count: number;
  } {
    if (this.scrollTimes.length === 0) {
      return { averageTime: 0, minTime: 0, maxTime: 0, count: 0 };
    }

    return {
      averageTime: this.getAverageScrollTime(),
      minTime: Math.round(Math.min(...this.scrollTimes)),
      maxTime: Math.round(Math.max(...this.scrollTimes)),
      count: this.scrollTimes.length,
    };
  }

  /**
   * 重置数据
   */
  reset() {
    this.scrollTimes = [];
    this.startTime = 0;
  }
}

/**
 * 全局性能监控实例
 */
let fpsMonitor: FPSMonitor | null = null;
let scrollMonitor: ScrollPerformanceMonitor | null = null;

/**
 * 启用性能监控 (仅开发环境)
 */
export function enablePerformanceMonitoring() {
  if (process.env.NODE_ENV !== 'development') return;

  if (!fpsMonitor) {
    fpsMonitor = new FPSMonitor();
    fpsMonitor.start();
  }

  if (!scrollMonitor) {
    scrollMonitor = new ScrollPerformanceMonitor();
  }

  // 在控制台输出性能报告
  setInterval(() => {
    if (fpsMonitor) {
      const avgFPS = fpsMonitor.getAverageFPS();
      const minFPS = fpsMonitor.getMinFPS();
      
      console.log('[Performance] FPS:', {
        average: avgFPS,
        min: minFPS,
        status: avgFPS >= 60 ? '✅ 优秀' : avgFPS >= 30 ? '⚠️ 一般' : '❌ 差',
      });
    }

    if (scrollMonitor) {
      const report = scrollMonitor.getReport();
      if (report.count > 0) {
        console.log('[Performance] Scroll:', report);
      }
    }
  }, 5000); // 每 5 秒输出一次
}

/**
 * 记录滚动开始
 */
export function recordScrollStart() {
  if (scrollMonitor) {
    scrollMonitor.startScroll();
  }
}

/**
 * 记录滚动结束
 */
export function recordScrollEnd() {
  if (scrollMonitor) {
    scrollMonitor.endScroll();
  }
}

/**
 * 禁用性能监控
 */
export function disablePerformanceMonitoring() {
  if (fpsMonitor) {
    fpsMonitor.stop();
    fpsMonitor = null;
  }
  scrollMonitor = null;
}
