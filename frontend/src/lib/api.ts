const API_BASE = import.meta.env.PUBLIC_API_URL ?? 'http://127.0.0.1:8000/api';

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = typeof localStorage !== 'undefined' ? localStorage.getItem('token') : null;
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Token ${token}` } : {}),
      ...options.headers,
    },
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({}));
    throw Object.assign(new Error('API error'), { status: res.status, data: error });
  }
  return res.json();
}

export const api = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body: unknown) =>
    request<T>(path, { method: 'POST', body: JSON.stringify(body) }),
};

// Types matching the Django API responses

export interface Equipment {
  id: number;
  name: string;
}

export interface Room {
  id: number;
  name: string;
  slug: string;
  description: string;
  size_sqm: number | null;
  hourly_rate: string;
  equipment: Equipment[];
  image: string | null;
}

export interface Slot {
  start_time: string;
  max_hours: number;
}

export interface AvailableRoom {
  room_id: number;
  name: string;
  slug: string;
  hourly_rate: string;
  slots: Slot[];
}

export interface AvailabilityResponse {
  is_open: boolean;
  date: string;
  open_time?: string;
  close_time?: string;
  min_booking_hours?: number;
  rooms: AvailableRoom[];
}

export interface StudioSettings {
  min_notice_days: number;
  allow_pay_on_day: boolean;
  min_booking_hours: number;
  min_cancellation_notice_days: number;
}

export interface Booking {
  id: number;
  room: { id: number; name: string; slug: string };
  start_datetime: string;
  end_datetime: string;
  payment_method: 'UPFRONT' | 'ON_DAY';
  payment_status: 'PENDING' | 'PAID' | 'REFUNDED';
  is_cancelled: boolean;
  created_at: string;
  total_cost: string;
  client_secret?: string;
}
