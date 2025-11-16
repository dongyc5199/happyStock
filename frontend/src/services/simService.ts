import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export type OrderSide = 'BUY' | 'SELL';
export type OrderType = 'MARKET' | 'LIMIT';

export interface TickOrder {
  order_id: string;
  participant_id: string;
  participant_code?: string;
  participant_type?: 'player' | 'agent';
  side: OrderSide;
  type: OrderType;
  quantity: number;
  price?: number | null;
}

export interface TickRequestPayload {
  session_id: number;
  session_code: string;
  tick: number;
  timestamp?: string;
  orders: TickOrder[];
}

export interface TickResponse {
  status: string;
  trace_id: string;
  orders: string[];
  trades: Array<{
    buy_order: string;
    sell_order: string;
    price: number;
    quantity: number;
  }>;
  snapshot: Record<string, unknown>;
}

export async function sendTickRequest(
  payload: TickRequestPayload
): Promise<TickResponse> {
  const response = await axios.post<TickResponse>(
    `${API_BASE_URL}/api/sim/tick`,
    payload
  );
  return response.data;
}
