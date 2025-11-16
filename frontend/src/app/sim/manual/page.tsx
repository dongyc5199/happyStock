'use client';

import ManualTickForm from '@/components/sim/ManualTickForm';

export default function ManualOrderPage() {
  return (
    <div className="mx-auto max-w-4xl space-y-4 px-4 py-8">
      <h1 className="text-2xl font-semibold">仿真下单实验室</h1>
      <p className="text-sm text-gray-600">
        用于手动构造 `/api/sim/tick` 请求，方便在浏览器中直接提交订单并观察
        撮合结果。
      </p>
      <ManualTickForm />
    </div>
  );
}
